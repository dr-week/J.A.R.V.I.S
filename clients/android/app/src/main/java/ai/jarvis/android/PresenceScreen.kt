package ai.jarvis.android

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

/** Field-style Presence — pair / bridge / confirm / open web (not product chat). */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PresenceScreen(vm: PresenceViewModel) {
    val state by vm.state.collectAsState()
    val bridge by vm.bridgeStatus.collectAsState()
    val pending by vm.pending.collectAsState()

    Scaffold(
        topBar = { TopAppBar(title = { Text("Jarvis Presence") }) },
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(12.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Text(state.statusLine, style = MaterialTheme.typography.bodyMedium)
            Text(bridge, style = MaterialTheme.typography.bodySmall)
            Text(state.healthLine, style = MaterialTheme.typography.bodySmall)
            Text("Device: ${state.deviceId}", style = MaterialTheme.typography.labelSmall)

            OutlinedTextField(
                value = state.brainUrl,
                onValueChange = vm::onBrainUrlChange,
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                label = { Text("Brain URL") },
                supportingText = {
                    Text("Emulator: http://10.0.2.2:8787 · Phone: http://PC_LAN_IP:8787")
                },
            )
            OutlinedTextField(
                value = state.pairingSecret,
                onValueChange = vm::onSecretChange,
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                label = { Text("Pairing secret") },
                supportingText = { Text("Must match JARVIS_PAIRING_SECRET") },
            )
            OutlinedTextField(
                value = state.webAssistantUrl,
                onValueChange = vm::onWebUrlChange,
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                label = { Text("Full assistant (web) URL") },
            )

            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = vm::checkHealth, enabled = !state.busy) { Text("Health") }
                Button(onClick = vm::pair, enabled = !state.busy) {
                    Text(if (state.paired) "Re-pair" else "Pair")
                }
                OutlinedButton(onClick = vm::restartBridge) { Text("Bridge") }
            }

            Button(
                onClick = vm::openFullAssistant,
                modifier = Modifier.fillMaxWidth(),
            ) { Text("Open full assistant") }

            pending?.let { p ->
                Text(
                    "Confirm: ${p.tool}",
                    style = MaterialTheme.typography.titleMedium,
                )
                Text(p.paramsJson, style = MaterialTheme.typography.bodySmall)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(onClick = vm::approveConfirm) { Text("Approve") }
                    OutlinedButton(onClick = vm::denyConfirm) { Text("Deny") }
                }
            }

            Text("LAN smoke (optional)", style = MaterialTheme.typography.titleSmall)
            OutlinedTextField(
                value = state.smokeDraft,
                onValueChange = vm::onSmokeDraftChange,
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                label = { Text("Quick ping") },
            )
            Button(onClick = vm::smokeSend, enabled = !state.busy) { Text("Send smoke") }
            if (state.smokeReply.isNotBlank()) {
                Text(state.smokeReply, style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}
