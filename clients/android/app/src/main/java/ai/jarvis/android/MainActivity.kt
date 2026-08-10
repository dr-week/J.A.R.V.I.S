package ai.jarvis.android

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.darkColorScheme
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Start the device-bridge service so the brain can dispatch
        // android_open intent/deep-link requests (ISSUE-033) anytime.
        startService(Intent(this, BridgeService::class.java))
        enableEdgeToEdge()
        val prefs = getSharedPreferences("jarvis", MODE_PRIVATE)
        setContent {
            MaterialTheme(colorScheme = darkColorScheme()) {
                Surface(modifier = Modifier.fillMaxSize()) {
                    val vm: ChatViewModel = viewModel(
                        factory = ChatViewModel.factory(prefs)
                    )
                    ChatScreen(vm)
                }
            }
        }
    }
}
