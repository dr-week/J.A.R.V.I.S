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
 * Device bridge for Jarvis (ISSUE-033).
 *
 * Connects to the brain's `/ws` endpoint, registers a `device_id`, and listens
 * for `tool_execute` requests. When the brain asks for `android_open`, it
 * builds an Android [Intent] (ACTION_VIEW) for a URL, a market link, or an app
 * package and launches it. The result is sent back as `tool_result`.
 *
 * Protocol: see docs/SYNC_PROTOCOL.md (register / registered / tool_execute /
 * tool_result).
 */
class DeviceBridge(
    private val context: Context,
    private val brainUrl: String,
    private val deviceId: String,
) {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val client = OkHttpClient.Builder()
        .pingInterval(20, TimeUnit.SECONDS)
        .build()

    private var ws: WebSocket? = null
    private var running = false

    interface Listener {
        fun onBridgeStatus(text: String)
    }

    var listener: Listener? = null

    fun start() {
        if (running) return
        running = true
        launch()
    }

    fun stop() {
        running = false
        ws?.close(1000, "client shutdown")
        ws = null
        scope.cancel()
    }

    private fun launch() {
        if (!running) return
        val wsUrl = brainUrl
            .replace("http://", "ws://")
            .replace("https://", "wss://")
            .trimEnd('/') + "/ws"
        val req = Request.Builder().url(wsUrl).build()
        ws = client.newWebSocket(req, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                if (!running) return
                val register = JSONObject()
                    .put("type", "register")
                    .put("device_id", deviceId)
                webSocket.send(register.toString())
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                handleMessage(webSocket, text)
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                Log.w(TAG, "bridge ws failure: ${t.message}")
                listener?.onBridgeStatus("bridge: disconnected (${t.message})")
                scheduleReconnect()
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                Log.i(TAG, "bridge ws closed: $code $reason")
                listener?.onBridgeStatus("bridge: closed")
                scheduleReconnect()
            }
        })
    }

    private fun scheduleReconnect() {
        if (!running) return
        scope.launch {
            kotlinx.coroutines.delay(RECONNECT_MS)
            launch()
        }
    }

    private fun handleMessage(webSocket: WebSocket, text: String) {
        val msg = try {
            JSONObject(text)
        } catch (e: Exception) {
            Log.w(TAG, "bad json from brain: $text")
            return
        }

        when (msg.optString("type")) {
            "registered" -> {
                listener?.onBridgeStatus("bridge: connected (${msg.optString("device_id")})")
            }
            "ping" -> webSocket.send(JSONObject().put("type", "pong").toString())
            "tool_execute" -> handleToolExecute(webSocket, msg)
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
        }
    }

    /**
     * Build and launch an [Intent] for the given target.
     * - https:// / http:// → ACTION_VIEW Uri
     * - market:// → ACTION_VIEW (Play Store)
     * - otherwise treated as an app package name → packageManager launch intent
     */
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
                JSONObject()
                    .put("ok", true)
                    .put("kind", "url")
                    .put("target", t)
                    .put("result", "opened: $t")
            } else {
                // Treat as app package name.
                val launch = context.packageManager.getLaunchIntentForPackage(t)
                if (launch == null) {
                    JSONObject()
                        .put("ok", false)
                        .put("kind", "app")
                        .put("target", t)
                        .put("error", "no launch intent for package: $t")
                } else {
                    launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                    context.startActivity(launch)
                    JSONObject()
                        .put("ok", true)
                        .put("kind", "app")
                        .put("target", t)
                        .put("result", "launched package: $t")
                }
            }
        } catch (e: Exception) {
            JSONObject()
                .put("ok", false)
                .put("kind", "intent")
                .put("target", t)
                .put("error", e.message ?: "failed to launch")
        }
    }

    companion object {
        private const val TAG = "JarvisBridge"
        private const val RECONNECT_MS = 3000L
    }
}
