import queue
import sys

import numpy as np
import sounddevice as sd

# Import the CEO loop
from backend.app.company.ceo import ceo_app
from faster_whisper import WhisperModel
from openwakeword.model import Model


class HearingCortex:
    def __init__(self, wakewords=["jarvis", "friday"]):
        print("[Hearing] Initializing openWakeWord...")
        try:
            # Initialize openwakeword model
            self.oww_model = Model(wakeword_models=wakewords, inference_framework="onnx")
        except Exception as e:
            print(f"[Hearing] Failed to load requested wakewords, using default. Error: {e}")
            self.oww_model = Model(inference_framework="onnx")
            
        print("[Hearing] Initializing faster-whisper...")
        # Initialize whisper model for STT
        self.whisper_model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
        
        self.audio_queue = queue.Queue()
        self.chunk_size = 1280
        self.sample_rate = 16000

    def _audio_callback(self, indata, frames, time_info, status):
        """This is called for each audio block by sounddevice."""
        if status:
            print(status, file=sys.stderr)
        # indata is shape (frames, channels), float32 by default
        # openwakeword expects 1D array of int16
        audio_data = (indata[:, 0] * 32767).astype(np.int16)
        self.audio_queue.put(audio_data)

    def listen_loop(self):
        print("[Hearing] Listening for wake words...")
        recording = False
        voice_buffer = []
        silence_counter = 0
        
        # Open audio stream
        with sd.InputStream(
            samplerate=self.sample_rate, 
            channels=1, 
            blocksize=self.chunk_size, 
            callback=self._audio_callback
        ):
            try:
                while True:
                    chunk = self.audio_queue.get()
                    
                    if not recording:
                        # Feed the audio chunk to openwakeword
                        prediction = self.oww_model.predict(chunk)
                        
                        for mdl in self.oww_model.prediction_buffer.keys():
                            # Trigger on > 0.5 confidence
                            if prediction[mdl] > 0.5:
                                print(f"\n[Hearing] Wake word '{mdl}' detected!")
                                recording = True
                                voice_buffer = []
                                silence_counter = 0
                                break
                    else:
                        # We are recording a voice command
                        voice_buffer.append(chunk)
                        
                        # Calculate RMS for silence detection
                        rms = np.sqrt(np.mean(chunk.astype(np.float32)**2))
                        if rms < 500: # Heuristic for silence
                            silence_counter += 1
                        else:
                            silence_counter = 0
                            
                        # ~2 seconds of silence (2 * 16000 / 1280 = 25 chunks) stops recording
                        if silence_counter > 25:
                            print("[Hearing] Finished recording command.")
                            self._process_command(voice_buffer)
                            recording = False
            except KeyboardInterrupt:
                print("[Hearing] Stopping...")

    def _process_command(self, voice_buffer):
        print("[Hearing] Transcribing command...")
        # Concatenate and normalize for Whisper (float32 between -1 and 1)
        audio_data = np.concatenate(voice_buffer).astype(np.float32) / 32768.0
        
        # Transcribe audio to text
        segments, info = self.whisper_model.transcribe(audio_data, beam_size=5)
        text = "".join(segment.text for segment in segments).strip()
        print(f"[Hearing] STT Output: '{text}'")
        
        if text:
            print("[Hearing] Forwarding to CEO loop...")
            # Forward the text to the CEO loop
            response = ceo_app.invoke({"market_signal": text})
            print(f"[Hearing] CEO Decision: {response.get('decision', 'None')}")

if __name__ == "__main__":
    cortex = HearingCortex(wakewords=["jarvis", "friday"])
    cortex.listen_loop()
