package ai.jarvis.android

import android.content.SharedPreferences
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.util.UUID
import java.util.concurrent.TimeUnit

data class ChatMessage(
    val id: String = UUID.randomUUID().toString(),
    val role: String,
    val text: String,
)

data class ChatUiState(
    val brainUrl: String = "http://10.0.2.2:8787",
    val draft: String = "",
    val messages: List<ChatMessage> = emptyList(),
    val busy: Boolean = false,
    val status: String = "Set brain URL (LAN IP of your PC). Emulator: 10.0.2.2:8787",
)

class ChatViewModel(
    private val prefs: SharedPreferences,
) : ViewModel() {

    private val client = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(120, TimeUnit.SECONDS)
        .build()

    private val _state = MutableStateFlow(
        ChatUiState(brainUrl = prefs.getString(KEY_BRAIN, DEFAULT_BRAIN) ?: DEFAULT_BRAIN)
    )
    val state: StateFlow<ChatUiState> = _state.asStateFlow()

    private val sessionId = UUID.randomUUID().toString()
    private val deviceId = "android-" + (prefs.getString(KEY_DEVICE, null) ?: run {
        val id = UUID.randomUUID().toString().take(8)
        prefs.edit().putString(KEY_DEVICE, id).apply()
        id
    })

    fun onBrainUrlChange(url: String) {
        _state.update { it.copy(brainUrl = url) }
        prefs.edit().putString(KEY_BRAIN, url.trim()).apply()
    }

    fun onDraftChange(text: String) {
        _state.update { it.copy(draft = text) }
    }

    fun send() {
        val text = _state.value.draft.trim()
        if (text.isEmpty() || _state.value.busy) return

        val brain = _state.value.brainUrl.trim().trimEnd('/')
        _state.update {
            it.copy(
                draft = "",
                busy = true,
                status = "Sending…",
                messages = it.messages + ChatMessage(role = "user", text = text) +
                    ChatMessage(role = "assistant", text = ""),
            )
        }

        viewModelScope.launch {
            try {
                val reply = withContext(Dispatchers.IO) {
                    streamChat(brain, text) { partial ->
                        viewModelScope.launch(Dispatchers.Main.immediate) {
                            _state.update { st ->
                                val msgs = st.messages.toMutableList()
                                if (msgs.isNotEmpty() && msgs.last().role == "assistant") {
                                    msgs[msgs.lastIndex] = msgs.last().copy(text = partial)
                                }
                                st.copy(messages = msgs)
                            }
                        }
                    }
                }
                _state.update { st ->
                    val msgs = st.messages.toMutableList()
                    if (msgs.isNotEmpty() && msgs.last().role == "assistant") {
                        msgs[msgs.lastIndex] = msgs.last().copy(text = reply.ifBlank { "(empty reply)" })
                    }
                    st.copy(busy = false, status = "OK · $brain", messages = msgs)
                }
            } catch (e: Exception) {
                _state.update { st ->
                    val msgs = st.messages.toMutableList()
                    if (msgs.isNotEmpty() && msgs.last().role == "assistant") {
                        msgs[msgs.lastIndex] = msgs.last().copy(text = "Error: ${e.message}")
                    }
                    st.copy(busy = false, status = "Error: ${e.message}", messages = msgs)
                }
            }
        }
    }

    private fun streamChat(brain: String, text: String, onPartial: (String) -> Unit): String {
        val bodyJson = JSONObject()
            .put("text", text)
            .put("session_id", sessionId)
            .put("device_id", deviceId)
            .put("client_msg_id", UUID.randomUUID().toString())
            .toString()

        val request = Request.Builder()
            .url("$brain/chat")
            .post(bodyJson.toRequestBody(JSON))
            .header("Accept", "text/event-stream")
            .build()

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw IllegalStateException("HTTP ${response.code}")
            }
            val source = response.body?.source() ?: throw IllegalStateException("Empty body")
            val sb = StringBuilder()
            while (!source.exhausted()) {
                val line = source.readUtf8Line() ?: break
                if (!line.startsWith("data: ")) continue
                val chunk = line.removePrefix("data: ")
                if (chunk == "[DONE]") break
                if (chunk.startsWith("[ERROR]")) {
                    throw IllegalStateException(chunk)
                }
                sb.append(chunk)
                onPartial(sb.toString())
            }
            return sb.toString()
        }
    }

    companion object {
        private const val KEY_BRAIN = "brain_url"
        private const val KEY_DEVICE = "device_id"
        private const val DEFAULT_BRAIN = "http://10.0.2.2:8787"
        private val JSON = "application/json; charset=utf-8".toMediaType()

        fun factory(prefs: SharedPreferences): ViewModelProvider.Factory =
            object : ViewModelProvider.Factory {
                @Suppress("UNCHECKED_CAST")
                override fun <T : ViewModel> create(modelClass: Class<T>): T {
                    return ChatViewModel(prefs) as T
                }
            }
    }
}
