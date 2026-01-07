// js/scenes/MilanoScene.js
// Milano Market - Corner bodega

(function() {
  'use strict';

  window.MilanoScene = new Phaser.Class({
    Extends: window.BaseScene,

    initialize: function MilanoScene() {
      window.BaseScene.call(this, { key: 'MilanoScene' });
    },

    init: function(data) {
      window.BaseScene.prototype.init.call(this, {
        playerX: data.playerX || 280,
        playerY: data.playerY || 320
      });
    },

    setupScene: function() {
      // Side bars for narrower image
      this.addSideBars(299);
      
      // Background (299x400, centered)
      this.add.image(280, 200, 'bg-milano').setDisplaySize(299, 400).setDepth(1);
      
      // Location label
      this.addLocationLabel('Milano Market');
      
      // Movement bounds
      this.setMovementBounds(140, 150, 280, 230);
    },

    setupExits: function() {
      // Exit left → back to Subway
      this.createExit(130, 280, 30, 160, 'SubwayScene', 500, 320, '←');
      
      // Exit top → to Park
      this.createExit(280, 140, 160, 30, 'ParkScene', 280, 360, '↑');
    }
  });

})();
