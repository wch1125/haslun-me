// js/scenes/ParkScene.js
// Central Park - Mister Softee ice cream truck

(function() {
  'use strict';

  window.ParkScene = new Phaser.Class({
    Extends: window.BaseScene,

    initialize: function ParkScene() {
      window.BaseScene.call(this, { key: 'ParkScene' });
    },

    init: function(data) {
      window.BaseScene.prototype.init.call(this, {
        playerX: data.playerX || 280,
        playerY: data.playerY || 300
      });
    },

    setupScene: function() {
      // Background (full width)
      this.add.image(280, 200, 'bg-park').setDisplaySize(560, 400);
      
      // Location label
      this.addLocationLabel('Central Park');
      
      // Movement bounds
      this.setMovementBounds(20, 80, 520, 300);
    },

    setupExits: function() {
      // Exit bottom → back to Milano
      this.createExit(280, 390, 200, 30, 'MilanoScene', 280, 160, '↓');
      
      // Exit right → to Museum
      this.createExit(545, 250, 30, 200, 'MuseumScene', 60, 320, '→');
    }
  });

})();
