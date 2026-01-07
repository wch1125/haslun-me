// js/scenes/MuseumScene.js
// Natural History Museum - Gateway to Grand Central

(function() {
  'use strict';

  window.MuseumScene = new Phaser.Class({
    Extends: window.BaseScene,

    initialize: function MuseumScene() {
      window.BaseScene.call(this, { key: 'MuseumScene' });
    },

    init: function(data) {
      window.BaseScene.prototype.init.call(this, {
        playerX: data.playerX || 100,
        playerY: data.playerY || 320
      });
    },

    setupScene: function() {
      // Side bars for narrower image
      this.addSideBars(512);
      
      // Background (512x400, centered)
      this.add.image(280, 200, 'bg-museum').setDisplaySize(512, 400).setDepth(1);
      
      // Location label
      this.addLocationLabel('Natural History Museum');
      
      // Movement bounds
      this.setMovementBounds(30, 150, 500, 230);
    },

    setupExits: function() {
      // Exit left → back to Park
      this.createExit(25, 280, 30, 160, 'ParkScene', 500, 250, '←');
      
      // Exit to Grand Central (museum entrance)
      this.createDoorExit(280, 160, 120, 40, 'GrandCentralScene', 280, 350, '↑ Enter');
    }
  });

})();
