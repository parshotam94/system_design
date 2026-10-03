/**
 * Interactive System Flow Animation Component
 * Step-by-step request/data pipeline playback engine with live event logging
 */

class SystemFlowAnimationComponent {
  static initAll() {
    document.querySelectorAll('.topic-system-flow-target').forEach(el => {
      try {
        const rawData = el.getAttribute('data-system-flow');
        if (rawData) {
          const flowData = JSON.parse(rawData);
          SystemFlowAnimationComponent.render(el, flowData);
        }
      } catch (err) {
        console.error('[SystemFlowAnimationComponent] Error parsing data:', err);
      }
    });
  }

  static render(container, data) {
    const title = data.title || 'Interactive Request Flow Simulation';
    const steps = data.steps || [];
    let currentStepIdx = 0;
    let autoPlayTimer = null;

    let html = `
      <div class="flow-anim-container">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 1.25rem;">⚡</span>
            <h4 style="color: #fff; margin: 0; font-size: 1.1rem;">${title}</h4>
          </div>
          <div class="flow-step-badge">Step <span class="current-step-num">1</span> of ${steps.length}</div>
        </div>

        <!-- Visual Flow Nodes -->
        <div class="flow-nodes-track" style="display: flex; align-items: center; justify-content: space-around; gap: 1rem; padding: 1.5rem 0.5rem; background: var(--bg-card); border-radius: var(--radius-md); border: 1px solid rgba(255,255,255,0.06); flex-wrap: wrap;">
    `;

    // Extract unique active nodes
    const allNodesSet = new Set();
    steps.forEach(s => {
      if (s.nodes) s.nodes.forEach(n => allNodesSet.add(n));
      if (s.active_nodes) s.active_nodes.forEach(n => allNodesSet.add(n));
    });

    const uniqueNodes = Array.from(allNodesSet);
    uniqueNodes.forEach(nodeName => {
      html += `
        <div class="flow-anim-node" data-node-id="${nodeName}" style="padding: 0.75rem 1.25rem; background: var(--bg-secondary); border: 1px solid var(--glass-border); border-radius: var(--radius-md); font-size: 0.88rem; font-weight: 700; color: #fff; transition: all 0.3s ease; text-align: center; min-width: 110px;">
          ${nodeName}
        </div>
      `;
    });

    html += `
        </div>

        <!-- Live Step Log Message -->
        <div class="flow-event-log">
          <span style="color: var(--accent-cyan);">[Event Log]</span>
          <span class="flow-event-text">${steps[0] ? steps[0].description : 'Ready'}</span>
        </div>

        <!-- Animation Controls -->
        <div class="flow-anim-controls">
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <button class="btn btn-secondary btn-sm btn-flow-prev" style="cursor: pointer;">&larr; Prev</button>
            <button class="btn btn-primary btn-sm btn-flow-play" style="cursor: pointer;">▶ Play</button>
            <button class="btn btn-secondary btn-sm btn-flow-next" style="cursor: pointer;">Next &rarr;</button>
          </div>
          <button class="btn btn-outline btn-sm btn-flow-reset" style="cursor: pointer;">Reset</button>
        </div>
      </div>
    `;

    container.innerHTML = html;

    const currentStepNumEl = container.querySelector('.current-step-num');
    const eventTextEl = container.querySelector('.flow-event-text');
    const playBtn = container.querySelector('.btn-flow-play');
    const prevBtn = container.querySelector('.btn-flow-prev');
    const nextBtn = container.querySelector('.btn-flow-next');
    const resetBtn = container.querySelector('.btn-flow-reset');
    const nodeEls = container.querySelectorAll('.flow-anim-node');

    function updateStep(idx) {
      if (idx < 0 || idx >= steps.length) return;
      currentStepIdx = idx;
      currentStepNumEl.textContent = currentStepIdx + 1;

      const currentStep = steps[currentStepIdx];
      eventTextEl.textContent = currentStep.description || '';

      const activeNodes = currentStep.active_nodes || currentStep.nodes || [];
      nodeEls.forEach(nEl => {
        const nId = nEl.getAttribute('data-node-id');
        if (activeNodes.includes(nId)) {
          nEl.style.borderColor = 'var(--accent-cyan)';
          nEl.style.boxShadow = '0 0 20px rgba(56, 189, 248, 0.4)';
          nEl.style.transform = 'scale(1.06)';
          nEl.style.background = 'var(--bg-elevated)';
        } else {
          nEl.style.borderColor = 'var(--glass-border)';
          nEl.style.boxShadow = 'none';
          nEl.style.transform = 'scale(1)';
          nEl.style.background = 'var(--bg-secondary)';
        }
      });
    }

    function togglePlay() {
      if (autoPlayTimer) {
        clearInterval(autoPlayTimer);
        autoPlayTimer = null;
        playBtn.textContent = '▶ Play';
      } else {
        playBtn.textContent = '⏸ Pause';
        autoPlayTimer = setInterval(() => {
          if (currentStepIdx < steps.length - 1) {
            updateStep(currentStepIdx + 1);
          } else {
            updateStep(0); // loop
          }
        }, 2200);
      }
    }

    playBtn.addEventListener('click', togglePlay);
    prevBtn.addEventListener('click', () => {
      if (autoPlayTimer) togglePlay();
      if (currentStepIdx > 0) updateStep(currentStepIdx - 1);
    });
    nextBtn.addEventListener('click', () => {
      if (autoPlayTimer) togglePlay();
      if (currentStepIdx < steps.length - 1) updateStep(currentStepIdx + 1);
    });
    resetBtn.addEventListener('click', () => {
      if (autoPlayTimer) togglePlay();
      updateStep(0);
    });

    updateStep(0);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  SystemFlowAnimationComponent.initAll();
});

window.SystemFlowAnimationComponent = SystemFlowAnimationComponent;
