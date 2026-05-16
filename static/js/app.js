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
      this.el.clock.textContent = new Date().toLocaleTimeString('ko-KR', {
        hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false,
      });
    };
    tick();
    setInterval(tick, 1000);
  }

  // ── Connection badge ─────────────────────────────
  _setConnection(state) {
    this.el.connBadge.className = `connection-badge ${state}`;
    const labels = { connected: '연결됨', error: '연결 끊김', loading: '연결 중...' };
    this.el.connLabel.textContent = labels[state] ?? '연결 중...';
  }

  // ── Initial skeleton render ──────────────────────
  _initTreadmills() {
    this.el.tmGrid.innerHTML = Array.from({ length: 4 }, (_, i) => `
      <div class="tm-card loading" id="tm-card-${i + 1}">
        <div class="tm-label">트레드밀 ${i + 1}번</div>
        <div class="tm-image-wrap">
          <img class="tm-bg-img" src="/static/img/trail.png" alt="">
          <img class="tm-state-img" id="tm-img-${i + 1}" src="/static/img/human.png" alt="상태">
        </div>
        <div class="tm-status-text" id="tm-txt-${i + 1}">로딩 중...</div>
        <span class="tm-indicator" id="tm-dot-${i + 1}"></span>
      </div>
    `).join('');
  }

  _initEquipment() {
    const items = [
      { id: 1, name: '벤치프레스',  icon: '🏋️' },
      { id: 2, name: '덤벨 랙',     icon: '💪' },
      { id: 3, name: '스쿼트 랙',   icon: '🏗️' },
      { id: 4, name: '레그프레스',  icon: '🦵' },
      { id: 5, name: '케이블 머신', icon: '⚙️' },
      { id: 6, name: '풀업 바',     icon: '🤸' },
    ];

    this.el.equipGrid.innerHTML = items.map(it => `
      <div class="equip-card" id="equip-card-${it.id}">
        <span class="equip-icon">${it.icon}</span>
        <div class="equip-info">
          <div class="equip-name">${it.name}</div>
          <div class="equip-status" id="equip-status-${it.id}">로딩 중...</div>
        </div>
      </div>
    `).join('');
  }

  // ── Update helpers ───────────────────────────────
  _updateTreadmills(data) {
    let inUse = 0;
    let available = 0;

    // data: { Tmn1: "/static/img/onhuman.png", ... }
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
        txt.textContent = '사용 중';
        inUse++;
      } else if (isOff) {
        card.className = 'tm-card available';
        txt.textContent = '사용 가능';
        available++;
      } else {
        card.className = 'tm-card loading';
        txt.textContent = '대기 중';
      }

      if (imgPath) img.src = imgPath;
    }

    this.el.statInUse.textContent      = inUse;
    this.el.statAvailable.textContent  = available;
    this.el.tmBadge.textContent        = `${inUse}개 사용 중 · ${available}개 가능`;
  }

  _updateTowels(data) {
    // data: { 1: { name, count, max }, ... }
    this.el.towelList.innerHTML = Object.values(data).map(st => {
      const pct   = Math.round((st.count / st.max) * 100);
      const color = pct > 60 ? 'var(--accent-green)'
                  : pct > 30 ? 'var(--accent-yellow)'
                  : 'var(--accent-red)';
      return `
        <div class="towel-item">
          <div class="towel-row">
            <span class="towel-name">${st.name}</span>
            <span class="towel-count" style="color:${color}">${st.count} / ${st.max}장</span>
          </div>
          <div class="towel-track">
            <div class="towel-fill" style="width:${pct}%; background:${color}"></div>
          </div>
        </div>
      `;
    }).join('');
  }

  _updateEquipment(data) {
    // data: [{ id, name, icon, status }, ...]
    data.forEach(eq => {
      const card   = document.getElementById(`equip-card-${eq.id}`);
      const status = document.getElementById(`equip-status-${eq.id}`);
      if (!card || !status) return;

      const isInUse = eq.status === 'in_use';
      card.className   = `equip-card ${isInUse ? 'in_use' : ''}`;
      status.className = `equip-status ${eq.status}`;
      status.textContent = isInUse ? '사용 중' : '사용 가능';
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
      this._updateTreadmills(tmData);
      this._updateTowels(towelData);
      this._updateEquipment(equipData);
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
