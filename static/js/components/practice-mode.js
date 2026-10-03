/**
 * Reusable "Design This Yourself" Practice Mode Component
 */

const PracticeMode = {
  render(containerEl, config) {
    // config: { title, problemStatement, requirements: [], constraints: [], hint, expectedEntities: [], referenceCode: { filename, code } }
    const { title, problemStatement, requirements = [], constraints = [], hint, expectedEntities = [], referenceCode } = config;

    const refCodeHtml = (referenceCode && window.CodeBlock) ? window.CodeBlock.highlightCpp(referenceCode.code) : (referenceCode ? referenceCode.code : '');

    containerEl.innerHTML = `
      <div class="glass-panel" style="padding: 1.75rem; margin: 2rem 0; border: 1px solid rgba(168, 85, 247, 0.4);">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
          <h4 style="color: #fff; font-size: 1.15rem; display: flex; align-items: center; gap: 0.5rem;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#a855f7" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polygon points="12 8 8 12 12 16 12 8"></polygon></svg>
            Design This Yourself: ${title || 'LLD Exercise'}
          </h4>
          <span class="badge badge-advanced">Interactive Challenge</span>
        </div>

        <p style="color: var(--text-primary); font-size: 0.98rem; margin-bottom: 1.25rem;">${problemStatement || ''}</p>

        ${requirements.length > 0 ? `
          <div style="margin-bottom: 1rem;">
            <h5 style="color: var(--accent-cyan); font-size: 0.9rem; margin-bottom: 0.5rem;">Key Requirements:</h5>
            <ul style="margin-left: 1.25rem; font-size: 0.88rem; color: var(--text-secondary);">
              ${requirements.map(r => `<li>${r}</li>`).join('')}
            </ul>
          </div>
        ` : ''}

        ${constraints.length > 0 ? `
          <div style="margin-bottom: 1.5rem;">
            <h5 style="color: var(--accent-amber); font-size: 0.9rem; margin-bottom: 0.5rem;">System Constraints:</h5>
            <ul style="margin-left: 1.25rem; font-size: 0.88rem; color: var(--text-secondary);">
              ${constraints.map(c => `<li>${c}</li>`).join('')}
            </ul>
          </div>
        ` : ''}

        <div style="display: flex; gap: 0.75rem; margin-bottom: 1.25rem; flex-wrap: wrap;">
          ${hint ? `<button class="btn btn-secondary btn-sm btn-reveal-hint">💡 Reveal Design Hint</button>` : ''}
          ${expectedEntities.length > 0 ? `<button class="btn btn-secondary btn-sm btn-reveal-entities">📋 Reveal Expected Entities</button>` : ''}
          ${referenceCode ? `<button class="btn btn-outline btn-sm btn-reveal-solution">⚡ Reveal Reference C++ Solution</button>` : ''}
        </div>

        ${hint ? `
          <div class="box-hint" style="display: none; margin-bottom: 1rem;">
            <div class="callout callout-tip">
              <div class="callout-content">
                <h5>Design Hint:</h5>
                <p>${hint}</p>
              </div>
            </div>
          </div>
        ` : ''}

        ${expectedEntities.length > 0 ? `
          <div class="box-entities" style="display: none; margin-bottom: 1rem;">
            <div class="callout callout-important">
              <div class="callout-content">
                <h5>Expected Domain Entities & Classes:</h5>
                <ul style="margin-left: 1.25rem; margin-top: 0.5rem;">
                  ${expectedEntities.map(e => `<li><strong>${e.name}</strong>: ${e.responsibility}</li>`).join('')}
                </ul>
              </div>
            </div>
          </div>
        ` : ''}

        ${referenceCode ? `
          <div class="box-solution" style="display: none; margin-top: 1.5rem;">
            <div class="code-container">
              <div class="code-header">
                <span class="code-filename">${referenceCode.filename || 'solution.cpp'}</span>
                <span class="code-lang-tag">C++20 Reference Solution</span>
              </div>
              <div class="code-body">
                <div class="code-content">${refCodeHtml}</div>
              </div>
            </div>
          </div>
        ` : ''}
      </div>
    `;

    // Hook toggle buttons
    const btnHint = containerEl.querySelector('.btn-reveal-hint');
    if (btnHint) {
      btnHint.addEventListener('click', () => {
        const box = containerEl.querySelector('.box-hint');
        box.style.display = box.style.display === 'none' ? 'block' : 'none';
        btnHint.textContent = box.style.display === 'none' ? '💡 Reveal Design Hint' : 'Hide Hint';
      });
    }

    const btnEntities = containerEl.querySelector('.btn-reveal-entities');
    if (btnEntities) {
      btnEntities.addEventListener('click', () => {
        const box = containerEl.querySelector('.box-entities');
        box.style.display = box.style.display === 'none' ? 'block' : 'none';
        btnEntities.textContent = box.style.display === 'none' ? '📋 Reveal Expected Entities' : 'Hide Entities';
      });
    }

    const btnSolution = containerEl.querySelector('.btn-reveal-solution');
    if (btnSolution) {
      btnSolution.addEventListener('click', () => {
        const box = containerEl.querySelector('.box-solution');
        box.style.display = box.style.display === 'none' ? 'block' : 'none';
        btnSolution.textContent = box.style.display === 'none' ? '⚡ Reveal Reference C++ Solution' : 'Hide Solution';
      });
    }
  }
};

window.PracticeMode = PracticeMode;
