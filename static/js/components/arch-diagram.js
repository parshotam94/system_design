/**
 * Interactive HLD Architecture Diagram Component
 * Renders layered system nodes with live hover/click inspection tooltips
 */

class ArchDiagramComponent {
  static initAll() {
    document.querySelectorAll('.topic-arch-diagram-target').forEach(el => {
      try {
        const rawData = el.getAttribute('data-arch-diagram');
        if (rawData) {
          const diagramData = JSON.parse(rawData);
          ArchDiagramComponent.render(el, diagramData);
        }
      } catch (err) {
        console.error('[ArchDiagramComponent] Error parsing diagram data:', err);
      }
    });
  }

  static render(container, data) {
    const title = data.title || 'System Architecture Diagram';
    const tiers = data.tiers || [];
    const inspectorId = `inspector-${Math.random().toString(36).substr(2, 9)}`;

    let html = `
      <div class="arch-diagram-wrapper">
        <div class="arch-diagram-header">
          <div class="arch-diagram-title">
            <span>🏛️</span>
            <span>${title}</span>
          </div>
          <span class="badge badge-cpp">Interactive &bull; Click any node to inspect</span>
        </div>

        <div class="arch-canvas-container">
    `;

    tiers.forEach((tier, tIdx) => {
      html += `<div class="arch-tier">`;
      if (tier.label) {
        html += `<div class="arch-tier-label">${tier.label}</div>`;
      }

      tier.nodes.forEach(node => {
        const nodeJson = encodeURIComponent(JSON.stringify(node));
        html += `
          <div class="arch-node" data-type="${node.type || 'service'}" data-node-info="${nodeJson}">
            <span class="arch-node-icon">${node.icon || '📦'}</span>
            <div class="arch-node-name">${node.name}</div>
            <div class="arch-node-sub">${node.sub || node.type || ''}</div>
          </div>
        `;
      });

      html += `</div>`;

      if (tIdx < tiers.length - 1) {
        html += `
          <div class="arch-connector-down">
            <span>↓</span>
          </div>
        `;
      }
    });

    html += `
        </div>

        <!-- Node Inspector Drawer -->
        <div class="arch-node-inspector" id="${inspectorId}">
          <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 0.75rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <span class="inspector-icon" style="font-size: 1.5rem;">📦</span>
              <h4 class="inspector-name" style="color: #fff; font-size: 1.1rem; margin: 0;">Component Name</h4>
            </div>
            <span class="badge badge-intermediate inspector-type">Service</span>
          </div>

          <div class="inspector-grid">
            <div class="inspector-item">
              <div class="inspector-item-title">What is it?</div>
              <div class="inspector-item-desc inspector-what">-</div>
            </div>
            <div class="inspector-item">
              <div class="inspector-item-title">Why we need it?</div>
              <div class="inspector-item-desc inspector-why">-</div>
            </div>
            <div class="inspector-item">
              <div class="inspector-item-title">When to use</div>
              <div class="inspector-item-desc inspector-when">-</div>
            </div>
            <div class="inspector-item">
              <div class="inspector-item-title">Failure Scenarios</div>
              <div class="inspector-item-desc inspector-failure">-</div>
            </div>
          </div>
        </div>
      </div>
    `;

    container.innerHTML = html;

    // Attach click listeners to nodes
    const inspectorEl = container.querySelector(`#${inspectorId}`);
    container.querySelectorAll('.arch-node').forEach(nodeEl => {
      nodeEl.addEventListener('click', () => {
        container.querySelectorAll('.arch-node').forEach(n => n.classList.remove('active-pulse'));
        nodeEl.classList.add('active-pulse');

        const rawInfo = decodeURIComponent(nodeEl.getAttribute('data-node-info'));
        try {
          const info = JSON.parse(rawInfo);
          inspectorEl.querySelector('.inspector-icon').textContent = info.icon || '📦';
          inspectorEl.querySelector('.inspector-name').textContent = info.name || 'Component';
          inspectorEl.querySelector('.inspector-type').textContent = info.type || 'Infrastructure';
          inspectorEl.querySelector('.inspector-what').textContent = info.what || 'Core architectural building block.';
          inspectorEl.querySelector('.inspector-why').textContent = info.why || 'Solves scalability, decoupling, or durability needs.';
          inspectorEl.querySelector('.inspector-when').textContent = info.when || 'When traffic, storage, or concurrency exceeds single-server limits.';
          inspectorEl.querySelector('.inspector-failure').textContent = info.failure || 'Failover to standby replica or return degraded fallback.';
          inspectorEl.classList.add('visible');
          inspectorEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        } catch (e) {
          console.error(e);
        }
      });
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  ArchDiagramComponent.initAll();
});

window.ArchDiagramComponent = ArchDiagramComponent;
