/**
 * Reusable Code Refactoring Component (Before vs After)
 */

const RefactorMode = {
  render(containerEl, config) {
    // config: { title, problemSummary, violations: [], badCode: { filename, code }, goodCode: { filename, code }, benefits: [] }
    const { title, problemSummary, violations = [], badCode, goodCode, benefits = [] } = config;

    const badCodeHtml = window.CodeBlock ? window.CodeBlock.highlightCpp(badCode.code) : badCode.code;
    const goodCodeHtml = window.CodeBlock ? window.CodeBlock.highlightCpp(goodCode.code) : goodCode.code;

    containerEl.innerHTML = `
      <div class="glass-panel" style="padding: 1.75rem; margin: 2rem 0;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
          <h4 style="color: #fff; font-size: 1.15rem; display: flex; align-items: center; gap: 0.5rem;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f43f5e" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
            Refactoring Challenge: ${title || 'Code Smell & Refactor'}
          </h4>
        </div>
        
        <p style="color: var(--text-secondary); margin-bottom: 1rem;">${problemSummary || ''}</p>

        ${violations.length > 0 ? `
          <div class="callout callout-trap" style="margin: 1rem 0;">
            <div class="callout-content">
              <h5>Design Smells & Violations:</h5>
              <ul style="margin-left: 1.25rem; font-size: 0.9rem; color: #fb7185;">
                ${violations.map(v => `<li>${v}</li>`).join('')}
              </ul>
            </div>
          </div>
        ` : ''}

        <div class="refactor-diff-grid">
          <div class="refactor-panel bad">
            <div class="refactor-panel-header">
              <span>❌ BAD DESIGN (Violates Principles)</span>
              <span>${badCode.filename || 'bad_design.cpp'}</span>
            </div>
            <div class="code-body">
              <div class="code-content">${badCodeHtml}</div>
            </div>
          </div>

          <div class="refactor-panel good">
            <div class="refactor-panel-header">
              <span>✓ REFACTORED DESIGN (Clean C++ Architecture)</span>
              <span>${goodCode.filename || 'clean_design.cpp'}</span>
            </div>
            <div class="code-body">
              <div class="code-content">${goodCodeHtml}</div>
            </div>
          </div>
        </div>

        ${benefits.length > 0 ? `
          <div class="callout callout-tip" style="margin-top: 1rem;">
            <div class="callout-content">
              <h5>Why This Refactored Design Wins:</h5>
              <ul style="margin-left: 1.25rem; font-size: 0.9rem; color: #34d399;">
                ${benefits.map(b => `<li>${b}</li>`).join('')}
              </ul>
            </div>
          </div>
        ` : ''}
      </div>
    `;
  }
};

window.RefactorMode = RefactorMode;
