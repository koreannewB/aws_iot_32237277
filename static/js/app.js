class GymDashboard {
  constructor() {
    this.pollTimer = null;
    this.POLL_INTERVAL = 1000;
    this.treadmillUsageTimes = ['24:12', '', '12:45', ''];
    this.equipmentDefaults = [
      { id: 1, name: '벤치 프레스 01', icon: '▣' },
      { id: 2, name: '덤벨 랙 A', icon: '▦' },
      { id: 3, name: '레그 프레스', icon: '↻' },
      { id: 4, name: '케이블 머신', icon: '↻' },
      { id: 5, name: '풀업 스테이션', icon: '━' },
      { id: 6, name: '런닝머신 02', icon: '↻' },
    ];

    this.el = {
      connBadge: document.getElementById('connBadge'),
      connLabel: document.getElementById('connLabel'),
      clock: document.getElementById('clock'),
      statTotal: document.getElementById('statTotal'),
      statInUse: document.getElementById('statInUse'),
      statAvailable: document.getElementById('statAvailable'),
      tmGrid: document.getElementById('tmGrid'),
      tmBadge: document.getElementById('tmBadge'),
      towelList: document.getElementById('towelList'),
      equipGrid: document.getElementById('equipGrid'),
    };

    this._initTreadmills();
    this._initEquipment();
    this._startClock();
    this._startPolling();
  }

  _escapeHTML(value) {
    return String(value ?? '').replace(/[&<>"']/g, char => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;',
    }[char]));
  }

  _startClock() {
    const tick = () => {
      this.el.clock.textContent = new Date().toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
      });
    };
    tick();
    setInterval(tick, 1000);
  }

  _setConnection(state) {
    this.el.connBadge.className = `connection-badge ${state}`;
    const labels = {
      connected: '시스템 정상',
      error: '연결 점검',
      loading: '시스템 확인 중',
    };
    this.el.connLabel.textContent = labels[state] ?? labels.loading;
  }

  _machineIcon() {
    return `
      <svg class="machine-icon" viewBox="0 0 64 64" aria-hidden="true" focusable="false">
        <path class="machine-line machine-belt" d="M10 47h31c6.4 0 10.8-3 13-9" />
        <path class="machine-line" d="M16 42h22" />
        <path class="machine-line" d="M50 23h7v13" />
        <path class="machine-line" d="M50 24l-8 17" />
        <circle class="machine-head" cx="31" cy="18" r="4.4" />
        <path class="machine-line" d="M27 27l8 5 7-5" />
        <path class="machine-line" d="M35 32l-6 8" />
        <path class="machine-line" d="M29 40l-11-3" />
        <path class="machine-line" d="M27 27l-8 8" />
      </svg>
    `;
  }

  _initTreadmills() {
    this.el.tmGrid.innerHTML = Array.from({ length: 4 }, (_, index) => {
      const id = index + 1;
      return `
        <article class="tm-card loading" id="tm-card-${id}">
          <div class="tm-card-head">
            <span class="tm-name">런닝머신 ${String(id).padStart(2, '0')}</span>
            <span class="tm-chip" id="tm-chip-${id}">확인 중</span>
          </div>
          <div class="tm-figure">
            ${this._machineIcon()}
          </div>
          <div class="tm-meta">
            <span class="tm-meta-label" id="tm-meta-label-${id}">상태</span>
            <strong class="tm-status-text" id="tm-txt-${id}">연결 중</strong>
          </div>
        </article>
      `;
    }).join('');
  }

  _initEquipment() {
    this.el.equipGrid.innerHTML = this.equipmentDefaults.map(item => `
      <article class="equip-card loading" id="equip-card-${item.id}">
        <span class="equip-icon">${item.icon}</span>
        <div class="equip-info">
          <div class="equip-name">${this._escapeHTML(item.name)}</div>
          <div class="equip-status" id="equip-status-${item.id}">연결 중...</div>
        </div>
      </article>
    `).join('');
  }

  _updateTreadmills(data) {
    let inUse = 0;
    let available = 0;

    for (let id = 1; id <= 4; id++) {
      const imgPath = data[`Tmn${id}`] ?? '';
      const isInUse = imgPath.includes('onhuman');
      const isOff = imgPath.includes('offhuman');
      const state = isInUse ? 'in-use' : isOff ? 'available' : 'loading';

      const card = document.getElementById(`tm-card-${id}`);
      const chip = document.getElementById(`tm-chip-${id}`);
      const label = document.getElementById(`tm-meta-label-${id}`);
      const text = document.getElementById(`tm-txt-${id}`);
      if (!card || !chip || !label || !text) continue;

      card.className = `tm-card ${state}`;

      if (isInUse) {
        chip.textContent = '사용 중';
        label.textContent = '사용 시간';
        text.textContent = this.treadmillUsageTimes[id - 1] || '12:00';
        inUse++;
      } else if (isOff) {
        chip.textContent = '대기 중';
        label.textContent = '상태';
        text.textContent = '사용 가능';
        available++;
      } else {
        chip.textContent = '확인 중';
        label.textContent = '상태';
        text.textContent = '연결 중';
      }
    }

    this.el.statTotal.textContent = '4 대';
    this.el.statInUse.textContent = `${inUse} 대`;
    this.el.statAvailable.textContent = `${available} 대`;
    this.el.tmBadge.innerHTML = `
      <span class="badge-dot orange"></span>사용중 ${inUse}
      <span class="badge-dot green"></span>대기중 ${available}
    `;
  }

  _towelColor(percent) {
    const pct = Math.max(0, Math.min(100, percent));
    const hue = pct < 50
      ? Math.round((pct / 50) * 48)
      : Math.round(48 + ((pct - 50) / 50) * 92);
    return `hsl(${hue} 74% 55%)`;
  }

  _towelLabel(percent) {
    if (percent >= 70) return '충분';
    if (percent >= 35) return '보통';
    return '부족';
  }

  _updateTowels(data) {
    const towels = Object.values(data ?? {});
    this.el.towelList.innerHTML = towels.map((station, index) => {
      const max = Number(station.max) > 0 ? Number(station.max) : 1;
      const count = Math.max(0, Math.min(max, Number(station.count) || 0));
      const percent = Math.round((count / max) * 100);
      const color = this._towelColor(percent);
      const label = this._towelLabel(percent);
      const fallbackName = `디스펜서 ${String(index + 1).padStart(2, '0')}`;
      const name = this._escapeHTML(station.name || fallbackName);

      return `
        <article class="towel-item" style="--level-color:${color}; --level-pct:${percent}%;">
          <div class="towel-row">
            <div>
              <span class="towel-name">${name}</span>
              <span class="towel-state">${label}</span>
            </div>
            <strong class="towel-percent">${percent}%</strong>
          </div>
          <div class="towel-track" aria-label="${name} 잔량 ${percent}%">
            <div class="towel-fill"></div>
          </div>
        </article>
      `;
    }).join('');
  }

  _updateEquipment(data) {
    const byId = new Map((data ?? []).map(item => [Number(item.id), item]));

    this.equipmentDefaults.forEach(defaultItem => {
      const equipment = byId.get(defaultItem.id);
      const card = document.getElementById(`equip-card-${defaultItem.id}`);
      const status = document.getElementById(`equip-status-${defaultItem.id}`);
      if (!card || !status) return;

      if (!equipment) {
        card.className = 'equip-card loading';
        status.className = 'equip-status loading';
        status.textContent = '연결 중...';
        return;
      }

      const isInUse = equipment.status === 'in_use' || equipment.in_use === 1;
      card.className = `equip-card ${isInUse ? 'in_use' : 'available'}`;
      status.className = `equip-status ${isInUse ? 'in_use' : 'available'}`;
      status.textContent = isInUse ? '사용 중' : '대기 중';
    });
  }

  async _fetchAll() {
    const [tmData, towelData, equipData] = await Promise.all([
      API.getTreadmillData(),
      API.getTowelData(),
      API.getEquipmentData(),
    ]);

    this._setConnection(tmData && towelData && equipData ? 'connected' : 'error');
    if (tmData) this._updateTreadmills(tmData);
    if (towelData) this._updateTowels(towelData);
    if (equipData) this._updateEquipment(equipData);
  }

  _startPolling() {
    this._fetchAll();
    this.pollTimer = setInterval(() => this._fetchAll(), this.POLL_INTERVAL);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.dashboard = new GymDashboard();
});
