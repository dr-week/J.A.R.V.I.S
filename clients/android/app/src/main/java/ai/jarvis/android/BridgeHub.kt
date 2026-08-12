package ai.jarvis.android

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import org.json.JSONObject

/** Shared bridge → UI bus (process-local). */
data class ConfirmPending(
    val requestId: String,
    val tool: String,
    val paramsJson: String,
    val sessionId: String = "",
)

object BridgeHub {
    private val _status = MutableStateFlow("bridge: idle")
    val status: StateFlow<String> = _status.asStateFlow()

    private val _pending = MutableStateFlow<ConfirmPending?>(null)
    val pending: StateFlow<ConfirmPending?> = _pending.asStateFlow()

    fun setStatus(text: String) {
        _status.value = text
    }

    fun setPending(pending: ConfirmPending?) {
        _pending.value = pending
    }

    fun clearPending() {
        _pending.value = null
    }

    fun pendingFromConfirmMessage(msg: JSONObject): ConfirmPending {
        val params = msg.optJSONObject("params") ?: JSONObject()
        return ConfirmPending(
            requestId = msg.optString("request_id"),
            tool = msg.optString("tool"),
            paramsJson = params.toString(),
            sessionId = msg.optString("session_id"),
        )
    }
}
