// js/scenes/GrandCentralScene.js
// Grand Central Terminal - Finale location

(function() {
  'use strict';

  window.GrandCentralScene = new Phaser.Class({
    Extends: window.BaseScene,

    initialize: function GrandCentralScene() {
      window.BaseScene.call(this, { key: 'GrandCentralScene' });
    },

    init: function(data) {
      window.BaseScene.prototype.init.call(this, {
        playerX: data.playerX || 280,
        playerY: data.playerY || 350
      });
    },

    setupScene: function() {
      // Side bars for narrower image
      this.addSideBars(401);
      
      // Background (401x400, centered)
      this.add.image(280, 200, 'bg-grandcentral').setDisplaySize(401, 400).setDepth(1);
      
      // Location label
      this.addLocationLabel('Grand Central Terminal');
      
      // "You made it" message
      var congrats = this.add.text(280, 55, '✦ You\'ve arrived ✦', {
        fontFamily: 'Georgia, serif',
        fontSize: '22px',
        color: '#FFD700',
        stroke: '#000000',
        strokeThickness: 4
      }).setOrigin(0.5).setDepth(10);

      this.tweens.add({
        targets: congrats,
        scale: 1.1,
        duration: 1200,
        yoyo: true,
        repeat: -1,
        ease: 'Sine.easeInOut'
      });

      // Subtitle
      this.add.text(280, 85, 'Thanks for wandering', {
        fontFamily: 'Georgia, serif',
        fontSize: '12px',
        color: '#aaaaaa',
        stroke: '#000000',
        strokeThickness: 2
      }).setOrigin(0.5).setDepth(10);
      
      // Movement bounds
      this.setMovementBounds(90, 150, 380, 230);
    },

    setupExits: function() {
      // Exit bottom → back to Museum
      this.createExit(280, 390, 200, 30, 'MuseumScene', 280, 200, '↓ Exit');
    }
  });

})();
