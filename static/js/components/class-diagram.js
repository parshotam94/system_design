/**
 * Reusable Interactive UML Class Diagram Component
 */

const ClassDiagram = {
  render(containerEl, data) {
    // data: { title, classes: [{ name, stereotype, isInterface, attributes: [], methods: [] }], relationships: [{ from, to, type, label, ownership, lifetime, coupling, cppSyntax }] }
    const { title, classes = [], relationships = [] } = data;

    let classesHtml = classes.map(c => `
      <div class="uml-class-box ${c.isInterface ? 'interface' : ''}">
        <div class="uml-header">
          ${c.stereotype ? `<div class="uml-stereotype">&laquo;${c.stereotype}&raquo;</div>` : ''}
          <div class="uml-class-name">${c.name}</div>
        </div>
        ${c.attributes && c.attributes.length > 0 ? `
          <div class="uml-section">
            ${c.attributes.map(attr => `
              <div class="uml-member">
                <span class="uml-vis-${attr.visibility === '+' ? 'public' : (attr.visibility === '-' ? 'private' : 'protected')}">${attr.visibility}</span>
                <span>${attr.name}: ${attr.type}</span>
              </div>
            `).join('')}
          </div>
        ` : ''}
        ${c.methods && c.methods.length > 0 ? `
          <div class="uml-section">
            ${c.methods.map(m => `
              <div class="uml-member">
                <span class="uml-vis-${m.visibility === '+' ? 'public' : (m.visibility === '-' ? 'private' : 'protected')}">${m.visibility}</span>
                <span>${m.name}(${m.params || ''}): ${m.returnType || 'void'}</span>
              </div>
            `).join('')}
          </div>
        ` : ''}
      </div>
    `).join('');

    let relationHtml = relationships.map(rel => {
      let arrowSymbol = '──>';
      if (rel.type === 'inheritance') arrowSymbol = '──▷';
      if (rel.type === 'composition') arrowSymbol = '──◆';
      if (rel.type === 'aggregation') arrowSymbol = '──◇';
      if (rel.type === 'dependency') arrowSymbol = '..>';

      return `
        <div class="uml-relation-connector">
          <span class="relation-label">${rel.label || rel.type}</span>
          <span class="relation-arrow-art">${arrowSymbol}</span>
          <div class="relation-inspect-card">
            <div class="inspect-header">${rel.type.toUpperCase()} RELATIONSHIP</div>
            <div class="inspect-row">
              <span class="inspect-key">Ownership:</span>
              <span class="inspect-val">${rel.ownership || 'None'}</span>
            </div>
            <div class="inspect-row">
              <span class="inspect-key">Lifetime:</span>
              <span class="inspect-val">${rel.lifetime || 'Independent'}</span>
            </div>
            <div class="inspect-row">
              <span class="inspect-key">Coupling:</span>
              <span class="inspect-val">${rel.coupling || 'Moderate'}</span>
            </div>
            ${rel.cppSyntax ? `
              <div class="inspect-code">${rel.cppSyntax}</div>
            ` : ''}
          </div>
        </div>
      `;
    }).join('');

    containerEl.innerHTML = `
      <div class="diagram-wrapper">
        <div class="diagram-header">
          <div class="diagram-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 20V10"></path><path d="M12 20V4"></path><path d="M6 20v-6"></path></svg>
            ${title || 'UML Class Diagram'}
          </div>
          <div class="diagram-legend">
            <span class="legend-item"><span class="legend-symbol">+</span> Public</span>
            <span class="legend-item"><span class="legend-symbol">-</span> Private</span>
            <span class="legend-item"><span class="legend-symbol">#</span> Protected</span>
            <span class="legend-item"><span class="legend-symbol">──◆</span> Composition</span>
            <span class="legend-item"><span class="legend-symbol">──◇</span> Aggregation</span>
            <span class="legend-item"><span class="legend-symbol">──▷</span> Inheritance</span>
          </div>
        </div>
        <div class="diagram-canvas">
          ${classesHtml}
          ${relationHtml}
        </div>
      </div>
    `;
  }
};

window.ClassDiagram = ClassDiagram;
