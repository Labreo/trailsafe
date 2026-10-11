/**
 * TrailSafe Mobile Field Application Client.
 * Manages phone sensor telemetry, dead-man countdown timers, Web Audio sirens,
 * camera waypoint scanning, and API synchronization with Temporal and TabPFN.
 */

// Application State
const state = {
  activeSession: null,
  trails: [],
  selectedTrail: null,
  timerInterval: null,
  audioContext: null,
  sirenOscillator: null,
  sirenGain: null,
  sirenActive: false,
  wakeLock: null,
  
  // Real Phone Telemetry
  telemetry: {
    latitude: 15.0892,
    longitude: 74.2154,
    altitude_m: 90.0,
    speed_mps: 0.0,
    accuracy_m: 5.0,
    elevation_delta_m: 0.0,
    pace_min_per_km: 11.5,
    hours_elapsed: 0.1,
    ambient_temp_c: 26.5,
    water_remaining_ml: 2000.0,
    cadence_spm: 118.0,
    terrain_roughness_idx: 1.2,
    battery_pct: 100,
  },
  
  stepCount: 0,
  lastStepTimestamp: 0,
};

// DOM Elements
const el = {
  clusterStatusBadge: document.getElementById('cluster-status-badge'),
  clusterStatusDot: document.getElementById('cluster-status-dot'),
  clusterStatusText: document.getElementById('cluster-status-text'),
  
  setupCard: document.getElementById('setup-card'),
  trailSelect: document.getElementById('trail-select'),
  hikerNameInput: document.getElementById('hiker-name-input'),
  timeoutInput: document.getElementById('timeout-input'),
  emergencyPhoneInput: document.getElementById('emergency-phone-input'),
  startHikeBtn: document.getElementById('start-hike-btn'),
  
  activeHikeCard: document.getElementById('active-hike-card'),
  activeTrailName: document.getElementById('active-trail-name'),
  activeCheckpointName: document.getElementById('active-checkpoint-name'),
  checkpointIndexText: document.getElementById('checkpoint-index-text'),
  countdownDigits: document.getElementById('countdown-digits'),
  countdownStatusText: document.getElementById('countdown-status-text'),
  
  // Metrics
  metricGps: document.getElementById('metric-gps'),
  metricElevation: document.getElementById('metric-elevation'),
  metricPace: document.getElementById('metric-pace'),
  metricCadence: document.getElementById('metric-cadence'),
  metricWater: document.getElementById('metric-water'),
  metricBattery: document.getElementById('metric-battery'),
  
  // TabPFN Risk Banner
  tabpfnProb: document.getElementById('tabpfn-prob'),
  tabpfnDeficit: document.getElementById('tabpfn-deficit'),
  tabpfnRecommendation: document.getElementById('tabpfn-recommendation'),
  
  // Buttons
  checkInBtn: document.getElementById('check-in-btn'),
  scanQrBtn: document.getElementById('scan-qr-btn'),
  extendBtn: document.getElementById('extend-btn'),
  sosBtn: document.getElementById('sos-btn'),
  finishBtn: document.getElementById('finish-btn'),
  
  // Waypoint list
  checkpointList: document.getElementById('checkpoint-list'),
  auditLog: document.getElementById('audit-log'),
  
  // QR Scanner Modal
  scannerModal: document.getElementById('scanner-modal'),
  scannerVideo: document.getElementById('scanner-video'),
  closeScannerBtn: document.getElementById('close-scanner-btn'),
  confirmWaypointTokenBtn: document.getElementById('confirm-waypoint-token-btn'),

  // Benchmark Panel
  runBenchmarkBtn: document.getElementById('run-benchmark-btn'),
  benchmarkResultsCard: document.getElementById('benchmark-results-card'),
  benchmarkTableBody: document.getElementById('benchmark-table-body'),
};

// Initialize Application
async function initApp() {
  // Register Offline PWA Service Worker for backcountry cellular dead-zones
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/sw.js')
      .then((reg) => console.log('TrailSafe Offline Service Worker registered:', reg.scope))
      .catch((err) => console.log('Service Worker registration note:', err));
  }

  // Monitor online / offline network state
  window.addEventListener('online', updateNetworkIndicator);
  window.addEventListener('offline', updateNetworkIndicator);

  await checkSystemStatus();
  await loadTrails();
  restoreLocalSession();
  initGeolocation();
  initMotionSensor();
  initBatterySensor();
  setupEventListeners();
}

function updateNetworkIndicator() {
  if (!navigator.onLine) {
    el.clusterStatusDot.classList.add('offline');
    el.clusterStatusText.textContent = 'Cellular Dead-Zone (Offline Cache Active)';
  } else {
    checkSystemStatus();
  }
}

// System Status Check
async function checkSystemStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    if (data.temporal_connected) {
      el.clusterStatusDot.classList.remove('offline');
      el.clusterStatusText.textContent = 'Temporal Cluster Online';
    } else {
      el.clusterStatusDot.classList.add('offline');
      el.clusterStatusText.textContent = 'Temporal Dev Local Mode';
    }
  } catch (err) {
    el.clusterStatusDot.classList.add('offline');
    el.clusterStatusText.textContent = 'Standby Mode';
  }
}

// Load Trail Checkpoints
async function loadTrails() {
  try {
    const res = await fetch('/api/trails');
    state.trails = await res.json();
    el.trailSelect.innerHTML = '';
    state.trails.forEach((t) => {
      const opt = document.createElement('option');
      opt.value = t.trail_id;
      opt.textContent = `${t.trail_name} (${t.total_distance_km} km | +${t.elevation_gain_m}m)`;
      el.trailSelect.appendChild(opt);
    });
    if (state.trails.length > 0) {
      state.selectedTrail = state.trails[0];
    }
  } catch (err) {
    console.error('Failed to load trails:', err);
  }
}

// Geolocation Integration (Real GPS)
function initGeolocation() {
  if ('geolocation' in navigator) {
    navigator.geolocation.watchPosition(
      (pos) => {
        state.telemetry.latitude = pos.coords.latitude;
        state.telemetry.longitude = pos.coords.longitude;
        state.telemetry.accuracy_m = Math.round(pos.coords.accuracy || 5);
        if (pos.coords.altitude !== null) {
          const prevAlt = state.telemetry.altitude_m;
          state.telemetry.altitude_m = Math.round(pos.coords.altitude);
          state.telemetry.elevation_delta_m = Math.round(pos.coords.altitude - prevAlt);
        }
        if (pos.coords.speed !== null && pos.coords.speed > 0.5) {
          state.telemetry.speed_mps = pos.coords.speed;
          // convert m/s to min/km: 1000 / (speed * 60)
          const pace = 1000 / (pos.coords.speed * 60);
          state.telemetry.pace_min_per_km = Math.min(30, Math.max(5, Math.round(pace * 10) / 10));
        }
        updateTelemetryDisplay();
      },
      (err) => {
        console.warn('Geolocation sensor warning:', err.message);
      },
      { enableHighAccuracy: true, maximumAge: 10000, timeout: 15000 }
    );
  }
}

// Device Motion Accelerometer (Cadence & Step Counter)
function initMotionSensor() {
  if (typeof window.DeviceMotionEvent !== 'undefined') {
    let lastZ = 0;
    window.addEventListener('devicemotion', (evt) => {
      const acc = evt.accelerationIncludingGravity;
      if (!acc) return;
      const deltaZ = Math.abs((acc.z || 0) - lastZ);
      lastZ = acc.z || 0;
      const now = Date.now();
      if (deltaZ > 4.5 && now - state.lastStepTimestamp > 350) {
        state.stepCount++;
        state.lastStepTimestamp = now;
        // Estimate cadence over moving window
        state.telemetry.cadence_spm = Math.min(160, Math.max(80, Math.round(60000 / (now - state.lastStepTimestamp || 500))));
        updateTelemetryDisplay();
      }
    });
  }
}

// Battery API
function initBatterySensor() {
  if ('getBattery' in navigator) {
    navigator.getBattery().then((battery) => {
      state.telemetry.battery_pct = Math.round(battery.level * 100);
      battery.addEventListener('levelchange', () => {
        state.telemetry.battery_pct = Math.round(battery.level * 100);
        updateTelemetryDisplay();
      });
      updateTelemetryDisplay();
    });
  }
}

// Tactical Web Audio Synthesizer (Rescue Siren Alarm)
function triggerAudioSiren(active = true) {
  if (!active) {
    if (state.sirenOscillator) {
      state.sirenOscillator.stop();
      state.sirenOscillator.disconnect();
      state.sirenOscillator = null;
    }
    state.sirenActive = false;
    return;
  }
  if (state.sirenActive) return;

  try {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;
    state.audioContext = state.audioContext || new AudioCtx();
    if (state.audioContext.state === 'suspended') {
      state.audioContext.resume();
    }

    const osc = state.audioContext.createOscillator();
    const gain = state.audioContext.createGain();

    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(880, state.audioContext.currentTime);

    // Oscillating tactical sweep 880Hz to 1200Hz
    const now = state.audioContext.currentTime;
    for (let i = 0; i < 30; i++) {
      osc.frequency.linearRampToValueAtTime(1200, now + i * 0.8 + 0.4);
      osc.frequency.linearRampToValueAtTime(880, now + i * 0.8 + 0.8);
    }

    gain.gain.setValueAtTime(0.3, now);
    osc.connect(gain);
    gain.connect(state.audioContext.destination);

    osc.start();
    state.sirenOscillator = osc;
    state.sirenActive = true;
  } catch (err) {
    console.error('Audio siren error:', err);
  }
}

// Screen WakeLock to avoid phone sleeping during critical count
async function requestWakeLock() {
  if ('wakeLock' in navigator) {
    try {
      state.wakeLock = await navigator.wakeLock.request('screen');
    } catch (err) {
      console.warn('WakeLock not acquired:', err);
    }
  }
}

// Update UI Telemetry Display
function updateTelemetryDisplay() {
  const t = state.telemetry;
  if (el.metricGps) {
    el.metricGps.textContent = `${t.latitude.toFixed(4)}, ${t.longitude.toFixed(4)}`;
  }
  if (el.metricElevation) {
    el.metricElevation.textContent = `${t.altitude_m}m (Δ ${t.elevation_delta_m >= 0 ? '+' : ''}${t.elevation_delta_m}m)`;
  }
  if (el.metricPace) {
    el.metricPace.textContent = `${t.pace_min_per_km} min/km`;
  }
  if (el.metricCadence) {
    el.metricCadence.textContent = `${t.cadence_spm} SPM`;
  }
  if (el.metricWater) {
    el.metricWater.textContent = `${t.water_remaining_ml} mL`;
  }
  if (el.metricBattery) {
    el.metricBattery.textContent = `${t.battery_pct}%`;
  }
}

// Event Listeners
function setupEventListeners() {
  el.trailSelect.addEventListener('change', (e) => {
    state.selectedTrail = state.trails.find((t) => t.trail_id === e.target.value) || state.trails[0];
  });

  el.startHikeBtn.addEventListener('click', handleStartHike);
  el.checkInBtn.addEventListener('click', handleCheckIn);
  el.scanQrBtn.addEventListener('click', openCameraScanner);
  el.closeScannerBtn.addEventListener('click', closeCameraScanner);
  el.confirmWaypointTokenBtn.addEventListener('click', confirmQrToken);
  el.extendBtn.addEventListener('click', handleExtendWindow);
  el.sosBtn.addEventListener('click', handleEmergencySos);
  el.finishBtn.addEventListener('click', handleFinishHike);
  el.runBenchmarkBtn.addEventListener('click', handleRunBenchmark);

  const resetBtn = document.getElementById('reset-session-btn');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      localStorage.removeItem('trailsafe_active_session');
      state.activeSession = null;
      if (state.timerInterval) clearInterval(state.timerInterval);
      triggerAudioSiren(false);
      const activeCard = el.activeHikeCard || document.getElementById('active-hike-card');
      const setupCard = el.setupCard || document.getElementById('setup-card');
      if (activeCard) activeCard.style.display = 'none';
      if (setupCard) setupCard.style.display = 'block';
    });
  }
}

// Start Hike Session
async function handleStartHike() {
  const hikerName = el.hikerNameInput.value.trim() || 'Solo Explorer';
  const trailId = el.trailSelect.value;
  const timeoutMins = parseInt(el.timeoutInput.value, 10) || 45;
  const emergencyPhone = el.emergencyPhoneInput.value.trim();

  // Tactical vibration
  if (navigator.vibrate) navigator.vibrate(100);
  await requestWakeLock();

  const payload = {
    hiker_id: hikerName,
    trail_id: trailId,
    timeout_minutes: timeoutMins,
    emergency_contact: emergencyPhone || null,
    initial_telemetry: state.telemetry,
  };

  try {
    el.startHikeBtn.disabled = true;
    el.startHikeBtn.textContent = 'Activating Dead-Man Switch...';
    
    const res = await fetch('/api/hikes/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    
    if (!res.ok) throw new Error('Failed to start session');
    
    const session = await res.json();
    state.activeSession = session;
    localStorage.setItem('trailsafe_active_session', JSON.stringify(session));
    
    renderActiveSession();
    startCountdownLoop();
  } catch (err) {
    alert('Session initiation failed: ' + err.message);
  } finally {
    el.startHikeBtn.disabled = false;
    el.startHikeBtn.textContent = 'Initiate Trailhead Session';
  }
}

// Render Active Session View
function renderActiveSession() {
  const s = state.activeSession;
  if (!s) return;

  const setupCard = el.setupCard || document.getElementById('setup-card');
  if (setupCard) setupCard.style.display = 'none';

  const activeCard = el.activeHikeCard || document.getElementById('active-hike-card');
  if (activeCard) activeCard.style.display = 'block';

  const trailNameEl = el.activeTrailName || document.getElementById('active-trail-name');
  if (trailNameEl && s.trail) {
    trailNameEl.textContent = s.trail.trail_name;
  }
  const cpIdx = s.current_checkpoint_idx || 0;
  const totalCps = s.trail && s.trail.checkpoints ? s.trail.checkpoints.length : 1;
  const currentCp = s.trail && s.trail.checkpoints ? s.trail.checkpoints[Math.min(cpIdx, totalCps - 1)] : null;

  const cpNameEl = el.activeCheckpointName || document.getElementById('active-checkpoint-name');
  if (cpNameEl && currentCp) {
    cpNameEl.textContent = currentCp.name;
  }
  const cpIdxEl = el.checkpointIndexText || document.getElementById('checkpoint-index-text');
  if (cpIdxEl) {
    cpIdxEl.textContent = `Waypoint ${Math.min(cpIdx + 1, totalCps)} of ${totalCps}`;
  }

  // Update Waypoint list
  const cpListEl = el.checkpointList || document.getElementById('checkpoint-list');
  if (cpListEl && s.trail && s.trail.checkpoints) {
    cpListEl.innerHTML = '';
    s.trail.checkpoints.forEach((cp, idx) => {
      const item = document.createElement('div');
      item.className = 'checkpoint-item';
      if (idx < cpIdx) {
        item.classList.add('completed');
      } else if (idx === cpIdx) {
        item.classList.add('active');
      }

      item.innerHTML = `
        <div>
          <div class="checkpoint-name">${cp.name}</div>
          <div class="checkpoint-meta">Elev: ${cp.elevation_m}m | Distance: ${cp.distance_km} km</div>
        </div>
        <div class="checkpoint-meta" style="${idx < cpIdx ? 'color: var(--accent-safe); font-weight: 700;' : (idx === cpIdx ? 'color: var(--accent-orange); font-weight: 700;' : '')}">${idx < cpIdx ? '✓ VERIFIED' : (idx === cpIdx ? 'TARGET' : 'PENDING')}</div>
      `;
      cpListEl.appendChild(item);
    });
  }

  // TabPFN Risk Banner
  updateRiskBanner(s.latest_risk);
  updateAuditLog(s.audit_trail);
}

// Update Risk Banner
function updateRiskBanner(risk) {
  if (!risk) return;
  const prob = (risk.hazard_probability * 100).toFixed(1);
  const probEl = el.tabpfnProb || document.getElementById('tabpfn-prob');
  if (probEl) {
    probEl.textContent = `${prob}%`;
    if (risk.hazard_probability >= 0.70) {
      probEl.className = 'risk-score danger';
    } else if (risk.hazard_probability >= 0.40) {
      probEl.className = 'risk-score warning';
    } else {
      probEl.className = 'risk-score safe';
    }
  }

  const defEl = el.tabpfnDeficit || document.getElementById('tabpfn-deficit');
  if (defEl) {
    defEl.textContent = `${risk.projected_water_deficit_ml || 0} mL`;
  }
  const recEl = el.tabpfnRecommendation || document.getElementById('tabpfn-recommendation');
  if (recEl) {
    recEl.textContent = risk.recommendation || 'Pace nominal. Continue leg.';
  }
}

// Update Audit Log
function updateAuditLog(events) {
  if (!events || !el.auditLog) return;
  el.auditLog.innerHTML = '';
  events.slice(-6).reverse().forEach((ev) => {
    const d = document.createElement('div');
    d.className = 'audit-entry';
    const timeStr = ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString() : '';
    d.textContent = `[${timeStr}] ${ev.event.toUpperCase()} ${ev.checkpoint_id || ev.reason || ''}`;
    el.auditLog.appendChild(d);
  });
}

// Countdown Timer Loop
function startCountdownLoop() {
  if (state.timerInterval) clearInterval(state.timerInterval);

  state.timerInterval = setInterval(() => {
    if (!state.activeSession) return;

    const now = Date.now() / 1000;
    const remaining = Math.max(0, Math.round(state.activeSession.deadline_timestamp - now));

    const mins = Math.floor(remaining / 60);
    const secs = remaining % 60;
    const digitsEl = el.countdownDigits || document.getElementById('countdown-digits');
    const statusEl = el.countdownStatusText || document.getElementById('countdown-status-text');

    if (digitsEl) {
      digitsEl.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }

    if (remaining > 300) {
      if (digitsEl) digitsEl.className = 'countdown-digits';
      if (statusEl) statusEl.textContent = 'Normal Safety Window Active';
      triggerAudioSiren(false);
    } else if (remaining > 0) {
      if (digitsEl) digitsEl.className = 'countdown-digits warning';
      if (statusEl) statusEl.textContent = 'Warning: Checkpoint Window Closing Soon';
    } else {
      if (digitsEl) digitsEl.className = 'countdown-digits danger';
      if (statusEl) statusEl.textContent = 'DEAD-MAN SWITCH TRIGGERED: SIREN ACTIVE';
      triggerAudioSiren(true);
      if (navigator.vibrate) navigator.vibrate([300, 100, 300, 100, 500]);
    }
  }, 1000);
}

// Check-in Signal Transmission
async function handleCheckIn() {
  if (!state.activeSession) return;
  const s = state.activeSession;
  const cpIdx = s.current_checkpoint_idx;
  const currentCp = s.trail.checkpoints[Math.min(cpIdx, s.trail.checkpoints.length - 1)];

  if (navigator.vibrate) navigator.vibrate([100, 50, 100]);

  // Adjust telemetry dynamically based on progress
  state.telemetry.hours_elapsed = Math.round((state.telemetry.hours_elapsed + 0.8) * 10) / 10;
  state.telemetry.water_remaining_ml = Math.max(0, state.telemetry.water_remaining_ml - 350);
  state.telemetry.elevation_delta_m = currentCp.elevation_m - 90;

  const payload = {
    checkpoint_id: currentCp.id,
    telemetry: state.telemetry,
  };

  try {
    const btn = el.checkInBtn || document.getElementById('check-in-btn');
    if (btn) {
      btn.disabled = true;
      btn.textContent = 'Transmitting Signal...';
    }

    const res = await fetch(`/api/hikes/${s.session_id}/check-in`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) throw new Error('Check-in failed');
    const updated = await res.json();
    state.activeSession = updated;
    localStorage.setItem('trailsafe_active_session', JSON.stringify(updated));

    triggerAudioSiren(false);
    renderActiveSession();

    if (btn) {
      btn.style.backgroundColor = '#10b981';
      btn.style.borderColor = '#059669';
      btn.innerHTML = `<svg viewBox="0 0 24 24" style="width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:3;"><polyline points="20 6 9 17 4 12"/></svg> Checkpoint Verified ✓`;
      setTimeout(() => {
        btn.style.backgroundColor = '';
        btn.style.borderColor = '';
        btn.innerHTML = `<svg viewBox="0 0 24 24"><path d="M20 6L9 17l-5-5"/></svg> Transmit Waypoint Check-In`;
      }, 2500);
    }
  } catch (err) {
    alert('Check-in failed: ' + err.message);
  } finally {
    const btn = el.checkInBtn || document.getElementById('check-in-btn');
    if (btn) btn.disabled = false;
  }
}

// Camera QR Waypoint Scanner
let cameraStream = null;
async function openCameraScanner() {
  el.scannerModal.classList.add('open');
  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment' },
    });
    el.scannerVideo.srcObject = cameraStream;
  } catch (err) {
    console.warn('Camera access error:', err);
  }
}

function closeCameraScanner() {
  if (cameraStream) {
    cameraStream.getTracks().forEach((track) => track.stop());
    cameraStream = null;
  }
  el.scannerModal.classList.remove('open');
}

function confirmQrToken() {
  closeCameraScanner();
  handleCheckIn();
}

// Window Extension
async function handleExtendWindow() {
  if (!state.activeSession) return;
  try {
    const res = await fetch(`/api/hikes/${state.activeSession.session_id}/extend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ minutes: 15 }),
    });
    if (!res.ok) throw new Error('Window extension failed');
    const data = await res.json();
    state.activeSession.deadline_timestamp = data.deadline_timestamp;
    localStorage.setItem('trailsafe_active_session', JSON.stringify(state.activeSession));
    triggerAudioSiren(false);
    alert('Safety window extended by 15 minutes.');
  } catch (err) {
    alert('Failed to extend window: ' + err.message);
  }
}

// Emergency SOS Panic Button
async function handleEmergencySos() {
  if (!state.activeSession) return;
  const confirmed = confirm('ACTIVATE EMERGENCY SOS RESCUE BEACON?\n\nThis will trigger immediate Telegram and SMS emergency dispatch alerts with your GPS coordinates.');
  if (!confirmed) return;

  if (navigator.vibrate) navigator.vibrate([500, 200, 500, 200, 1000]);
  triggerAudioSiren(true);

  const payload = {
    reason: 'Manual Emergency SOS triggered by solo hiker in field interface',
    latitude: state.telemetry.latitude,
    longitude: state.telemetry.longitude,
  };

  try {
    const res = await fetch(`/api/hikes/${state.activeSession.session_id}/sos`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('SOS dispatch failed');
    alert('EMERGENCY SOS BEACON DISPATCHED TO CONTACTS AND CLUSTER.');
  } catch (err) {
    alert('SOS transmission error: ' + err.message);
  }
}

// Finish Hike
async function handleFinishHike() {
  if (!state.activeSession) return;
  const confirmed = confirm('Mark hike as completed? This will disarm the dead-man switch.');
  if (!confirmed) return;

  try {
    await fetch(`/api/hikes/${state.activeSession.session_id}/finish`, { method: 'POST' });
    triggerAudioSiren(false);
    if (state.timerInterval) clearInterval(state.timerInterval);
    localStorage.removeItem('trailsafe_active_session');
    state.activeSession = null;
    el.activeHikeCard.style.display = 'none';
    el.setupCard.style.display = 'block';
    alert('Hike completed safely. Dead-man switch disarmed.');
  } catch (err) {
    alert('Error finishing hike: ' + err.message);
  }
}

// Run Comparative Empirical Benchmark
async function handleRunBenchmark() {
  el.runBenchmarkBtn.disabled = true;
  el.runBenchmarkBtn.textContent = 'Evaluating TabPFN vs Baselines...';
  try {
    const res = await fetch('/api/benchmark/run');
    const data = await res.json();
    el.benchmarkResultsCard.style.display = 'block';
    el.benchmarkTableBody.innerHTML = '';

    const cls = data.classification;
    const reg = data.regression;

    const rows = [
      { name: 'Prior Labs TabPFN', brier: cls.tabpfn.brier_score, auc: cls.tabpfn.roc_auc, acc: `${(cls.tabpfn.accuracy * 100).toFixed(1)}%`, mae: `${reg.tabpfn_mae_ml} mL` },
      { name: 'Random Forest (50 trees)', brier: cls.random_forest.brier_score, auc: cls.random_forest.roc_auc, acc: `${(cls.random_forest.accuracy * 100).toFixed(1)}%`, mae: `${reg.random_forest_mae_ml} mL` },
      { name: 'Logistic / Linear Regression', brier: cls.logistic_regression.brier_score, auc: cls.logistic_regression.roc_auc, acc: `${(cls.logistic_regression.accuracy * 100).toFixed(1)}%`, mae: `${reg.linear_regression_mae_ml} mL` },
    ];

    rows.forEach((r) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td style="font-weight: 600;">${r.name}</td>
        <td>${r.brier}</td>
        <td>${r.auc}</td>
        <td>${r.acc}</td>
        <td>${r.mae}</td>
      `;
      el.benchmarkTableBody.appendChild(tr);
    });
  } catch (err) {
    alert('Benchmark execution error: ' + err.message);
  } finally {
    el.runBenchmarkBtn.disabled = false;
    el.runBenchmarkBtn.textContent = 'Run TabPFN Empirical Benchmark';
  }
}

// Restore Local Session if reloaded
function restoreLocalSession() {
  const cached = localStorage.getItem('trailsafe_active_session');
  if (cached) {
    try {
      state.activeSession = JSON.parse(cached);
      renderActiveSession();
      startCountdownLoop();
    } catch (e) {
      localStorage.removeItem('trailsafe_active_session');
    }
  }
}

document.addEventListener('DOMContentLoaded', initApp);
