package ai.jarvis.android

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import org.json.JSONObject
import java.util.concurrent.TimeUnit

/**
 * Device bridge — `/ws` register + tool_execute + confirm_request.
 * Protocol: docs/SYNC_PROTOCOL.md
 */
class DeviceBridge(
    private val context: Context,
    private val brainUrl: String,
    private val deviceId: String,
    private val token: String = "",
) {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val client = OkHttpClient.Builder()
        .pingInterval(20, TimeUnit.SECONDS)
        .build()

    private var ws: WebSocket? = null
    private var running = false

    fun start() {
        if (running) return
        running = true
        connect()
    }

    fun stop() {
        running = false
        ws?.close(1000, "client shutdown")
        ws = null
        scope.cancel()
    }

    private fun connect() {
        if (!running) return
        var wsUrl = brainUrl
            .replace("http://", "ws://")
            .replace("https://", "wss://")
            .trimEnd('/') + "/ws"
        if (token.isNotBlank()) {
            wsUrl += "?token=" + java.net.URLEncoder.encode(token, "UTF-8")
        }
        val req = Request.Builder().url(wsUrl).build()
        BridgeHub.setStatus("bridge: connecting…")
        ws = client.newWebSocket(req, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                if (!running) return
                val register = JSONObject()
                    .put("type", "register")
                    .put("device_id", deviceId)
                if (token.isNotBlank()) {
                    register.put("token", token)
                }
                webSocket.send(register.toString())
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                handleMessage(webSocket, text)
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                Log.w(TAG, "bridge ws failure: ${t.message}")
                BridgeHub.setStatus("bridge: disconnected (${t.message})")
                scheduleReconnect()
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                BridgeHub.setStatus("bridge: closed")
                scheduleReconnect()
            }
        })
    }

    private fun scheduleReconnect() {
        if (!running) return
        scope.launch {
            kotlinx.coroutines.delay(RECONNECT_MS)
            connect()
        }
    }

    private fun handleMessage(webSocket: WebSocket, text: String) {
        val msg = try {
            JSONObject(text)
        } catch (_: Exception) {
            return
        }

        when (msg.optString("type")) {
            "registered" -> {
                BridgeHub.setStatus("bridge: connected (${msg.optString("device_id")})")
            }
            "ping" -> webSocket.send(JSONObject().put("type", "pong").toString())
            "tool_execute" -> handleToolExecute(webSocket, msg)
            "confirm_request" -> {
                BridgeHub.setPending(BridgeHub.pendingFromConfirmMessage(msg))
                BridgeHub.setStatus("bridge: confirm needed — ${msg.optString("tool")}")
            }
            "push_memory", "push_habit", "velocity_update" -> {
                // Glance-only; Field UI can ignore for now
            }
        }
    }

    private fun handleToolExecute(webSocket: WebSocket, msg: JSONObject) {
        val requestId = msg.optString("request_id")
        val sessionId = msg.optString("session_id")
        val tool = msg.optString("tool")
        val params = msg.optJSONObject("params") ?: JSONObject()

        scope.launch {
            val result = if (tool == "android_open") {
                withContext(Dispatchers.Main) {
                    launchIntent(params.optString("target"))
                }
            } else {
                JSONObject().put("ok", false).put("error", "unsupported device tool: $tool")
            }

            val status = if (result.optBoolean("ok")) "ok" else "error"
            val reply = JSONObject()
                .put("type", "tool_result")
                .put("request_id", requestId)
                .put("session_id", sessionId)
                .put("tool", tool)
                .put("status", status)
                .put("result", result)
            webSocket.send(reply.toString())
            BridgeHub.setStatus("bridge: ran $tool ($status)")
        }
    }

    private fun launchIntent(target: String): JSONObject {
        val t = target.trim()
        if (t.isEmpty()) {
            return JSONObject().put("ok", false).put("error", "empty target")
        }
        return try {
            if (t.startsWith("http://") || t.startsWith("https://") || t.startsWith("market://")) {
                val intent = Intent(Intent.ACTION_VIEW, Uri.parse(t))
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                context.startActivity(intent)
                JSONObject().put("ok", true).put("kind", "url").put("target", t)
                    .put("result", "opened: $t")
            } else {
                val launch = context.packageManager.getLaunchIntentForPackage(t)
                if (launch == null) {
                    JSONObject().put("ok", false).put("kind", "app").put("target", t)
                        .put("error", "no launch intent for package: $t")
                } else {
                    launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                    context.startActivity(launch)
                    JSONObject().put("ok", true).put("kind", "app").put("target", t)
                        .put("result", "launched package: $t")
                }
            }
        } catch (e: Exception) {
            JSONObject().put("ok", false).put("kind", "intent").put("target", t)
                .put("error", e.message ?: "failed to launch")
        }
    }

    companion object {
        private const val TAG = "JarvisBridge"
        private const val RECONNECT_MS = 3000L
    }
}
