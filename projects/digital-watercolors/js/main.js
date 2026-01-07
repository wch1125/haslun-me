// js/main.js
// NYC Wanderer - Main game initialization

(function() {
  'use strict';

  var config = {
    type: Phaser.AUTO,
    width: 560,
    height: 400,
    parent: 'game',
    backgroundColor: '#1a1a24',
    physics: {
      default: 'arcade',
      arcade: {
        gravity: { y: 0 },
        debug: false
      }
    },
    scene: [
      window.BootScene,
      window.SubwayScene,
      window.MilanoScene,
      window.ParkScene,
      window.MuseumScene,
      window.GrandCentralScene
    ]
  };

  // Create game instance
  var game = new Phaser.Game(config);

  console.log('[Digital Watercolors] Game initialized');
  console.log('[Digital Watercolors] Arrow keys to move');

})();
