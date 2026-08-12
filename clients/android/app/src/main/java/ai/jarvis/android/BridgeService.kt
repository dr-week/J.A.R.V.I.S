package ai.jarvis.android

import android.app.Service
import android.content.Intent
import android.content.SharedPreferences
import android.os.Binder
import android.os.IBinder
import android.util.Log

/**
 * Hosts [DeviceBridge] so the brain can dispatch android_open / confirm_request
 * while the Presence UI is backgrounded.
 */
class BridgeService : Service() {

    companion object {
        private const val TAG = "JarvisBridgeService"
        const val DEFAULT_BRAIN = "http://10.0.2.2:8787"
        const val KEY_BRAIN = "brain_url"
        const val KEY_DEVICE = "device_id"
        const val KEY_TOKEN = "auth_token"
        const val ACTION_RESTART = "ai.jarvis.android.RESTART_BRIDGE"
    }

    private val binder = LocalBinder()
    private var bridge: DeviceBridge? = null

    inner class LocalBinder : Binder() {
        fun getService(): BridgeService = this@BridgeService
    }

    override fun onBind(intent: Intent?): IBinder = binder

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == ACTION_RESTART) {
            restartBridge()
        } else {
            ensureStarted()
        }
        return START_STICKY
    }

    @Synchronized
    private fun restartBridge() {
        bridge?.stop()
        bridge = null
        ensureStarted()
    }

    @Synchronized
    private fun ensureStarted() {
        if (bridge != null) return
        val prefs: SharedPreferences = getSharedPreferences("jarvis", MODE_PRIVATE)
        val brain = prefs.getString(KEY_BRAIN, DEFAULT_BRAIN)?.trim()?.takeIf { it.isNotEmpty() }
            ?: DEFAULT_BRAIN
        val deviceId = "android-" + (prefs.getString(KEY_DEVICE, null) ?: run {
            val id = java.util.UUID.randomUUID().toString().take(8)
            prefs.edit().putString(KEY_DEVICE, id).apply()
            id
        })
        val token = prefs.getString(KEY_TOKEN, "") ?: ""
        Log.i(TAG, "starting bridge device=$deviceId brain=$brain token=${token.isNotBlank()}")

        bridge = DeviceBridge(applicationContext, brain, deviceId, token).also { it.start() }
    }

    override fun onDestroy() {
        bridge?.stop()
        bridge = null
        BridgeHub.setStatus("bridge: stopped")
        super.onDestroy()
    }
}
