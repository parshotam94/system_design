/**
 * Reusable Design Comparison Matrix Component
 */

const ComparisonTable = {
  render(containerEl, data) {
    // data: { title, columns: ["Aspect", "Option A", "Option B"], rows: [["Definition", "..."], ["Lifetime", "..."]] }
    const { title, columns = [], rows = [] } = data;

    const headerHtml = columns.map(c => `<th>${c}</th>`).join('');
    const rowsHtml = rows.map(row => `
      <tr>
        ${row.map((cell, idx) => idx === 0 ? `<td class="comp-aspect">${cell}</td>` : `<td>${cell}</td>`).join('')}
      </tr>
    `).join('');

    containerEl.innerHTML = `
      <div class="glass-panel" style="margin: 1.5rem 0; overflow-x: auto; padding: 1.5rem;">
        ${title ? `<h4 style="margin-bottom: 1rem; color: #fff;">${title}</h4>` : ''}
        <table class="comp-table" style="width: 100%; border-collapse: collapse; font-size: 0.88rem; text-align: left;">
          <thead>
            <tr style="border-bottom: 1.5px solid rgba(56, 189, 248, 0.3); color: var(--accent-cyan); font-weight: 700;">
              ${headerHtml}
            </tr>
          </thead>
          <tbody>
            ${rowsHtml}
          </tbody>
        </table>
      </div>
    `;

    // Inject simple table cell styling
    containerEl.querySelectorAll('th, td').forEach(el => {
      el.style.padding = '0.75rem 1rem';
      el.style.borderBottom = '1px solid rgba(255, 255, 255, 0.06)';
    });
  },

  initAll() {
    document.querySelectorAll('.topic-comp-target, .comp-table-target').forEach(el => {
      const raw = el.getAttribute('data-comp');
      if (raw) {
        try {
          const data = JSON.parse(raw);
          this.render(el, data);
        } catch (e) {
          console.error('[ComparisonTable] Failed to parse data', e);
        }
      }
    });
  }
};

document.addEventListener('DOMContentLoaded', () => {
  ComparisonTable.initAll();
});

window.ComparisonTable = ComparisonTable;
