/**
 * Global Search Controller - Client & Server Fast Token Search
 */

const SearchController = {
  isOpen: false,
  selectedIndex: 0,
  results: [],

  init() {
    this.modal = document.getElementById('search-modal-backdrop');
    this.input = document.getElementById('global-search-input');
    this.resultsList = document.getElementById('search-results-list');

    if (!this.modal || !this.input) return;

    // Trigger button clicks
    document.querySelectorAll('.sidebar-search-btn, .topbar-search-btn').forEach(btn => {
      btn.addEventListener('click', () => this.open());
    });

    // Close on backdrop click
    this.modal.addEventListener('click', (e) => {
      if (e.target === this.modal) this.close();
    });

    // Input events
    this.input.addEventListener('input', (e) => {
      this.handleSearch(e.target.value);
    });

    // Keydown navigation inside modal
    this.input.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.close();
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        this.selectNext();
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        this.selectPrev();
      } else if (e.key === 'Enter') {
        e.preventDefault();
        this.navigateToSelected();
      }
    });
  },

  open() {
    if (!this.modal) return;
    this.isOpen = true;
    this.modal.classList.add('active');
    this.input.value = '';
    this.input.focus();
    this.handleSearch('');
  },

  close() {
    if (!this.modal) return;
    this.isOpen = false;
    this.modal.classList.remove('active');
  },

  async handleSearch(query) {
    if (!query.trim()) {
      this.renderInitialHints();
      return;
    }

    try {
      const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
      const data = await res.json();
      this.results = data.results || [];
      this.selectedIndex = 0;
      this.renderResults();
    } catch (e) {
      console.error('Search query failed', e);
    }
  },

  renderInitialHints() {
    this.results = [
      { term: "SOLID Principles", category: "Principles", module_id: "06", topic_id: "srp", snippet: "Single Responsibility, Open-Closed, Liskov, Interface Segregation, Dependency Inversion" },
      { term: "Singleton (Thread-safe & Meyers)", category: "Design Patterns", module_id: "09", topic_id: "singleton-pattern", snippet: "Ensures single instance with static local variables and concurrency safety" },
      { term: "Factory Method vs Abstract Factory", category: "Design Patterns", module_id: "09", topic_id: "factory-method-pattern", snippet: "Creational patterns comparison for object families" },
      { term: "Observer Pattern", category: "Design Patterns", module_id: "11", topic_id: "observer-pattern", snippet: "Event-driven decoupling with subject and subscriber lifelines" },
      { term: "Composition vs Aggregation", category: "Class Relationships", module_id: "05", topic_id: "composition", snippet: "Lifetime ownership and coupling differences in C++" },
      { term: "Smart Pointers (unique_ptr, shared_ptr)", category: "Memory", module_id: "01", topic_id: "smart-pointers-ownership", snippet: "RAII resource ownership and circular reference prevention" }
    ];
    this.selectedIndex = 0;
    this.renderResults();
  },

  renderResults() {
    if (!this.resultsList) return;

    if (this.results.length === 0) {
      this.resultsList.innerHTML = `
        <div style="padding: 2rem; text-align: center; color: var(--text-muted);">
          <p>No matching LLD concepts found.</p>
        </div>
      `;
      return;
    }

    this.resultsList.innerHTML = this.results.map((item, idx) => `
      <a href="/module/${item.module_id}#${item.topic_id || ''}" 
         class="search-result-item ${idx === this.selectedIndex ? 'selected' : ''}" 
         data-index="${idx}">
        <div class="search-item-top">
          <span class="search-item-title">${item.term}</span>
          <span class="badge badge-intermediate">${item.category || 'Topic'}</span>
        </div>
        <div class="search-item-snippet">${item.snippet || ''}</div>
      </a>
    `).join('');
  },

  selectNext() {
    if (this.results.length === 0) return;
    this.selectedIndex = (this.selectedIndex + 1) % this.results.length;
    this.updateSelectionUI();
  },

  selectPrev() {
    if (this.results.length === 0) return;
    this.selectedIndex = (this.selectedIndex - 1 + this.results.length) % this.results.length;
    this.updateSelectionUI();
  },

  updateSelectionUI() {
    const items = this.resultsList.querySelectorAll('.search-result-item');
    items.forEach((item, idx) => {
      item.classList.toggle('selected', idx === this.selectedIndex);
      if (idx === this.selectedIndex) {
        item.scrollIntoView({ block: 'nearest' });
      }
    });
  },

  navigateToSelected() {
    if (this.results[this.selectedIndex]) {
      const item = this.results[this.selectedIndex];
      window.location.href = `/module/${item.module_id}#${item.topic_id || ''}`;
      this.close();
    }
  }
};

window.SearchController = SearchController;
document.addEventListener('DOMContentLoaded', () => SearchController.init());
