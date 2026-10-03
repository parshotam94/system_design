/**
 * High-Level Design (HLD) Progress Tracking Engine - LocalStorage Powered
 */

const HLDProgressTracker = {
  STORAGE_KEY: 'cpp_hld_mastery_progress_v1',
  TOTAL_MODULES: 40,
  TOTAL_TOPICS: 156,

  state: {
    modules: {}
  },

  init() {
    try {
      const saved = localStorage.getItem(this.STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        this.state = parsed.modules ? parsed : { modules: parsed };
      } else {
        this.state = { modules: {} };
      }
    } catch (e) {
      console.error('[HLDProgressTracker] Failed to load from localStorage', e);
      this.state = { modules: {} };
    }

    this.bindEvents();
    this.updateUI();
  },

  save() {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(this.state));
      this.updateUI();
      window.dispatchEvent(new CustomEvent('hldProgressUpdated', { detail: this.getGlobalStats() }));
    } catch (e) {
      console.error('[HLDProgressTracker] Failed to save to localStorage', e);
    }
  },

  bindEvents() {
    // Topic completion buttons on HLD pages
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('.btn-hld-topic-toggle');
      if (btn) {
        const topicId = btn.getAttribute('data-topic-id');
        const moduleId = btn.getAttribute('data-module-id');
        if (topicId && moduleId) {
          const current = this.getTopicStatus(moduleId, topicId);
          const next = current === 'completed' ? 'not_started' : 'completed';
          this.setTopicStatus(moduleId, topicId, next);
          
          if (window.showToast) {
            if (next === 'completed') {
              window.showToast(`✓ Marked HLD topic as Completed!`, 'success');
            } else {
              window.showToast(`○ Reset HLD topic progress`, 'info');
            }
          }
        }
      }

      // Quick Mark Entire HLD Module Button
      const modBtn = e.target.closest('.btn-mark-hld-module-complete');
      if (modBtn) {
        const moduleId = modBtn.getAttribute('data-module-id');
        if (moduleId) {
          this.toggleEntireModule(moduleId);
        }
      }
    });

    const statusSelect = document.getElementById('hld-module-status-select');
    if (statusSelect) {
      statusSelect.addEventListener('change', (e) => {
        const activeMod = document.querySelector('[data-current-hld-module-id]');
        const modId = activeMod ? activeMod.getAttribute('data-current-hld-module-id') : null;
        if (modId) {
          this.setModuleStatus(modId, e.target.value);
        }
      });
    }
  },

  getTopicStatus(moduleId, topicId) {
    const padId = String(moduleId).padStart(2, '0');
    if (!this.state.modules[padId] || !this.state.modules[padId].topics) {
      return 'not_started';
    }
    return this.state.modules[padId].topics[topicId] || 'not_started';
  },

  setTopicStatus(moduleId, topicId, status) {
    const padId = String(moduleId).padStart(2, '0');
    if (!this.state.modules[padId]) {
      this.state.modules[padId] = { status: 'in_progress', topics: {} };
    }
    if (!this.state.modules[padId].topics) {
      this.state.modules[padId].topics = {};
    }

    this.state.modules[padId].topics[topicId] = status;
    this.refreshModuleStatus(padId);
    this.save();
  },

  getModuleStatus(moduleId) {
    const padId = String(moduleId).padStart(2, '0');
    if (!this.state.modules[padId]) return 'not_started';
    return this.state.modules[padId].status || 'not_started';
  },

  setModuleStatus(moduleId, status) {
    const padId = String(moduleId).padStart(2, '0');
    if (!this.state.modules[padId]) {
      this.state.modules[padId] = { status: status, topics: {} };
    } else {
      this.state.modules[padId].status = status;
    }
    this.save();
  },

  refreshModuleStatus(padId) {
    const mod = this.state.modules[padId];
    if (!mod || !mod.topics) return;

    const topicVals = Object.values(mod.topics);
    if (topicVals.length === 0) {
      mod.status = 'not_started';
      return;
    }

    const completedCount = topicVals.filter(s => s === 'completed').length;
    if (completedCount === topicVals.length && completedCount > 0) {
      mod.status = 'completed';
    } else if (completedCount > 0 || topicVals.some(s => s === 'in_progress')) {
      mod.status = 'in_progress';
    } else {
      mod.status = 'not_started';
    }
  },

  toggleEntireModule(moduleId) {
    const padId = String(moduleId).padStart(2, '0');
    const topicsOnPage = document.querySelectorAll('.topic-container');
    const isCurrentlyComplete = this.getModuleStatus(padId) === 'completed';
    const targetStatus = isCurrentlyComplete ? 'not_started' : 'completed';

    if (!this.state.modules[padId]) {
      this.state.modules[padId] = { status: targetStatus, topics: {} };
    }

    topicsOnPage.forEach(t => {
      const tId = t.id;
      if (tId) {
        this.state.modules[padId].topics[tId] = targetStatus;
      }
    });

    this.state.modules[padId].status = targetStatus;
    this.save();

    if (window.showToast) {
      window.showToast(targetStatus === 'completed' ? `🎉 HLD Module ${padId} marked fully completed!` : `○ HLD Module ${padId} progress reset`, 'success');
    }
  },

  getModuleStats(moduleId, knownTotalTopics = null) {
    const padId = String(moduleId).padStart(2, '0');
    const mod = this.state.modules[padId];
    if (!mod || !mod.topics) {
      return { completed: 0, total: knownTotalTopics || 0, percentage: 0, status: 'not_started' };
    }

    const completed = Object.values(mod.topics).filter(s => s === 'completed').length;
    const total = knownTotalTopics || Object.keys(mod.topics).length || 1;
    const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
    return {
      completed,
      total,
      percentage: Math.min(100, Math.max(0, percentage)),
      status: mod.status || 'not_started'
    };
  },

  getGlobalStats() {
    let completedTopics = 0;
    let completedModules = 0;
    let inProgressModules = 0;

    for (let i = 1; i <= this.TOTAL_MODULES; i++) {
      const padId = String(i).padStart(2, '0');
      const mod = this.state.modules[padId];
      if (mod) {
        if (mod.status === 'completed') completedModules++;
        else if (mod.status === 'in_progress') inProgressModules++;

        if (mod.topics) {
          completedTopics += Object.values(mod.topics).filter(s => s === 'completed').length;
        }
      }
    }

    const overallPct = Math.round((completedTopics / this.TOTAL_TOPICS) * 100);

    return {
      completedTopics,
      totalTopics: this.TOTAL_TOPICS,
      completedModules,
      inProgressModules,
      totalModules: this.TOTAL_MODULES,
      percentage: Math.min(100, Math.max(0, overallPct))
    };
  },

  updateUI() {
    const stats = this.getGlobalStats();

    // Update Global HLD Indicators
    document.querySelectorAll('.hld-overall-progress-bar-fill').forEach(el => {
      el.style.width = `${stats.percentage}%`;
    });

    document.querySelectorAll('.hld-overall-progress-pct-text').forEach(el => {
      el.textContent = `${stats.percentage}%`;
    });

    document.querySelectorAll('.hld-total-completed-topics-count').forEach(el => {
      el.textContent = `${stats.completedTopics} / ${stats.totalTopics}`;
    });

    // Update HLD Module Cards on /hld
    document.querySelectorAll('[data-hld-module-card-id]').forEach(card => {
      const modId = card.getAttribute('data-hld-module-card-id');
      const padId = String(modId).padStart(2, '0');
      const totalTopicsAttr = parseInt(card.getAttribute('data-total-topics') || '4', 10);
      const modStats = this.getModuleStats(padId, totalTopicsAttr);

      const fill = card.querySelector('.hld-module-card-progress-fill');
      if (fill) {
        fill.style.width = `${modStats.percentage}%`;
      }

      const text = card.querySelector('.hld-module-card-progress-text');
      if (text) {
        text.textContent = `${modStats.completed}/${modStats.total} completed (${modStats.percentage}%)`;
      }

      const badge = card.querySelector('.hld-module-card-status-badge');
      if (badge) {
        if (modStats.status === 'completed') {
          badge.className = 'badge badge-completed hld-module-card-status-badge';
          badge.textContent = '✓ Completed';
        } else if (modStats.status === 'in_progress') {
          badge.className = 'badge badge-in-progress hld-module-card-status-badge';
          badge.textContent = '◐ In Progress';
        } else {
          badge.className = 'badge badge-not-started hld-module-card-status-badge';
          badge.textContent = '○ Not Started';
        }
      }
    });

    // Update HLD Module Page topic buttons
    const currentModuleEl = document.querySelector('[data-current-hld-module-id]');
    if (currentModuleEl) {
      const currentModId = currentModuleEl.getAttribute('data-current-hld-module-id');
      const padId = String(currentModId).padStart(2, '0');

      document.querySelectorAll('.topic-container').forEach(topicContainer => {
        const topicId = topicContainer.id;
        const isComp = this.getTopicStatus(padId, topicId) === 'completed';
        
        if (isComp) {
          topicContainer.classList.add('topic-completed');
        } else {
          topicContainer.classList.remove('topic-completed');
        }

        const toggleBtn = topicContainer.querySelector('.btn-hld-topic-toggle');
        if (toggleBtn) {
          if (isComp) {
            toggleBtn.className = 'btn btn-sm btn-hld-topic-toggle btn-completed';
            toggleBtn.innerHTML = `✓ Completed`;
          } else {
            toggleBtn.className = 'btn btn-sm btn-hld-topic-toggle btn-outline';
            toggleBtn.innerHTML = `○ Mark Completed`;
          }
        }
      });
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  HLDProgressTracker.init();
});

window.HLDProgressTracker = HLDProgressTracker;
