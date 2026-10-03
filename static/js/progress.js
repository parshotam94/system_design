/**
 * Progress Tracking Engine - LocalStorage Powered
 */

const ProgressTracker = {
  STORAGE_KEY: 'cpp_lld_progress_v1',
  
  // State: { [moduleId]: { status: 'not_started' | 'in_progress' | 'completed', topics: { [topicId]: status } } }
  state: {},

  init() {
    try {
      const saved = localStorage.getItem(this.STORAGE_KEY);
      if (saved) {
        this.state = JSON.parse(saved);
      }
    } catch (e) {
      console.error('Failed to load progress from localStorage', e);
      this.state = {};
    }
  },

  save() {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(this.state));
      this.updateUI();
    } catch (e) {
      console.error('Failed to save progress', e);
    }
  },

  getModuleStatus(moduleId) {
    if (!this.state[moduleId]) return 'not_started';
    return this.state[moduleId].status || 'not_started';
  },

  setModuleStatus(moduleId, status) {
    if (!this.state[moduleId]) {
      this.state[moduleId] = { status: status, topics: {} };
    } else {
      this.state[moduleId].status = status;
    }
    this.save();
  },

  setTopicStatus(moduleId, topicId, status) {
    if (!this.state[moduleId]) {
      this.state[moduleId] = { status: 'in_progress', topics: {} };
    }
    this.state[moduleId].topics[topicId] = status;

    // Recalculate module status based on topics
    const topics = Object.values(this.state[moduleId].topics);
    if (topics.every(s => s === 'completed')) {
      this.state[moduleId].status = 'completed';
    } else if (topics.some(s => s === 'completed' || s === 'in_progress')) {
      this.state[moduleId].status = 'in_progress';
    }
    
    this.save();
  },

  calculateOverallProgress() {
    const modules = document.querySelectorAll('.module-nav-link');
    if (!modules.length) return 0;

    let completedCount = 0;
    let inProgressCount = 0;
    const total = 24; // 24 modules total

    for (let i = 1; i <= total; i++) {
      const id = i < 10 ? `0${i}` : `${i}`;
      const status = this.getModuleStatus(id);
      if (status === 'completed') {
        completedCount++;
      } else if (status === 'in_progress') {
        inProgressCount++;
      }
    }

    const percentage = Math.round(((completedCount + (inProgressCount * 0.5)) / total) * 100);
    return Math.min(100, Math.max(0, percentage));
  },

  updateUI() {
    const pct = this.calculateOverallProgress();

    // Update progress bars
    document.querySelectorAll('.progress-fill-mini, .progress-fill-global').forEach(el => {
      el.style.width = `${pct}%`;
    });

    document.querySelectorAll('.progress-info-pct, .progress-pct-display').forEach(el => {
      el.textContent = `${pct}%`;
    });

    // Update sidebar module indicators
    document.querySelectorAll('.module-nav-link').forEach(link => {
      const modId = link.getAttribute('data-module-id');
      if (modId) {
        const status = this.getModuleStatus(modId);
        const indicator = link.querySelector('.nav-status-indicator');
        if (indicator) {
          indicator.className = `nav-status-indicator ${status}`;
        }
      }
    });
  }
};

window.ProgressTracker = ProgressTracker;
