// js/scenes/SubwayScene.js
// 72nd Street Subway - Starting location

(function() {
  'use strict';

  window.SubwayScene = new Phaser.Class({
    Extends: window.BaseScene,

    initialize: function SubwayScene() {
      window.BaseScene.call(this, { key: 'SubwayScene' });
    },

    init: function(data) {
      window.BaseScene.prototype.init.call(this, {
        playerX: data.playerX || 100,
        playerY: data.playerY || 320
      });
    },

    setupScene: function() {
      // Background (549x400)
      this.add.image(280, 200, 'bg-subway').setDisplaySize(549, 400);
      
      // Location label
      this.addLocationLabel('72nd Street Subway');
      
      // Movement bounds
      this.setMovementBounds(20, 150, 520, 230);
    },

    setupExits: function() {
      // Exit right → Milano Market
      this.createExit(545, 280, 30, 160, 'MilanoScene', 160, 320, '→');
    }
  });

})();
