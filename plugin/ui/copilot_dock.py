"""Copilot dock widget for AI interaction."""

from qgis.PyQt.QtWidgets import (
    QDockWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QComboBox,
    QLabel, QWidget, QSplitter
)
from qgis.PyQt.QtCore import Qt, pyqtSignal, QThread
from qgis.PyQt.QtGui import QTextCursor


class CopilotDock(QDockWidget):
    """Dock widget for SPAGeo Copilot."""

    def __init__(self, iface, agent):
        """Initialize Copilot dock."""
        super().__init__("SPAGeo Copilot", iface.mainWindow())
        self.iface = iface
        self.agent = agent

        # Setup UI
        self.setup_ui()

        # Connect signals
        self.connect_signals()

    def setup_ui(self):
        """Setup Copilot UI."""
        # Main widget
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)

        # Provider selector
        provider_layout = QHBoxLayout()
        provider_layout.addWidget(QLabel("AI Provider:"))
        self.provider_combo = QComboBox()
        self.provider_combo.addItems([
            'OpenAI (GPT-4)',
            'Anthropic (Claude)',
            'Google (Gemini)',
            'AWS Bedrock',
            'Ollama (Local)'
        ])
        provider_layout.addWidget(self.provider_combo)
        layout.addLayout(provider_layout)

        # Chat history
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.chat_history)

        # Input area
        input_layout = QHBoxLayout()
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText(
            "Ask SPAGeo Copilot anything...\n"
            "e.g., 'Create a model for my study area'"
        )
        self.input_field.setMaximumHeight(80)
        input_layout.addWidget(self.input_field)

        self.send_button = QPushButton("Send")
        self.send_button.setMinimumWidth(80)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #2a6d8c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a8dac;
            }
        """)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

        # Action buttons
        action_layout = QHBoxLayout()
        self.clear_button = QPushButton("Clear Chat")
        self.screenshot_button = QPushButton("📷 Screenshot")
        self.export_button = QPushButton("Export Transcript")
        action_layout.addWidget(self.clear_button)
        action_layout.addWidget(self.screenshot_button)
        action_layout.addWidget(self.export_button)
        layout.addLayout(action_layout)

        self.setWidget(main_widget)
        self.setMinimumWidth(400)
        self.setMinimumHeight(500)

    def connect_signals(self):
        """Connect UI signals."""
        self.send_button.clicked.connect(self.send_message)
        self.input_field.keyPressEvent = self._handle_key_press
        self.clear_button.clicked.connect(self.clear_chat)
        self.screenshot_button.clicked.connect(self.capture_screenshot)
        self.export_button.clicked.connect(self.export_transcript)
        self.provider_combo.currentIndexChanged.connect(self.change_provider)

        # Agent signals
        self.agent.response_received.connect(self.on_response)
        self.agent.script_generated.connect(self.on_script_generated)
        self.agent.error_occurred.connect(self.on_error)

    def _handle_key_press(self, event):
        """Handle Enter key to send message."""
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
            self.send_message()
        else:
            QTextEdit.keyPressEvent(self.input_field, event)

    def send_message(self):
        """Send user message to AI agent."""
        message = self.input_field.toPlainText().strip()
        if not message:
            return

        # Display user message
        self.display_message("You", message, "user")

        # Clear input
        self.input_field.clear()

        # Disable send button during processing
        self.send_button.setEnabled(False)
        self.send_button.setText("Processing...")

        # Send to agent (in thread to avoid UI freeze)
        self.agent.process_message(message)

    def on_response(self, response: str):
        """Handle AI response."""
        self.display_message("SPAGeo Copilot", response, "assistant")
        self.send_button.setEnabled(True)
        self.send_button.setText("Send")

    def on_script_generated(self, script: str):
        """Handle generated PyQGIS script."""
        self.display_message(
            "Generated Script",
            f"```python\n{script}\n```",
            "script"
        )
        self.send_button.setEnabled(True)
        self.send_button.setText("Send")

    def on_error(self, error: str):
        """Handle agent errors."""
        self.display_message("Error", f"❌ {error}", "error")
        self.send_button.setEnabled(True)
        self.send_button.setText("Send")

    def display_message(self, sender: str, content: str, msg_type: str = "user"):
        """Display message in chat history."""
        # Format message based on type
        if msg_type == "user":
            html = f"""
            <div style="margin: 8px 0;">
                <b style="color: #2a6d8c;">{sender}:</b>
                <div style="background-color: #e3f2fd; padding: 8px; border-radius: 4px; margin-top: 4px;">
                    {content}
                </div>
            </div>
            """
        elif msg_type == "assistant":
            html = f"""
            <div style="margin: 8px 0;">
                <b style="color: #2e7d32;">{sender}:</b>
                <div style="background-color: #e8f5e9; padding: 8px; border-radius: 4px; margin-top: 4px;">
                    {content}
                </div>
            </div>
            """
        elif msg_type == "script":
            html = f"""
            <div style="margin: 8px 0;">
                <b style="color: #e65100;">{sender}:</b>
                <div style="background-color: #fff3e0; padding: 8px; border-radius: 4px; margin-top: 4px; font-family: monospace;">
                    {content}
                </div>
            </div>
            """
        else:  # error
            html = f"""
            <div style="margin: 8px 0;">
                <b style="color: #c62828;">{sender}:</b>
                <div style="background-color: #ffebee; padding: 8px; border-radius: 4px; margin-top: 4px;">
                    {content}
                </div>
            </div>
            """

        self.chat_history.append(html)
        self.chat_history.moveCursor(QTextCursor.End)

    def clear_chat(self):
        """Clear chat history."""
        self.chat_history.clear()

    def capture_screenshot(self):
        """Capture and send screenshot to AI."""
        # Implementation using GeoAgent screenshot capability[citation:2]
        pass

    def export_transcript(self):
        """Export chat transcript."""
        # Implementation
        pass

    def change_provider(self, index: int):
        """Change AI provider."""
        providers = ['openai', 'anthropic', 'google', 'bedrock', 'ollama']
        provider = providers[index] if index < len(providers) else 'openai'
        self.agent.initialize(provider)

