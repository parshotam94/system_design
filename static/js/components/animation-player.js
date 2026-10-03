/**
 * Reusable Interactive Animation Player & Simulation Engine
 */

class AnimationPlayer {
  constructor(containerEl, config) {
    this.container = containerEl;
    this.config = config; // { title, steps: [{ badge, narrative, renderStage(stageEl) }] }
    this.currentStep = 0;
    this.isPlaying = false;
    this.timer = null;
    this.speedMs = 2500;
    this.init();
  }

  init() {
    this.renderShell();
    this.renderStep(0);
    this.bindEvents();
  }

  renderShell() {
    this.container.innerHTML = `
      <div class="sim-container">
        <div class="sim-header">
          <div class="sim-title">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polygon points="10 8 16 12 10 16 10 8"></polygon></svg>
            ${this.config.title || 'Interactive Concept Simulation'}
          </div>
          <div class="sim-controls">
            <button class="sim-btn btn-prev">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="19 20 9 12 19 4 19 20"></polygon><line x1="5" y1="19" x2="5" y2="5"></line></svg>
              Prev
            </button>
            <button class="sim-btn primary btn-play">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
              Play
            </button>
            <button class="sim-btn btn-next">
              Next
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 4 15 12 5 20 5 4"></polygon><line x1="19" y1="5" x2="19" y2="19"></line></svg>
            </button>
            <button class="sim-btn btn-reset">Reset</button>
          </div>
        </div>
        <div class="sim-stage"></div>
        <div class="sim-step-narrative">
          <span class="sim-step-badge">STEP 1/${this.config.steps.length}</span>
          <span class="narrative-text"></span>
        </div>
      </div>
    `;

    this.stageEl = this.container.querySelector('.sim-stage');
    this.badgeEl = this.container.querySelector('.sim-step-badge');
    this.narrativeEl = this.container.querySelector('.narrative-text');
    this.playBtn = this.container.querySelector('.btn-play');
  }

  bindEvents() {
    this.container.querySelector('.btn-prev').addEventListener('click', () => this.prev());
    this.container.querySelector('.btn-next').addEventListener('click', () => this.next());
    this.container.querySelector('.btn-reset').addEventListener('click', () => this.reset());
    this.playBtn.addEventListener('click', () => this.togglePlay());
  }

  renderStep(index) {
    if (index < 0 || index >= this.config.steps.length) return;
    this.currentStep = index;
    const step = this.config.steps[index];

    this.badgeEl.textContent = `STEP ${index + 1}/${this.config.steps.length}`;
    this.narrativeEl.textContent = step.narrative;
    
    // Call step renderer
    if (typeof step.renderStage === 'function') {
      step.renderStage(this.stageEl);
    }
  }

  next() {
    if (this.currentStep < this.config.steps.length - 1) {
      this.renderStep(this.currentStep + 1);
    } else {
      this.pause();
    }
  }

  prev() {
    if (this.currentStep > 0) {
      this.renderStep(this.currentStep - 1);
    }
  }

  reset() {
    this.pause();
    this.renderStep(0);
  }

  togglePlay() {
    if (this.isPlaying) {
      this.pause();
    } else {
      this.play();
    }
  }

  play() {
    this.isPlaying = true;
    this.playBtn.innerHTML = `
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>
      Pause
    `;

    if (this.currentStep === this.config.steps.length - 1) {
      this.renderStep(0);
    }

    this.timer = setInterval(() => {
      if (this.currentStep < this.config.steps.length - 1) {
        this.next();
      } else {
        this.pause();
      }
    }, this.speedMs);
  }

  pause() {
    this.isPlaying = false;
    clearInterval(this.timer);
    if (this.playBtn) {
      this.playBtn.innerHTML = `
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
        Play
      `;
    }
  }
}

window.AnimationPlayer = AnimationPlayer;
