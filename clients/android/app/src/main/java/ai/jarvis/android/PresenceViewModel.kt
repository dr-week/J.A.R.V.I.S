package ai.jarvis.android

import android.app.Application
import android.content.Intent
import android.content.SharedPreferences
import android.net.Uri
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.stateIn
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

data class PresenceUiState(
    val brainUrl: String = BridgeService.DEFAULT_BRAIN,
    val pairingSecret: String = "change-me",
    val webAssistantUrl: String = "http://10.0.2.2:5173",
    val deviceId: String = "",
    val paired: Boolean = false,
    val healthLine: String = "Tap Health to ping brain",
    val statusLine: String = "Presence — pair, then open web for chat",
    val busy: Boolean = false,
    val smokeDraft: String = "",
    val smokeReply: String = "",
)

/**
 * Field-style Presence state (not a chat product).
 * Chat lives in clients/web; this app = pair + bridge + confirm + open web.
 */
class PresenceViewModel(
    app: Application,
    private val prefs: SharedPreferences,
) : AndroidViewModel(app) {

    private val client = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .build()

    private val deviceId = "android-" + (prefs.getString(BridgeService.KEY_DEVICE, null) ?: run {
        val id = UUID.randomUUID().toString().take(8)
        prefs.edit().putString(BridgeService.KEY_DEVICE, id).apply()
        id
    })

    private val sessionId = prefs.getString(KEY_SESSION, null) ?: run {
        val id = UUID.randomUUID().toString()
        prefs.edit().putString(KEY_SESSION, id).apply()
        id
    }

    private val _state = MutableStateFlow(
        PresenceUiState(
            brainUrl = prefs.getString(BridgeService.KEY_BRAIN, BridgeService.DEFAULT_BRAIN)
                ?: BridgeService.DEFAULT_BRAIN,
            pairingSecret = prefs.getString(KEY_SECRET, "change-me") ?: "change-me",
            webAssistantUrl = prefs.getString(KEY_WEB, "http://10.0.2.2:5173")
                ?: "http://10.0.2.2:5173",
            deviceId = deviceId,
            paired = !prefs.getString(BridgeService.KEY_TOKEN, "").isNullOrBlank(),
        )
    )
    val state: StateFlow<PresenceUiState> = _state.asStateFlow()

    val bridgeStatus: StateFlow<String> = BridgeHub.status
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), "bridge: idle")

    val pending: StateFlow<ConfirmPending?> = BridgeHub.pending
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), null)

    fun onBrainUrlChange(url: String) {
        _state.update { it.copy(brainUrl = url) }
        prefs.edit().putString(BridgeService.KEY_BRAIN, url.trim()).apply()
    }

    fun onSecretChange(secret: String) {
        _state.update { it.copy(pairingSecret = secret) }
        prefs.edit().putString(KEY_SECRET, secret).apply()
    }

    fun onWebUrlChange(url: String) {
        _state.update { it.copy(webAssistantUrl = url) }
        prefs.edit().putString(KEY_WEB, url.trim()).apply()
    }

    fun onSmokeDraftChange(text: String) {
        _state.update { it.copy(smokeDraft = text) }
    }

    fun checkHealth() {
        viewModelScope.launch {
            _state.update { it.copy(busy = true, healthLine = "Checking…") }
            try {
                val brain = brainBase()
                val body = withContext(Dispatchers.IO) {
                    val req = Request.Builder().url("$brain/health").get().build()
                    client.newCall(req).execute().use { resp ->
                        if (!resp.isSuccessful) throw IllegalStateException("HTTP ${resp.code}")
                        resp.body?.string().orEmpty()
                    }
                }
                val json = JSONObject(body)
                val llm = json.optBoolean("llm_ready", json.optBoolean("ok", false))
                _state.update {
                    it.copy(
                        busy = false,
                        healthLine = "OK · LLM ${if (llm) "on" else "off"} · $brain",
                        statusLine = "Brain reachable",
                    )
                }
            } catch (e: Exception) {
                _state.update {
                    it.copy(busy = false, healthLine = "Offline: ${e.message}", statusLine = "Brain unreachable")
                }
            }
        }
    }

    fun pair() {
        viewModelScope.launch {
            _state.update { it.copy(busy = true, statusLine = "Pairing…") }
            try {
                val brain = brainBase()
                val secret = _state.value.pairingSecret
                val token = withContext(Dispatchers.IO) {
                    val payload = JSONObject()
                        .put("pairing_secret", secret)
                        .put("device_id", deviceId)
                        .put("device_name", "android")
                        .toString()
                    val req = Request.Builder()
                        .url("$brain/pair")
                        .post(payload.toRequestBody(JSON))
                        .build()
                    client.newCall(req).execute().use { resp ->
                        val raw = resp.body?.string().orEmpty()
                        if (!resp.isSuccessful) {
                            throw IllegalStateException("HTTP ${resp.code}: $raw")
                        }
                        JSONObject(raw).getString("token")
                    }
                }
                prefs.edit().putString(BridgeService.KEY_TOKEN, token).apply()
                _state.update {
                    it.copy(busy = false, paired = true, statusLine = "Paired · restarting bridge")
                }
                restartBridge()
            } catch (e: Exception) {
                _state.update {
                    it.copy(busy = false, paired = false, statusLine = "Pair failed: ${e.message}")
                }
            }
        }
    }

    fun restartBridge() {
        val ctx = getApplication<Application>()
        ctx.startService(
            Intent(ctx, BridgeService::class.java).setAction(BridgeService.ACTION_RESTART)
        )
    }

    fun openFullAssistant() {
        val url = _state.value.webAssistantUrl.trim()
        if (url.isEmpty()) return
        val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url)).apply {
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }
        getApplication<Application>().startActivity(intent)
    }

    fun approveConfirm() {
        val p = BridgeHub.pending.value ?: return
        BridgeHub.clearPending()
        sendConfirmPhrase("confirm", p.sessionId.ifBlank { sessionId })
    }

    fun denyConfirm() {
        val p = BridgeHub.pending.value ?: return
        BridgeHub.clearPending()
        sendConfirmPhrase("deny", p.sessionId.ifBlank { sessionId })
    }

    private fun sendConfirmPhrase(text: String, sid: String) {
        viewModelScope.launch {
            _state.update { it.copy(busy = true, statusLine = "Sending $text…") }
            try {
                withContext(Dispatchers.IO) { postChat(brainBase(), text, sid) }
                _state.update { it.copy(busy = false, statusLine = "Sent: $text") }
            } catch (e: Exception) {
                _state.update { it.copy(busy = false, statusLine = "Confirm error: ${e.message}") }
            }
        }
    }

    /** Optional LAN smoke — not the product chat UI. */
    fun smokeSend() {
        val text = _state.value.smokeDraft.trim()
        if (text.isEmpty() || _state.value.busy) return
        viewModelScope.launch {
            _state.update { it.copy(busy = true, smokeDraft = "", smokeReply = "…", statusLine = "Smoke chat…") }
            try {
                val reply = withContext(Dispatchers.IO) { postChat(brainBase(), text, sessionId) }
                _state.update {
                    it.copy(busy = false, smokeReply = reply.ifBlank { "(empty)" }, statusLine = "Smoke OK")
                }
            } catch (e: Exception) {
                _state.update {
                    it.copy(busy = false, smokeReply = "Error: ${e.message}", statusLine = "Smoke failed")
                }
            }
        }
    }

    private fun brainBase(): String = _state.value.brainUrl.trim().trimEnd('/')

    private fun postChat(brain: String, text: String, sid: String): String {
        val bodyJson = JSONObject()
            .put("text", text)
            .put("session_id", sid)
            .put("device_id", deviceId)
            .put("client_msg_id", UUID.randomUUID().toString())
            .toString()
        val request = Request.Builder()
            .url("$brain/chat")
            .post(bodyJson.toRequestBody(JSON))
            .header("Accept", "text/event-stream")
            .build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw IllegalStateException("HTTP ${response.code}")
            val source = response.body?.source() ?: throw IllegalStateException("Empty body")
            val sb = StringBuilder()
            while (!source.exhausted()) {
                val line = source.readUtf8Line() ?: break
                if (!line.startsWith("data: ")) continue
                val chunk = line.removePrefix("data: ")
                if (chunk == "[DONE]") break
                if (chunk.startsWith("[ERROR]")) throw IllegalStateException(chunk)
                sb.append(chunk)
            }
            return sb.toString()
        }
    }

    companion object {
        private const val KEY_SECRET = "pairing_secret"
        private const val KEY_WEB = "web_assistant_url"
        private const val KEY_SESSION = "presence_session_id"
        private val JSON = "application/json; charset=utf-8".toMediaType()

        fun factory(app: Application, prefs: SharedPreferences): ViewModelProvider.Factory =
            object : ViewModelProvider.Factory {
                @Suppress("UNCHECKED_CAST")
                override fun <T : ViewModel> create(modelClass: Class<T>): T {
                    return PresenceViewModel(app, prefs) as T
                }
            }
    }
}
