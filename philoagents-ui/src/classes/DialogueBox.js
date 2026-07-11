/**
 * DOM-based dialogue box (Phase 3).
 *
 * The original DialogueBox drew text on the Phaser canvas, which handles
 * Persian (RTL, joined letters) poorly. This version renders an HTML overlay
 * on top of the canvas instead:
 *   - proper RTL layout via CSS `direction: rtl`
 *   - Vazirmatn font
 *   - a real <input> element, so Persian typing / IME just works
 *
 * Styles live in public/style.css (#dialogue-panel and friends).
 */
class DialogueBox {
    constructor(scene) {
        this.scene = scene;
        this.awaitingInput = false;
        this.onSubmit = null; // set by DialogueManager
        this.onClose = null;  // set by DialogueManager

        // The Game scene can be restarted (e.g. "reset game"), so drop any
        // panel left over from a previous scene instance.
        const existing = document.getElementById('dialogue-panel');
        if (existing) {
            existing.remove();
        }

        const gameContainer = document.getElementById('game-container');

        this.panel = document.createElement('div');
        this.panel.id = 'dialogue-panel';

        this.nameEl = document.createElement('div');
        this.nameEl.id = 'dialogue-name';

        this.textEl = document.createElement('div');
        this.textEl.id = 'dialogue-text';

        this.form = document.createElement('form');
        this.form.id = 'dialogue-form';

        this.input = document.createElement('input');
        this.input.id = 'dialogue-input';
        this.input.type = 'text';
        this.input.dir = 'rtl';
        this.input.autocomplete = 'off';
        this.input.placeholder = 'پرسش خود را بنویسید و Enter را بزنید…';

        this.form.appendChild(this.input);
        this.panel.appendChild(this.nameEl);
        this.panel.appendChild(this.textEl);
        this.panel.appendChild(this.form);
        gameContainer.appendChild(this.panel);

        this.form.addEventListener('submit', (event) => {
            event.preventDefault();
            const message = this.input.value.trim();
            if (message && this.onSubmit) {
                this.onSubmit(message);
            }
        });

        this.input.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && this.onClose) {
                this.onClose();
            }
            // Keep game keys (SPACE, arrows, ESC) from leaking into Phaser
            // while the player is typing.
            event.stopPropagation();
        });

        this.hide();
    }

    setName(name) {
        this.nameEl.textContent = name;
    }

    show(message, awaitInput = false) {
        this.textEl.textContent = message;
        this.panel.style.display = 'flex';
        this.awaitingInput = awaitInput;
    }

    setText(message) {
        this.textEl.textContent = message;
        // Keep the newest streamed line visible.
        this.textEl.scrollTop = this.textEl.scrollHeight;
    }

    clearInput() {
        this.input.value = '';
    }

    focusInput() {
        this.input.removeAttribute('disabled');
        this.input.focus();
    }

    disableInput() {
        this.input.setAttribute('disabled', 'disabled');
    }

    hide() {
        this.panel.style.display = 'none';
        this.awaitingInput = false;
        this.input.value = '';
    }

    isVisible() {
        return this.panel.style.display !== 'none';
    }

    isAwaitingInput() {
        return this.awaitingInput;
    }
}

export default DialogueBox;
