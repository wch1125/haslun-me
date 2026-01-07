// js/BaseScene.js
// Base class for all game scenes - reduces code duplication

(function() {
  'use strict';

  window.BaseScene = new Phaser.Class({
    Extends: Phaser.Scene,

    initialize: function BaseScene(config) {
      Phaser.Scene.call(this, config);
      this.sceneConfig = config;
    },

    init: function(data) {
      this.spawnX = data.playerX || 280;
      this.spawnY = data.playerY || 320;
      this.isTransitioning = false;
    },

    // Override in subclass to define scene-specific setup
    setupScene: function() {
      // Override this
    },

    // Override to define exits
    setupExits: function() {
      // Override this
    },

    create: function() {
      var self = this;

      // Fade in
      this.cameras.main.fadeIn(300);

      // Setup keyboard
      this.cursors = this.input.keyboard.createCursorKeys();

      // Call scene-specific setup
      this.setupScene();

      // Create player after background
      this.player = this.createPlayer(this.spawnX, this.spawnY);

      // Setup exits
      this.setupExits();
    },

    update: function() {
      if (this.isTransitioning) return;
      this.handleMovement();
    },

    // ─────────────────────────────────────────────────────────────────
    // HELPERS
    // ─────────────────────────────────────────────────────────────────

    createPlayer: function(x, y) {
      // Create circle texture if not exists
      if (!this.textures.exists('player-circle')) {
        var graphics = this.add.graphics();
        graphics.fillStyle(0xFFD700, 1);
        graphics.fillCircle(14, 14, 12);
        graphics.lineStyle(2, 0xB8960F, 1);
        graphics.strokeCircle(14, 14, 12);
        graphics.generateTexture('player-circle', 28, 28);
        graphics.destroy();
      }

      var player = this.physics.add.sprite(x, y, 'player-circle');
      player.setCollideWorldBounds(true);
      player.setDepth(100);

      // Shadow
      player.shadow = this.add.ellipse(x, y + 10, 20, 8, 0x000000, 0.3);
      player.shadow.setDepth(99);

      return player;
    },

    handleMovement: function() {
      var speed = 160;
      this.player.setVelocity(0);

      if (this.cursors.left.isDown) {
        this.player.setVelocityX(-speed);
      } else if (this.cursors.right.isDown) {
        this.player.setVelocityX(speed);
      }

      if (this.cursors.up.isDown) {
        this.player.setVelocityY(-speed);
      } else if (this.cursors.down.isDown) {
        this.player.setVelocityY(speed);
      }

      // Update shadow
      if (this.player.shadow) {
        this.player.shadow.x = this.player.x;
        this.player.shadow.y = this.player.y + 10;
      }
    },

    // Add location label
    addLocationLabel: function(text) {
      this.add.text(16, 16, text, {
        fontFamily: 'Georgia, serif',
        fontSize: '18px',
        color: '#ffffff',
        stroke: '#000000',
        strokeThickness: 4
      }).setDepth(10);
    },

    // Set world bounds for player movement
    setMovementBounds: function(x, y, width, height) {
      this.physics.world.setBounds(x, y, width, height);
    },

    // Create exit zone with arrow hint
    createExit: function(x, y, w, h, targetScene, spawnX, spawnY, hint) {
      var self = this;

      var zone = this.add.zone(x, y, w, h);
      this.physics.add.existing(zone, true);

      // Exit hint arrow
      var hintText = this.add.text(x, y, hint, {
        fontFamily: 'Arial',
        fontSize: '24px',
        color: '#FFD700',
        stroke: '#000000',
        strokeThickness: 3
      }).setOrigin(0.5).setAlpha(0.8).setDepth(10);

      // Pulsing animation
      this.tweens.add({
        targets: hintText,
        alpha: 0.3,
        duration: 800,
        yoyo: true,
        repeat: -1
      });

      // Transition on overlap
      this.physics.add.overlap(this.player, zone, function() {
        if (self.isTransitioning) return;
        self.isTransitioning = true;

        self.cameras.main.fadeOut(300, 0, 0, 0);
        self.cameras.main.once('camerafadeoutcomplete', function() {
          self.scene.start(targetScene, { playerX: spawnX, playerY: spawnY });
        });
      });
    },

    // Create labeled door exit (for building entrances)
    createDoorExit: function(x, y, w, h, targetScene, spawnX, spawnY, hint) {
      var self = this;

      var zone = this.add.zone(x, y, w, h);
      this.physics.add.existing(zone, true);

      var hintText = this.add.text(x, y + 30, hint, {
        fontFamily: 'Georgia, serif',
        fontSize: '16px',
        color: '#FFD700',
        stroke: '#000000',
        strokeThickness: 3
      }).setOrigin(0.5).setAlpha(0.9).setDepth(10);

      this.tweens.add({
        targets: hintText,
        alpha: 0.5,
        duration: 600,
        yoyo: true,
        repeat: -1
      });

      this.physics.add.overlap(this.player, zone, function() {
        if (self.isTransitioning) return;
        self.isTransitioning = true;
        self.cameras.main.fadeOut(300, 0, 0, 0);
        self.cameras.main.once('camerafadeoutcomplete', function() {
          self.scene.start(targetScene, { playerX: spawnX, playerY: spawnY });
        });
      });
    },

    // Add dark bars for narrower images
    addSideBars: function(imageWidth) {
      var canvasWidth = 560;
      var barWidth = (canvasWidth - imageWidth) / 2;
      if (barWidth > 0) {
        this.add.rectangle(barWidth / 2, 200, barWidth, 400, 0x1a1a24);
        this.add.rectangle(canvasWidth - barWidth / 2, 200, barWidth, 400, 0x1a1a24);
      }
    }
  });

})();
