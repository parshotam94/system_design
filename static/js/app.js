/**
 * C++ Low-Level Design Mastery - Global Application Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  initSidebar();
  initProgressSync();
  initGlobalShortcuts();
});

function initSidebar() {
  const sidebar = document.querySelector('.sidebar');
  const toggleBtn = document.querySelector('.sidebar-toggle-btn');
  const mobileToggle = document.querySelector('.mobile-menu-btn');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
      localStorage.setItem('sidebar_collapsed', sidebar.classList.contains('collapsed'));
    });
  }

  if (mobileToggle && sidebar) {
    mobileToggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });
  }
}

function initProgressSync() {
  if (window.ProgressTracker) {
    window.ProgressTracker.init();
    window.ProgressTracker.updateUI();
  }
}

function initGlobalShortcuts() {
  document.addEventListener('keydown', (e) => {
    // Ctrl + K or Cmd + K opens search
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      if (window.SearchController) {
        window.SearchController.open();
      }
    }
  });
}

// Global Toast Notification Helper
window.showToast = function(message, type = 'info') {
  let toast = document.getElementById('global-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'global-toast';
    toast.style.cssText = `
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      background: #0d1527;
      border: 1px solid rgba(56, 189, 248, 0.4);
      box-shadow: 0 10px 30px rgba(0,0,0,0.8), 0 0 15px rgba(56, 189, 248, 0.3);
      color: #fff;
      padding: 0.75rem 1.25rem;
      border-radius: 8px;
      font-size: 0.88rem;
      z-index: 9999;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      transition: all 0.3s ease;
      opacity: 0;
      transform: translateY(10px);
    `;
    document.body.appendChild(toast);
  }

  toast.textContent = message;
  toast.style.opacity = '1';
  toast.style.transform = 'translateY(0)';

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
  }, 2500);
};
