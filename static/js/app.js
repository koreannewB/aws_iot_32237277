
class GymDashboard {
  constructor() {
    this.pollTimer = null;
    this.POLL_INTERVAL = 1000;
 
    this.el = {
      connBadge:       document.getElementById('connBadge'),
      connLabel:       document.getElementById('connLabel'),
      clock:           document.getElementById('clock'),
      statInUse:       document.getElementById('statInUse'),
      statAvailable:   document.getElementById('statAvailable'),
      tmGrid:          document.getElementById('tmGrid'),
      tmBadge:         document.getElementById('tmBadge'),
      towelList:       document.getElementById('towelList'),
      equipGrid:       document.getElementById('equipGrid'),
    };
 
    this._initTreadmills();
    this._initEquipment();
    this._startClock();
    this._startPolling();
  }
 
  // ── Clock ────────────────────────────────────────
  _startClock() {
    const tick = () => {
      this.el.clock.textContent = new Date().toLocaleTimeString('en-US', {
        hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false,
      });
    };
    tick();
    setInterval(tick, 1000);
  }
 
  // ── Connection badge ─────────────────────────────
  _setConnection(state) {
    this.el.connBadge.className = `connection-badge ${state}`;
    const labels = { connected: 'Connected', error: 'Disconnected', loading: 'Connecting...' };
    this.el.connLabel.textContent = labels[state] ?? 'Connecting...';
  }
 
  // ── Initial skeleton render ──────────────────────
  _initTreadmills() {
    this.el.tmGrid.innerHTML = Array.from({ length: 4 }, (_, i) => `
      <div class="tm-card loading" id="tm-card-${i + 1}">
        <div class="tm-label">Treadmill ${i + 1}</div>
        <div class="tm-image-wrap">
          <img class="tm-bg-img" src="/static/img/trail.png" alt="">
          <img class="tm-state-img" id="tm-img-${i + 1}" src="/static/img/human.png" alt="status">
        </div>
        <div class="tm-status-text" id="tm-txt-${i + 1}">Loading...</div>
        <span class="tm-indicator" id="tm-dot-${i + 1}"></span>
      </div>
    `).join('');
  }
 
  _initEquipment() {
    const items = [
      { id: 1, name: 'Bench Press',   icon: '🏋️' },
      { id: 2, name: 'Dumbbell Rack', icon: '💪' },
      { id: 3, name: 'Squat Rack',    icon: '🏗️' },
      { id: 4, name: 'Leg Press',     icon: '🦵' },
      { id: 5, name: 'Cable Machine', icon: '⚙️' },
      { id: 6, name: 'Pull-up Bar',   icon: '🤸' },
    ];
 
    this.el.equipGrid.innerHTML = items.map(it => `
      <div class="equip-card" id="equip-card-${it.id}">
        <span class="equip-icon">${it.icon}</span>
        <div class="equip-info">
          <div class="equip-name">${it.name}</div>
          <div class="equip-status" id="equip-status-${it.id}">Loading...</div>
        </div>
      </div>
    `).join('');
  }
 
  // ── Update helpers ───────────────────────────────
  _updateTreadmills(data) {
    let inUse = 0;
    let available = 0;
 
    for (let i = 1; i <= 4; i++) {
      const imgPath = data[`Tmn${i}`] ?? '';
      const isInUse = imgPath.includes('onhuman');
      const isOff   = imgPath.includes('offhuman');
 
      const card = document.getElementById(`tm-card-${i}`);
      const img  = document.getElementById(`tm-img-${i}`);
      const txt  = document.getElementById(`tm-txt-${i}`);
 
      if (!card) continue;
 
      if (isInUse) {
        card.className = 'tm-card in-use';
        txt.textContent = 'In Use';
        inUse++;
      } else if (isOff) {
        card.className = 'tm-card available';
        txt.textContent = 'Available';
        available++;
      } else {
        card.className = 'tm-card loading';
        txt.textContent = 'Standby';
      }
 
      if (imgPath) img.src = imgPath;
    }
 
    this.el.statInUse.textContent     = inUse;
    this.el.statAvailable.textContent = available;
    this.el.tmBadge.textContent       = `${inUse} in use · ${available} available`;
  }
 
  _updateTowels(data) {
    this.el.towelList.innerHTML = Object.values(data).map(st => {
      // 1. NaN(에러) 방지: max 값이 0이거나 없을 경우 기본값 1 부여
      const safeMax = (st.max && st.max > 0) ? st.max : 1;
      
      // 2. UI 깨짐 방지: 표시되는 수건 숫자가 0 ~ max 사이를 벗어나지 않도록 강제 고정
      const safeCount = Math.max(0, Math.min(safeMax, st.count));
      
      // 3. 그래프 너비 고정: 백분율을 무조건 0% ~ 100% 사이로 제한
      let pct = Math.round((safeCount / safeMax) * 100);
      pct = Math.max(0, Math.min(100, pct)); 

      // 4. 색상 표시 기준 (원하시는 알림 기준에 맞춰 숫자를 조절하셔도 좋습니다)
      const color = pct > 60 ? 'var(--accent-green)'   // 60% 초과면 초록색 (여유)
                  : pct > 30 ? 'var(--accent-yellow)'  // 30% 초과면 노란색 (주의)
                  : 'var(--accent-red)';               // 30% 이하면 빨간색 (부족)
                  
      return `
        <div class="towel-item">
          <div class="towel-row">
            <span class="towel-name">${st.name}</span>
            <span class="towel-count" style="color:${color}">${safeCount} / ${safeMax}</span>
          </div>
          <div class="towel-track">
            <div class="towel-fill" style="width:${pct}%; background:${color}"></div>
          </div>
        </div>
      `;
    }).join('');
  } 
 
  _updateEquipment(data) {
    data.forEach(eq => {
      const card   = document.getElementById(`equip-card-${eq.id}`);
      const status = document.getElementById(`equip-status-${eq.id}`);
      if (!card || !status) return;
 
      const isInUse = eq.status === 'in_use';
      card.className   = `equip-card ${isInUse ? 'in_use' : ''}`;
      status.className = `equip-status ${eq.status}`;
      status.textContent = isInUse ? 'In Use' : 'Available';
    });
  }
 
  // ── Polling ──────────────────────────────────────
  async _fetchAll() {
    try {
      const [tmData, towelData, equipData] = await Promise.all([
        API.getTreadmillData(),
        API.getTowelData(),
        API.getEquipmentData(),
      ]);
 
      this._setConnection('connected');
      if (tmData)    this._updateTreadmills(tmData);
      if (towelData) this._updateTowels(towelData);
      if (equipData) this._updateEquipment(equipData);
    } catch (err) {
      console.warn('[GymDashboard] fetch error:', err.message);
      this._setConnection('error');
    }
  }
 
  _startPolling() {
    this._fetchAll();
    this.pollTimer = setInterval(() => this._fetchAll(), this.POLL_INTERVAL);
  }
}
 
document.addEventListener('DOMContentLoaded', () => {
  window.dashboard = new GymDashboard();
});