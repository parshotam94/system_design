/**
 * Interactive Back-of-the-Envelope Capacity Estimator Component
 * Computes QPS, Peak QPS, Ingress/Egress Bandwidth, Storage growth & Cache sizing in real time
 */

class CapacityCalculatorComponent {
  static initAll() {
    document.querySelectorAll('.topic-capacity-calc-target').forEach(el => {
      CapacityCalculatorComponent.render(el);
    });
  }

  static render(container) {
    container.innerHTML = `
      <div class="capacity-calc-widget">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 1rem;">
          <div>
            <h3 style="color: #fff; margin: 0; font-size: 1.3rem; display: flex; align-items: center; gap: 0.5rem;">
              <span>🧮</span>
              <span>Interactive Back-of-the-Envelope Capacity Estimator</span>
            </h3>
            <p style="color: var(--text-secondary); font-size: 0.88rem; margin: 0.35rem 0 0;">
              Adjust the sliders below to calculate real-world system resource requirements live.
            </p>
          </div>
          <span class="badge badge-cpp">Dynamic Formula Engine</span>
        </div>

        <div class="calc-grid">
          <!-- Input Sliders Column -->
          <div>
            <div class="calc-input-group">
              <label>
                <span>Daily Active Users (DAU):</span>
                <span id="val-dau" style="color: var(--accent-cyan); font-family: var(--font-mono); font-weight: 700;">10,000,000</span>
              </label>
              <input type="range" id="input-dau" min="100000" max="100000000" step="500000" value="10000000">
            </div>

            <div class="calc-input-group">
              <label>
                <span>Reads per User / Day:</span>
                <span id="val-reads" style="color: var(--accent-cyan); font-family: var(--font-mono); font-weight: 700;">20</span>
              </label>
              <input type="range" id="input-reads" min="1" max="200" step="1" value="20">
            </div>

            <div class="calc-input-group">
              <label>
                <span>Writes per User / Day:</span>
                <span id="val-writes" style="color: var(--accent-cyan); font-family: var(--font-mono); font-weight: 700;">2</span>
              </label>
              <input type="range" id="input-writes" min="1" max="50" step="1" value="2">
            </div>

            <div class="calc-input-group">
              <label>
                <span>Average Payload Size (KB):</span>
                <span id="val-size" style="color: var(--accent-cyan); font-family: var(--font-mono); font-weight: 700;">100 KB</span>
              </label>
              <input type="range" id="input-size" min="1" max="2000" step="10" value="100">
            </div>

            <div class="calc-input-group">
              <label>
                <span>Peak Traffic Multiplier:</span>
                <span id="val-peak" style="color: var(--accent-cyan); font-family: var(--font-mono); font-weight: 700;">2.5x</span>
              </label>
              <input type="range" id="input-peak" min="1.0" max="5.0" step="0.5" value="2.5">
            </div>
          </div>

          <!-- Calculated Output Card -->
          <div class="calc-output-card">
            <h4 style="color: #fff; margin: 0 0 0.5rem; font-size: 1.05rem; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 0.5rem;">
              Estimated System Scale
            </h4>

            <div class="calc-result-row">
              <div>
                <div style="font-size: 0.78rem; color: var(--text-muted); text-transform: uppercase;">Average Read QPS</div>
                <div style="font-size: 0.72rem; color: var(--text-muted);">(DAU &times; Reads / 86,400s)</div>
              </div>
              <div class="calc-result-val" id="res-read-qps">2,314 QPS</div>
            </div>

            <div class="calc-result-row">
              <div>
                <div style="font-size: 0.78rem; color: var(--text-muted); text-transform: uppercase;">Peak Read QPS</div>
                <div style="font-size: 0.72rem; color: var(--text-muted);">(Avg QPS &times; Peak Multiplier)</div>
              </div>
              <div class="calc-result-val" id="res-peak-read-qps" style="color: #f59e0b;">5,785 QPS</div>
            </div>

            <div class="calc-result-row">
              <div>
                <div style="font-size: 0.78rem; color: var(--text-muted); text-transform: uppercase;">Average Write QPS</div>
                <div style="font-size: 0.72rem; color: var(--text-muted);">(DAU &times; Writes / 86,400s)</div>
              </div>
              <div class="calc-result-val" id="res-write-qps">231 QPS</div>
            </div>

            <div class="calc-result-row">
              <div>
                <div style="font-size: 0.78rem; color: var(--text-muted); text-transform: uppercase;">Daily Storage Ingestion</div>
                <div style="font-size: 0.72rem; color: var(--text-muted);">(Writes &times; Payload Size)</div>
              </div>
              <div class="calc-result-val" id="res-daily-storage">2.00 TB / day</div>
            </div>

            <div class="calc-result-row">
              <div>
                <div style="font-size: 0.78rem; color: var(--text-muted); text-transform: uppercase;">5-Year Storage (3x Replica)</div>
                <div style="font-size: 0.72rem; color: var(--text-muted);">(Daily &times; 365 &times; 5 &times; 3)</div>
              </div>
              <div class="calc-result-val" id="res-5yr-storage" style="color: #a855f7;">10.95 PB</div>
            </div>

            <div class="calc-result-row">
              <div>
                <div style="font-size: 0.78rem; color: var(--text-muted); text-transform: uppercase;">80/20 RAM Cache Sizing</div>
                <div style="font-size: 0.72rem; color: var(--text-muted);">(20% of Daily Volume)</div>
              </div>
              <div class="calc-result-val" id="res-cache-ram" style="color: #10b981;">400 GB RAM</div>
            </div>
          </div>
        </div>
      </div>
    `;

    const inDau = container.querySelector('#input-dau');
    const inReads = container.querySelector('#input-reads');
    const inWrites = container.querySelector('#input-writes');
    const inSize = container.querySelector('#input-size');
    const inPeak = container.querySelector('#input-peak');

    const vDau = container.querySelector('#val-dau');
    const vReads = container.querySelector('#val-reads');
    const vWrites = container.querySelector('#val-writes');
    const vSize = container.querySelector('#val-size');
    const vPeak = container.querySelector('#val-peak');

    const resReadQps = container.querySelector('#res-read-qps');
    const resPeakReadQps = container.querySelector('#res-peak-read-qps');
    const resWriteQps = container.querySelector('#res-write-qps');
    const resDailyStorage = container.querySelector('#res-daily-storage');
    const res5yrStorage = container.querySelector('#res-5yr-storage');
    const resCacheRam = container.querySelector('#res-cache-ram');

    function calculate() {
      const dau = parseFloat(inDau.value);
      const reads = parseFloat(inReads.value);
      const writes = parseFloat(inWrites.value);
      const sizeKB = parseFloat(inSize.value);
      const peak = parseFloat(inPeak.value);

      vDau.textContent = dau.toLocaleString();
      vReads.textContent = reads.toLocaleString();
      vWrites.textContent = writes.toLocaleString();
      vSize.textContent = `${sizeKB} KB`;
      vPeak.textContent = `${peak}x`;

      const SECONDS_PER_DAY = 86400;

      // QPS
      const avgReadQps = Math.round((dau * reads) / SECONDS_PER_DAY);
      const peakReadQps = Math.round(avgReadQps * peak);
      const avgWriteQps = Math.round((dau * writes) / SECONDS_PER_DAY);

      // Storage
      const dailyBytes = dau * writes * sizeKB * 1024;
      const dailyTB = dailyBytes / (1024 ** 4);
      const fiveYrPB = (dailyTB * 365 * 5 * 3) / 1024; // 3x replica in PB

      // Cache: 20% of daily read requests payload volume
      const dailyReadBytes = dau * reads * sizeKB * 1024;
      const cacheGB = (dailyReadBytes * 0.20) / (1024 ** 3);

      resReadQps.textContent = `${avgReadQps.toLocaleString()} QPS`;
      resPeakReadQps.textContent = `${peakReadQps.toLocaleString()} QPS`;
      resWriteQps.textContent = `${avgWriteQps.toLocaleString()} QPS`;

      if (dailyTB >= 1) {
        resDailyStorage.textContent = `${dailyTB.toFixed(2)} TB / day`;
      } else {
        resDailyStorage.textContent = `${(dailyTB * 1024).toFixed(1)} GB / day`;
      }

      if (fiveYrPB >= 1) {
        res5yrStorage.textContent = `${fiveYrPB.toFixed(2)} PB`;
      } else {
        res5yrStorage.textContent = `${(fiveYrPB * 1024).toFixed(1)} TB`;
      }

      if (cacheGB >= 1000) {
        resCacheRam.textContent = `${(cacheGB / 1024).toFixed(2)} TB RAM`;
      } else {
        resCacheRam.textContent = `${cacheGB.toFixed(0)} GB RAM`;
      }
    }

    [inDau, inReads, inWrites, inSize, inPeak].forEach(input => {
      input.addEventListener('input', calculate);
    });

    calculate();
  }
}

document.addEventListener('DOMContentLoaded', () => {
  CapacityCalculatorComponent.initAll();
});

window.CapacityCalculatorComponent = CapacityCalculatorComponent;
