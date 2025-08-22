cat > app.js <<'EOF'
// Barebones demo: two screens, fake data, sliding animation, auto-switch

const VIEW_SWITCH_MS = 20000;  // how often to switch screens
const TRAIN_REFRESH_MS = 12000; // refresh fake trains
const PLANE_REFRESH_MS = 3000;  // refresh fake plane

let showingTrain = true;
let trainInterval = null;
let planeInterval = null;

const fakeTrainsList = [
  { rt: 'Red', dest: '95th', eta: '2 min' },
  { rt: 'Blue', dest: 'O\'Hare', eta: '6 min' },
  { rt: 'Green', dest: 'Harlem/Lake', eta: '12 min' }
];

const fakePlanes = [
  { flight: 'UAL123', lat: 41.98, lon: -87.90, heading: 120, alt: 5000, spd: 180 },
  { flight: 'AAL456', lat: 41.90, lon: -87.70, heading: 60, alt: 4200, spd: 160 }
];

/* ---------- DOM helpers ---------- */
function q(id) { return document.getElementById(id); }

/* ---------- Trains: render fake cards ---------- */
function renderTrains() {
  const container = q('trains');
  container.innerHTML = '';
  // create a (shallow) copy and jitter eta text to look 'live'
  const arr = fakeTrainsList.map((t) => {
    const jitter = Math.random() < 0.4 ? Math.floor(Math.random()*2) : 0;
    const eta = t.eta.includes('min') ? `${Math.max(1, parseInt(t.eta)||0 - jitter)} min` : t.eta;
    return { ...t, eta };
  });

  arr.forEach((t, i) => {
    const card = document.createElement('div');
    card.className = 'train-card';
    card.innerHTML = `<div><strong>${t.rt}</strong> — ${t.dest}</div>
                      <div class="train-meta">${t.eta}</div>`;
    container.appendChild(card);
    setTimeout(() => card.classList.add('enter'), 80 * i);
  });
}

/* ---------- Planes: simple SVG arrow on small map ---------- */
const MAP_CENTER = { lat: 41.88, lon: -87.63 };
const MAP_RADIUS_DEG = 0.25; // degrees for mapping

function drawPlaneOnMiniMap(lat, lon, heading) {
  const w = 800, h = 600;
  const dx = (lon - MAP_CENTER.lon) / MAP_RADIUS_DEG;
  const dy = (lat - MAP_CENTER.lat) / MAP_RADIUS_DEG;
  const cx = Math.max(-1, Math.min(1, dx));
  const cy = Math.max(-1, Math.min(1, dy));
  const x = (0.5 + cx * 0.45) * w;
  const y = (0.5 - cy * 0.45) * h;

  const layer = document.getElementById('plane-layer');
  layer.innerHTML = '';
  const g = document.createElementNS('http://www.w3.org/2000/svg','g');
  g.setAttribute('transform', `translate(${x},${y}) rotate(${heading})`);
  const poly = document.createElementNS('http://www.w3.org/2000/svg','polygon');
  poly.setAttribute('points', '0,-12 6,8 0,4 -6,8');
  poly.setAttribute('fill', '#ffd166');
  poly.setAttribute('stroke', '#f2a365');
  poly.setAttribute('stroke-width', '1');
  g.appendChild(poly);
  const circ = document.createElementNS('http://www.w3.org/2000/svg','circle');
  circ.setAttribute('cx', '0'); circ.setAttribute('cy','0'); circ.setAttribute('r','2'); circ.setAttribute('fill','#fff');
  g.appendChild(circ);
  layer.appendChild(g);
}

function renderPlane(fake = null) {
  const p = fake || fakePlanes[Math.floor(Math.random() * fakePlanes.length)];
  q('flight').textContent = `Flight: ${p.flight}`;
  q('alt').textContent = `Alt: ${p.alt} ft`;
  q('spd').textContent = `Spd: ${p.spd} kts`;
  drawPlaneOnMiniMap(p.lat, p.lon, p.heading);
}

/* ---------- View switching ---------- */
function switchViews() {
  if (showingTrain) {
    q('train-view').classList.remove('visible'); q('train-view').classList.add('hidden');
    q('plane-view').classList.remove('hidden'); q('plane-view').classList.add('visible');

    // start plane updates
    if (planeInterval) clearInterval(planeInterval);
    renderPlane();
    planeInterval = setInterval(renderPlane, PLANE_REFRESH_MS);
  } else {
    q('plane-view').classList.remove('visible'); q('plane-view').classList.add('hidden');
    q('train-view').classList.remove('hidden'); q('train-view').classList.add('visible');

    if (planeInterval) { clearInterval(planeInterval); planeInterval = null; }
    renderTrains();
    // refresh trains occasionally
    if (trainInterval) clearInterval(trainInterval);
    trainInterval = setInterval(renderTrains, TRAIN_REFRESH_MS);
  }
  showingTrain = !showingTrain;
}

/* ---------- Init ---------- */
document.addEventListener('DOMContentLoaded', () => {
  // initial render
  renderTrains();
  trainInterval = setInterval(renderTrains, TRAIN_REFRESH_MS);
  // auto-switch
  setInterval(switchViews, VIEW_SWITCH_MS);
  // Optionally allow click to toggle quickly for demo/testing
  document.addEventListener('keydown', (e) => {
    if (e.key === ' ') switchViews();
  });
});
EOF
