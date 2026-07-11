import { Game } from './scenes/Game';
import { MainMenu } from './scenes/MainMenu';
import { Preloader } from './scenes/Preloader';
import { PauseMenu } from './scenes/PauseMenu';

const config = {
    type: Phaser.AUTO,
    width: 1024,
    height: 768,
    parent: 'game-container',
    scale: {
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH
    },
    scene: [
        Preloader,
        MainMenu,
        Game,
        PauseMenu
    ],
    physics: {
        default: "arcade",
        arcade: {
            gravity: { y: 0 },
        },
    },
};

// Make sure Vazirmatn is loaded before Phaser draws any Persian text on the
// canvas, otherwise the first menu render falls back to a default font.
const startGame = () => new Phaser.Game(config);

if (document.fonts && document.fonts.load) {
    Promise.all([
        document.fonts.load('28px Vazirmatn'),
        document.fonts.load('bold 28px Vazirmatn')
    ]).catch(() => {}).finally(startGame);
} else {
    startGame();
}
