package ai.jarvis.android

import android.app.Service
import android.content.Intent
import android.content.SharedPreferences
import android.os.Binder
import android.os.IBinder
import android.util.Log

/**
 * Android device bridge service (ISSUE-033).
 *
 * Hosts a [DeviceBridge] WebSocket loop so the brain can dispatch
 * `android_open` intent/deep-link requests to this phone independent of
 * whether the chat UI is open. Started from [MainActivity].
 */
class BridgeService : Service() {

    companion object {
        private const val TAG = "JarvisBridgeService"
        const val DEFAULT_BRAIN = "http://10.0.2.2:8787"
        const val KEY_BRAIN = "brain_url"
        const val KEY_DEVICE = "device_id"

        /** Simple in-memory status text this process exposes to the UI. */
        @Volatile
        var lastStatus: String = "bridge: idle"
            private set
    }

    private val binder = LocalBinder()
    private var bridge: DeviceBridge? = null

    inner class LocalBinder : Binder() {
        fun getService(): BridgeService = this@BridgeService
    }

    override fun onBind(intent: Intent?): IBinder = binder

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        ensureStarted()
        return START_STICKY
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
        Log.i(TAG, "starting bridge for device=$deviceId brain=$brain")

        bridge = DeviceBridge(applicationContext, brain, deviceId).also { b ->
            b.listener = object : DeviceBridge.Listener {
                override fun onBridgeStatus(text: String) {
                    lastStatus = text
                    Log.i(TAG, text)
                }
            }
            b.start()
        }
    }

    override fun onDestroy() {
        bridge?.stop()
        bridge = null
        lastStatus = "bridge: stopped"
        super.onDestroy()
    }
}
