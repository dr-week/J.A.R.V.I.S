package ai.jarvis.android

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

val colorBg = Color(0xFF0F0F13)
val colorSurface = Color(0xFF19191E)
val colorSurfaceElevated = Color(0xFF232328)
val colorBorder = Color(0xFF333333)
val colorAccent = Color(0xFF0A84FF)
val colorText = Color(0xFFF0F0F2)
val colorTextMuted = Color(0xFF8E8E93)
val colorUserBubble = Color(0xFF0A84FF)
val colorAssistBubble = Color(0xFF1E1E2E)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreen(vm: ChatViewModel) {
    val state by vm.state.collectAsState()
    val listState = rememberLazyListState()

    LaunchedEffect(state.messages.size, state.messages.lastOrNull()?.text) {
        if (state.messages.isNotEmpty()) {
            listState.animateScrollToItem(state.messages.lastIndex)
        }
    }

    Scaffold(
        containerColor = colorBg,
        topBar = {
            TopAppBar(
                title = { Text("Jarvis", color = colorText) },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = colorSurface)
            )
        },
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            OutlinedTextField(
                value = state.brainUrl,
                onValueChange = vm::onBrainUrlChange,
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                label = { Text("Brain URL") },
                supportingText = {
                    Text("Phone on Wi‑Fi: http://YOUR_PC_LAN_IP:8787 · Emulator: http://10.0.2.2:8787")
                },
            )
            Text(
                text = state.status,
                style = MaterialTheme.typography.bodySmall,
                color = colorTextMuted,
            )
            Text(
                text = BridgeService.lastStatus,
                style = MaterialTheme.typography.labelSmall,
                color = if (BridgeService.lastStatus.contains("connected")) colorAccent else colorTextMuted,
            )
            LazyColumn(
                state = listState,
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth(),
                contentPadding = PaddingValues(vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                items(state.messages, key = { it.id }) { msg ->
                    val isUser = msg.role == "user"
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = if (isUser) Arrangement.End else Arrangement.Start
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth(0.85f)
                        ) {
                            Text(
                                text = if (isUser) "You" else "Jarvis",
                                style = MaterialTheme.typography.labelMedium,
                                color = if (isUser) colorAccent else colorTextMuted,
                                modifier = Modifier.align(if (isUser) Alignment.End else Alignment.Start)
                            )
                            androidx.compose.foundation.layout.Box(
                                modifier = Modifier
                                    .padding(top = 4.dp)
                                    .androidx.compose.foundation.background(
                                        color = if (isUser) colorUserBubble else colorAssistBubble,
                                        shape = RoundedCornerShape(12.dp)
                                    )
                                    .padding(12.dp)
                            ) {
                                Text(
                                    text = msg.text.ifBlank { "…" },
                                    color = colorText
                                )
                            }
                        }
                    }
                }
            }
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                OutlinedTextField(
                    value = state.draft,
                    onValueChange = vm::onDraftChange,
                    modifier = Modifier.weight(1f),
                    singleLine = true,
                    enabled = !state.busy,
                    label = { Text("Message") },
                )
                Button(
                    onClick = vm::send, 
                    enabled = !state.busy && state.draft.isNotBlank(),
                    colors = ButtonDefaults.buttonColors(containerColor = colorAccent, contentColor = colorText)
                ) {
                    Text("Send")
                }
            }
        }
    }
}
