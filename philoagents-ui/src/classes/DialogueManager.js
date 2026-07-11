import ApiService from '../services/ApiService';
import WebSocketApiService from '../services/WebSocketApiService';

/**
 * Dialogue flow for the DOM-based dialogue box (Phase 3).
 *
 * The original manager captured every Phaser keydown and rebuilt the typed
 * message by hand, which breaks for Persian input. Typing now happens in the
 * real HTML <input> owned by DialogueBox, so this class only handles:
 *   - opening/closing the dialogue (and handing keyboard control over)
 *   - sending the message via WebSocket (with HTTP fallback)
 *   - streaming chunks into the dialogue text area
 */
class DialogueManager {
    constructor(scene) {
        this.scene = scene;
        this.dialogueBox = null;
        this.activePhilosopher = null;

        this.isStreaming = false;
        this.isWaiting = false;
        this.streamingText = '';

        this.disconnectTimeout = null;
    }

    // === Initialization ===

    initialize(dialogueBox) {
        this.dialogueBox = dialogueBox;
        this.dialogueBox.onSubmit = (message) => this.sendMessage(message);
        this.dialogueBox.onClose = () => this.closeDialogue();
    }

    // === Dialogue Flow Control ===

    startDialogue(poet) {
        this.cancelDisconnectTimeout();

        this.activePhilosopher = poet;

        // Hand keyboard control to the HTML input while the dialogue is open.
        this.scene.input.keyboard.enabled = false;
        this.scene.input.keyboard.disableGlobalCapture();

        this.dialogueBox.setName(poet.name);
        this.dialogueBox.show('', true);
        this.dialogueBox.clearInput();
        this.dialogueBox.focusInput();
    }

    closeDialogue() {
        this.dialogueBox.hide();
        this.isStreaming = false;
        this.isWaiting = false;

        // Give keyboard control back to the game.
        this.scene.input.keyboard.enabled = true;
        this.scene.input.keyboard.enableGlobalCapture();
        this.scene.input.keyboard.resetKeys();

        this.scheduleDisconnect();
    }

    isInDialogue() {
        return this.dialogueBox && this.dialogueBox.isVisible();
    }

    // === Message Processing ===

    async sendMessage(message) {
        if (this.isStreaming || this.isWaiting) {
            return;
        }

        this.isWaiting = true;
        this.dialogueBox.disableInput();
        this.dialogueBox.setText('…');

        try {
            if (this.activePhilosopher.defaultMessage) {
                await this.streamText(this.activePhilosopher.defaultMessage);
            } else {
                await this.handleWebSocketMessage(message);
            }
        } finally {
            this.isWaiting = false;
            if (this.dialogueBox.isVisible()) {
                this.dialogueBox.clearInput();
                this.dialogueBox.focusInput();
            }
        }
    }

    async handleWebSocketMessage(message) {
        this.isStreaming = true;
        this.streamingText = '';

        try {
            await WebSocketApiService.connect();

            const callbacks = {
                onMessage: () => {
                    this.finishStreaming();
                },
                onChunk: (chunk) => {
                    this.streamingText += chunk;
                    this.dialogueBox.setText(this.streamingText);
                },
                onStreamingStart: () => {
                    this.isStreaming = true;
                },
                onStreamingEnd: () => {
                    this.finishStreaming();
                }
            };

            await WebSocketApiService.sendMessage(
                this.activePhilosopher,
                message,
                callbacks
            );

            while (this.isStreaming) {
                await new Promise(resolve => setTimeout(resolve, 100));
            }

            WebSocketApiService.disconnect();
        } catch (error) {
            console.error('WebSocket error:', error);
            this.isStreaming = false;
            await this.fallbackToRegularApi(message);
        }
    }

    finishStreaming() {
        this.isStreaming = false;
        if (this.streamingText) {
            this.dialogueBox.setText(this.streamingText);
        }
    }

    async fallbackToRegularApi(message) {
        const apiResponse = await ApiService.sendMessage(
            this.activePhilosopher,
            message
        );
        await this.streamText(apiResponse);
    }

    // === Text Streaming (for default messages / HTTP fallback) ===

    async streamText(text, speed = 30) {
        this.isStreaming = true;
        let displayedText = '';

        for (let i = 0; i < text.length; i++) {
            displayedText += text[i];
            this.dialogueBox.setText(displayedText);

            await new Promise(resolve => setTimeout(resolve, speed));

            if (!this.isStreaming) break;
        }

        this.dialogueBox.setText(text);
        this.isStreaming = false;
        return true;
    }

    skipStreaming() {
        this.isStreaming = false;
    }

    // === Connection Management ===

    cancelDisconnectTimeout() {
        if (this.disconnectTimeout) {
            clearTimeout(this.disconnectTimeout);
            this.disconnectTimeout = null;
        }
    }

    scheduleDisconnect() {
        this.cancelDisconnectTimeout();

        this.disconnectTimeout = setTimeout(() => {
            WebSocketApiService.disconnect();
        }, 5000);
    }
}

export default DialogueManager;
