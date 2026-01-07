// js/scenes/BootScene.js
// Preloads all assets, then waits for player to click Start

(function() {
  'use strict';

  window.BootScene = new Phaser.Class({
    Extends: Phaser.Scene,

    initialize: function BootScene() {
      Phaser.Scene.call(this, { key: 'BootScene' });
    },

    preload: function() {
      // Loading text
      var loadingText = this.add.text(280, 180, 'Loading...', {
        fontFamily: 'Georgia, serif',
        fontSize: '24px',
        color: '#FFD700'
      }).setOrigin(0.5);

      // Progress bar
      var progressBar = this.add.graphics();
      var progressBox = this.add.graphics();
      progressBox.fillStyle(0x222222, 0.8);
      progressBox.fillRect(180, 220, 200, 20);

      this.load.on('progress', function(value) {
        progressBar.clear();
        progressBar.fillStyle(0xC4703F, 1);
        progressBar.fillRect(182, 222, 196 * value, 16);
      });

      // Load all scene backgrounds
      this.load.image('bg-subway', 'assets/scenes/subway-72nd.png');
      this.load.image('bg-milano', 'assets/scenes/milano-market.png');
      this.load.image('bg-park', 'assets/scenes/mister-softee.png');
      this.load.image('bg-museum', 'assets/scenes/museum.png');
      this.load.image('bg-grandcentral', 'assets/scenes/grand-central.png');
    },

    create: function() {
      var self = this;
      
      console.log('[Digital Watercolors] Assets loaded');
      
      // Enable the start button
      var startBtn = document.getElementById('start-btn');
      var titleOverlay = document.getElementById('title-overlay');
      
      startBtn.addEventListener('click', function() {
        titleOverlay.classList.add('hidden');
        self.scene.start('SubwayScene');
      });
    }
  });

})();
