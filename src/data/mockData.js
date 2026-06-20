// =====================================================================
//  ADVANCED MOCK DATA ENGINE v2.0
//  Smart Policing Platform — Ahmedabad Crime Dataset
//
//  Realistic patterns included:
//  ✅ Seasonal crime multipliers (monsoon dip, winter spike)
//  ✅ Festival spikes (Navratri, Diwali, Uttarayan, Holi, New Year)
//  ✅ Time-of-day distributions per crime type
//  ✅ Weekend vs. weekday behavioral differences
//  ✅ Area-specific crime tendencies (posh vs. dense areas)
//  ✅ Cybercrime YoY growth trend (2023→2025)
//  ✅ Contextual severity (night + festival = higher severity)
//  ✅ Hotspot emergence and decay over time
//  ✅ Reproducible via fixed seed (seed=42)
// =====================================================================


// ─── SEEDED RANDOM NUMBER GENERATOR ─────────────────────────────────────────
// mulberry32 — fast, high-quality 32-bit PRNG
function mulberry32(seed) {
  return function () {
    seed |= 0;
    seed = (seed + 0x6D2B79F5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const rand = mulberry32(42); // Fixed seed — always reproducible

function randomInRange(min, max) { return min + rand() * (max - min); }
function randomItem(arr) { return arr[Math.floor(rand() * arr.length)]; }
function jitter(val, spread = 0.015) { return val + (rand() - 0.5) * spread * 2; }

function weightedPick(items, weights) {
  const total = weights.reduce((a, b) => a + b, 0);
  let r = rand() * total;
  for (let i = 0; i < items.length; i++) {
    r -= weights[i];
    if (r <= 0) return items[i];
  }
  return items[items.length - 1];
}

function daysInMonth(year, month) {
  return new Date(year, month, 0).getDate();
}

function dayOfWeek(year, month, day) {
  return new Date(year, month - 1, day).getDay(); // 0=Sun, 6=Sat
}


// ─── AHMEDABAD AREAS ─────────────────────────────────────────────────────────
// base weight = overall crime density; zone = city quadrant
export const AREAS = [
  { name: 'Naroda',         lat: 23.0695, lng: 72.6415, weight: 9, zone: 'East'    },
  { name: 'Maninagar',      lat: 22.9970, lng: 72.6043, weight: 8, zone: 'South'   },
  { name: 'Bapunagar',      lat: 23.0530, lng: 72.6160, weight: 9, zone: 'East'    },
  { name: 'Asarwa',         lat: 23.0590, lng: 72.6080, weight: 8, zone: 'East'    },
  { name: 'Dariapur',       lat: 23.0310, lng: 72.5960, weight: 8, zone: 'Central' },
  { name: 'Gomtipur',       lat: 23.0280, lng: 72.6300, weight: 7, zone: 'East'    },
  { name: 'Isanpur',        lat: 22.9845, lng: 72.6117, weight: 7, zone: 'South'   },
  { name: 'Nikol',          lat: 23.0502, lng: 72.6525, weight: 7, zone: 'East'    },
  { name: 'Vastral',        lat: 23.0261, lng: 72.6573, weight: 6, zone: 'East'    },
  { name: 'Narol',          lat: 22.9700, lng: 72.6200, weight: 5, zone: 'South'   },
  { name: 'Vatva',          lat: 22.9600, lng: 72.6400, weight: 5, zone: 'South'   },
  { name: 'Ranip',          lat: 23.0935, lng: 72.5617, weight: 6, zone: 'North'   },
  { name: 'Shahibaug',      lat: 23.0651, lng: 72.5899, weight: 5, zone: 'North'   },
  { name: 'Chandkheda',     lat: 23.1180, lng: 72.5908, weight: 5, zone: 'North'   },
  { name: 'Paldi',          lat: 23.0103, lng: 72.5731, weight: 5, zone: 'South'   },
  { name: 'Ellis Bridge',   lat: 23.0328, lng: 72.5716, weight: 4, zone: 'Central' },
  { name: 'Navrangpura',    lat: 23.0395, lng: 72.5613, weight: 4, zone: 'Central' },
  { name: 'Ambavadi',       lat: 23.0270, lng: 72.5519, weight: 3, zone: 'West'    },
  { name: 'Vastrapur',      lat: 23.0421, lng: 72.5301, weight: 3, zone: 'West'    },
  { name: 'Satellite',      lat: 23.0226, lng: 72.5137, weight: 3, zone: 'West'    },
  { name: 'Gota',           lat: 23.1018, lng: 72.5539, weight: 3, zone: 'North'   },
  { name: 'Thaltej',        lat: 23.0566, lng: 72.5058, weight: 2, zone: 'West'    },
  { name: 'Prahlad Nagar',  lat: 23.0157, lng: 72.5106, weight: 2, zone: 'West'    },
  { name: 'Bodakdev',       lat: 23.0453, lng: 72.5164, weight: 2, zone: 'West'    },
  { name: 'Bopal',          lat: 23.0297, lng: 72.4673, weight: 2, zone: 'West'    },
  { name: 'Vejalpur',       lat: 23.0003, lng: 72.5465, weight: 3, zone: 'South'   },
  { name: 'Sarkhej',        lat: 22.9790, lng: 72.4980, weight: 3, zone: 'South'   },
];

export const CRIME_TYPES = [
  'Theft', 'Chain Snatching', 'Mobile Theft', 'Vehicle Theft',
  'Robbery', 'Burglary', 'Assault', 'Domestic Violence',
  'Drug Offense', 'Fraud', 'Kidnapping', 'Murder',
  'Eve Teasing', 'Property Dispute', 'Arms Act Violation',
];

export const CYBER_TYPES = [
  'UPI Fraud', 'Phishing', 'OTP Scam', 'Social Media Fraud',
  'Identity Theft', 'Online Banking Fraud', 'Investment Scam',
  'Job Fraud', 'Lottery Scam', 'Cyberstalking',
];

export const SEVERITY_LEVELS = ['Low', 'Medium', 'High', 'Critical'];


// ─── SEASONAL PATTERNS ───────────────────────────────────────────────────────
// Monthly crime frequency multipliers (index 0 = Jan ... 11 = Dec)
const MONTHLY_MULTIPLIERS = [
  1.15,  // Jan  — Uttarayan crowds, winter activity
  0.88,  // Feb  — Quiet, post-festival lull
  1.12,  // Mar  — Holi, heat building up
  1.05,  // Apr  — Summer begins, outdoor activity
  1.00,  // May  — Moderate
  0.82,  // Jun  — Monsoon start, people stay indoors
  0.78,  // Jul  — Peak monsoon, lowest crime month
  0.83,  // Aug  — Independence Day activity
  0.92,  // Sep  — Monsoon ending
  1.35,  // Oct  — NAVRATRI + early Diwali (huge spike)
  1.25,  // Nov  — Diwali peak, post-Diwali burglary
  1.15,  // Dec  — New Year celebrations, cold nights
];


// ─── FESTIVAL DEFINITIONS ────────────────────────────────────────────────────
// Each festival defines: month, day range, crime type boosts, and overall spike
const FESTIVALS = [
  {
    name: 'Uttarayan',
    events: [
      { year: 2023, month: 1, dayStart: 13, dayEnd: 15 },
      { year: 2024, month: 1, dayStart: 13, dayEnd: 15 },
      { year: 2025, month: 1, dayStart: 13, dayEnd: 15 },
    ],
    overallMultiplier: 1.9,
    // Mass kite-flying events: eve teasing, theft in crowds
    crimeBoosts: { 'Eve Teasing': 4.0, 'Chain Snatching': 3.0, 'Theft': 2.5, 'Mobile Theft': 2.0, 'Assault': 1.5 },
  },
  {
    name: 'Holi',
    events: [
      { year: 2023, month: 3, dayStart: 7,  dayEnd: 8  },
      { year: 2024, month: 3, dayStart: 24, dayEnd: 25 },
      { year: 2025, month: 3, dayStart: 13, dayEnd: 14 },
    ],
    overallMultiplier: 1.7,
    crimeBoosts: { 'Assault': 3.0, 'Eve Teasing': 3.5, 'Drug Offense': 2.5, 'Robbery': 1.5 },
  },
  {
    name: 'Navratri',
    events: [
      { year: 2023, month: 10, dayStart: 15, dayEnd: 24 },
      { year: 2024, month: 10, dayStart: 3,  dayEnd: 12 },
      { year: 2025, month: 9,  dayStart: 22, dayEnd: 30 },
    ],
    overallMultiplier: 2.1, // Largest festival in Ahmedabad = highest spike
    crimeBoosts: { 'Eve Teasing': 4.5, 'Chain Snatching': 3.5, 'Theft': 2.5, 'Mobile Theft': 2.5, 'Robbery': 2.0 },
  },
  {
    name: 'Diwali',
    events: [
      { year: 2023, month: 11, dayStart: 10, dayEnd: 14 },
      { year: 2024, month: 11, dayStart: 1,  dayEnd: 4  },
      { year: 2025, month: 10, dayStart: 20, dayEnd: 23 },
    ],
    overallMultiplier: 2.0,
    // People travel, leave homes empty → burglary spike
    crimeBoosts: { 'Burglary': 4.5, 'Theft': 2.5, 'Robbery': 2.0, 'Vehicle Theft': 2.0, 'Chain Snatching': 2.0 },
  },
  {
    name: 'New Year',
    events: [
      { year: 2023, month: 12, dayStart: 31, dayEnd: 31 },
      { year: 2024, month: 12, dayStart: 31, dayEnd: 31 },
    ],
    overallMultiplier: 1.8,
    crimeBoosts: { 'Assault': 3.0, 'Eve Teasing': 3.5, 'Drug Offense': 3.0, 'Robbery': 1.8 },
  },
  {
    name: 'New Year Day',
    events: [
      { year: 2024, month: 1, dayStart: 1, dayEnd: 1 },
      { year: 2025, month: 1, dayStart: 1, dayEnd: 1 },
    ],
    overallMultiplier: 1.6,
    crimeBoosts: { 'Assault': 2.5, 'Eve Teasing': 2.5, 'Drug Offense': 2.5 },
  },
];

function getFestivalContext(year, month, day) {
  for (const fest of FESTIVALS) {
    for (const ev of fest.events) {
      if (ev.year === year && ev.month === month && day >= ev.dayStart && day <= ev.dayEnd) {
        return { isFestival: true, name: fest.name, multiplier: fest.overallMultiplier, boosts: fest.crimeBoosts };
      }
    }
  }
  return { isFestival: false, name: null, multiplier: 1.0, boosts: {} };
}


// ─── TIME-OF-DAY DISTRIBUTIONS ───────────────────────────────────────────────
// 24-element array: index = hour (0–23), value = relative probability weight
// Higher value = more crimes happen at that hour for that crime type
const HOUR_WEIGHTS = {
  'Theft':            [3,3,3,2,1,1,1,2,3,3,3,3,3,2,2,3,3,4,4,4,4,4,4,4],
  'Chain Snatching':  [1,0,0,0,0,0,1,2,5,5,4,3,3,3,3,3,3,5,5,5,4,3,2,1],
  'Mobile Theft':     [1,0,0,0,0,0,1,2,4,5,5,5,5,4,4,4,4,5,5,4,3,2,2,1],
  'Vehicle Theft':    [4,4,5,5,4,3,2,1,1,1,1,1,1,1,2,2,2,2,3,3,4,4,4,4],
  'Robbery':          [2,2,2,2,1,1,1,1,2,2,2,2,2,2,2,2,2,3,4,5,5,5,4,3],
  'Burglary':         [3,4,5,5,4,3,1,1,0,0,0,0,1,3,4,3,2,2,2,2,2,3,3,3],
  'Assault':          [1,1,1,1,0,0,0,1,2,2,2,2,2,2,2,2,2,2,3,4,5,5,5,4],
  'Domestic Violence':[1,1,1,0,0,0,0,1,3,4,3,2,2,2,2,2,2,3,5,5,5,4,3,2],
  'Drug Offense':     [2,3,4,4,3,1,0,0,0,0,0,0,1,1,1,1,1,2,3,4,5,5,5,4],
  'Fraud':            [0,0,0,0,0,0,0,0,2,4,5,5,5,4,4,5,5,5,4,2,1,0,0,0],
  'Kidnapping':       [1,1,0,0,0,0,1,3,4,3,2,2,2,3,4,3,2,2,3,4,3,2,1,1],
  'Murder':           [2,3,3,2,1,0,0,0,0,0,0,0,0,0,1,1,1,1,2,3,4,5,5,4],
  'Eve Teasing':      [0,0,0,0,0,0,0,1,2,2,2,2,2,2,2,2,2,3,5,5,5,5,4,2],
  'Property Dispute': [0,0,0,0,0,0,0,1,3,4,4,4,4,4,4,4,4,4,3,2,1,0,0,0],
  'Arms Act Violation':[1,2,3,3,2,1,0,0,0,0,0,0,0,0,0,0,0,1,2,3,4,4,4,3],
};

function pickHour(crimeType) {
  const weights = HOUR_WEIGHTS[crimeType];
  if (!weights) return Math.floor(rand() * 24);
  return weightedPick(Array.from({ length: 24 }, (_, i) => i), weights);
}


// ─── AREA-SPECIFIC CRIME TENDENCIES ──────────────────────────────────────────
// Multiplier per crime type specific to that area (reflects local socioeconomics)
const AREA_CRIME_TENDENCIES = {
  'Naroda':        { 'Drug Offense': 3.0, 'Robbery': 2.5, 'Assault': 2.5, 'Arms Act Violation': 3.0, 'Murder': 2.5 },
  'Maninagar':     { 'Chain Snatching': 2.5, 'Vehicle Theft': 2.0, 'Theft': 1.8, 'Robbery': 1.5 },
  'Bapunagar':     { 'Robbery': 2.2, 'Chain Snatching': 2.0, 'Assault': 1.8, 'Drug Offense': 1.5 },
  'Asarwa':        { 'Drug Offense': 2.5, 'Assault': 2.2, 'Robbery': 1.8, 'Arms Act Violation': 1.5 },
  'Dariapur':      { 'Theft': 2.5, 'Property Dispute': 3.0, 'Drug Offense': 2.0, 'Chain Snatching': 1.8 },
  'Gomtipur':      { 'Vehicle Theft': 2.5, 'Burglary': 2.0, 'Robbery': 1.8 },
  'Isanpur':       { 'Assault': 2.0, 'Domestic Violence': 2.2, 'Robbery': 1.5 },
  'Nikol':         { 'Robbery': 2.5, 'Assault': 2.0, 'Chain Snatching': 1.8 },
  'Vastral':       { 'Chain Snatching': 2.2, 'Robbery': 2.0, 'Vehicle Theft': 1.8 },
  'Narol':         { 'Vehicle Theft': 2.5, 'Robbery': 2.0, 'Burglary': 1.8 },
  'Vatva':         { 'Burglary': 2.5, 'Arms Act Violation': 2.0, 'Vehicle Theft': 2.0 },
  'Ranip':         { 'Drug Offense': 1.8, 'Theft': 1.5, 'Chain Snatching': 1.5 },
  'Shahibaug':     { 'Theft': 1.5, 'Mobile Theft': 1.5, 'Chain Snatching': 1.5 },
  'Chandkheda':    { 'Fraud': 2.0, 'Mobile Theft': 1.8, 'Theft': 1.5 },
  'Paldi':         { 'Theft': 1.5, 'Mobile Theft': 1.5, 'Eve Teasing': 1.5 },
  // Upscale west areas — white-collar and property crimes
  'Satellite':     { 'Burglary': 2.5, 'Vehicle Theft': 2.5, 'Fraud': 2.0, 'Mobile Theft': 1.5 },
  'Bodakdev':      { 'Vehicle Theft': 3.0, 'Burglary': 2.5, 'Fraud': 2.5, 'Mobile Theft': 1.5 },
  'Prahlad Nagar': { 'Burglary': 2.5, 'Vehicle Theft': 2.5, 'Fraud': 2.2 },
  'Bopal':         { 'Burglary': 2.0, 'Vehicle Theft': 2.0, 'Theft': 1.3 },
  'Navrangpura':   { 'Fraud': 2.5, 'Mobile Theft': 2.0, 'Eve Teasing': 1.5 },
  'Vastrapur':     { 'Vehicle Theft': 2.0, 'Fraud': 2.0, 'Burglary': 1.8 },
  'Thaltej':       { 'Vehicle Theft': 2.0, 'Burglary': 1.8, 'Fraud': 1.8 },
};


// ─── CONTEXTUAL SEVERITY PROBABILITIES ───────────────────────────────────────
// Base probability distribution per crime type [Critical, High, Medium, Low]
const BASE_SEVERITY_PROBS = {
  'Murder':           [0.95, 0.05, 0.00, 0.00],
  'Kidnapping':       [0.60, 0.35, 0.05, 0.00],
  'Arms Act Violation':[0.30, 0.50, 0.18, 0.02],
  'Robbery':          [0.20, 0.55, 0.20, 0.05],
  'Assault':          [0.10, 0.40, 0.35, 0.15],
  'Burglary':         [0.10, 0.35, 0.40, 0.15],
  'Drug Offense':     [0.06, 0.30, 0.44, 0.20],
  'Fraud':            [0.05, 0.25, 0.45, 0.25],
  'Vehicle Theft':    [0.03, 0.20, 0.50, 0.27],
  'Chain Snatching':  [0.06, 0.30, 0.44, 0.20],
  'Domestic Violence':[0.08, 0.35, 0.40, 0.17],
  'Theft':            [0.01, 0.10, 0.35, 0.54],
  'Mobile Theft':     [0.01, 0.08, 0.30, 0.61],
  'Eve Teasing':      [0.02, 0.15, 0.45, 0.38],
  'Property Dispute': [0.02, 0.10, 0.35, 0.53],
};

function determineSeverity(crimeType, hour, dayOfWeek, isFestival) {
  let [c, h, m, l] = BASE_SEVERITY_PROBS[crimeType] || [0.05, 0.20, 0.45, 0.30];

  // Night effect (10 PM – 4 AM): crimes are more violent at night
  const isNight = hour >= 22 || hour <= 4;
  if (isNight) {
    c = Math.min(1, c * 1.6); h = Math.min(1, h * 1.3);
    const t = c + h + m + l; c /= t; h /= t; m /= t; l /= t;
  }

  // Festival effect: crowd pressure increases severity
  if (isFestival) {
    c = Math.min(1, c * 1.35); h = Math.min(1, h * 1.25);
    const t = c + h + m + l; c /= t; h /= t; m /= t; l /= t;
  }

  // Weekend assault/eve teasing is more severe (alcohol, crowds)
  const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
  if (isWeekend && (crimeType === 'Assault' || crimeType === 'Eve Teasing' || crimeType === 'Drug Offense')) {
    h = Math.min(1, h * 1.4);
    const t = c + h + m + l; c /= t; h /= t; m /= t; l /= t;
  }

  return weightedPick(['Critical', 'High', 'Medium', 'Low'], [c, h, m, l]);
}


// ─── AREA TEMPORAL WEIGHTS (Hotspot Emergence / Decay) ───────────────────────
// Returns the effective crime weight for an area at a given year/month
// Models: crackdowns (weight ↓), new industrial zones (weight ↑)
function getAreaTemporalWeight(areaName, year, month) {
  const base = AREAS.find(a => a.name === areaName)?.weight || 5;
  let multiplier = 1.0;

  // Narol & Vatva: emerging industrial hotspot from mid-2024
  if ((areaName === 'Narol' || areaName === 'Vatva') && (year === 2024 && month >= 6 || year === 2025)) {
    multiplier *= 1.6;
  }

  // Chandkheda police crackdown success — crime reduction from mid-2024
  if (areaName === 'Chandkheda' && (year === 2024 && month >= 8 || year === 2025)) {
    multiplier *= 0.55;
  }

  // Dariapur old city revival operation — 2025 reduction
  if (areaName === 'Dariapur' && year === 2025) {
    multiplier *= 0.72;
  }

  // Naroda stays persistently high in 2024-2025
  if (areaName === 'Naroda' && year >= 2024) {
    multiplier *= 1.2;
  }

  // Maninagar slight reduction after targeted operations in 2025
  if (areaName === 'Maninagar' && year === 2025) {
    multiplier *= 0.80;
  }

  // Bapunagar escalating 2024 → 2025
  if (areaName === 'Bapunagar' && year === 2025) {
    multiplier *= 1.25;
  }

  // Satellite / Bodakdev rising burglary trend 2024-2025 (new residents)
  if ((areaName === 'Satellite' || areaName === 'Bodakdev') && year >= 2024) {
    multiplier *= 1.35;
  }

  return base * multiplier;
}


// ─── CRIME TYPE PICKER ────────────────────────────────────────────────────────
function pickCrimeType(areaName, hour, dow, festivalBoosts) {
  const isWeekend  = dow === 0 || dow === 6;
  const isNight    = hour >= 21 || hour <= 5;
  const isMorning  = hour >= 7  && hour <= 10;
  const isEvening  = hour >= 17 && hour <= 21;
  const areaTend   = AREA_CRIME_TENDENCIES[areaName] || {};

  const weights = CRIME_TYPES.map(type => {
    let w = 1.0;

    // Area-specific tendency
    w *= (areaTend[type] || 1.0);

    // Festival boost for this crime type
    w *= (festivalBoosts[type] || 1.0);

    // Time-of-day weight (normalize so avg ≈ 1.0)
    const hw = HOUR_WEIGHTS[type];
    if (hw) w *= (hw[hour] + 0.5) / 3.5;

    // Weekend crime profile shifts
    if (isWeekend) {
      if (['Assault','Drug Offense','Eve Teasing','Robbery'].includes(type)) w *= 1.6;
      if (['Fraud','Property Dispute'].includes(type)) w *= 0.6;
    } else {
      // Weekday: commuter crimes, office fraud
      if (['Fraud','Chain Snatching','Mobile Theft'].includes(type)) w *= 1.4;
      if (['Assault','Eve Teasing'].includes(type)) w *= 0.75;
    }

    // Night profile
    if (isNight) {
      if (['Burglary','Robbery','Murder','Drug Offense','Vehicle Theft','Arms Act Violation'].includes(type)) w *= 2.0;
      if (['Fraud','Property Dispute','Mobile Theft'].includes(type)) w *= 0.2;
    }

    // Morning rush: commute crimes
    if (isMorning && ['Chain Snatching','Mobile Theft'].includes(type)) w *= 1.7;

    // Evening market crimes
    if (isEvening && ['Eve Teasing','Chain Snatching','Theft'].includes(type)) w *= 1.5;

    return Math.max(0.01, w);
  });

  return weightedPick(CRIME_TYPES, weights);
}


// ─── DATE GENERATION WITH SEASONAL BIAS ──────────────────────────────────────
function generateRealisticDate() {
  // Year distribution: realistic data coverage
  const year = weightedPick([2023, 2024, 2025], [0.30, 0.38, 0.32]);

  // Monthly weights with seasonal multipliers
  // 2025: only Jan–Jun are available (cap future data)
  const monthWeights = MONTHLY_MULTIPLIERS.map((w, i) => {
    if (year === 2025 && i >= 6) return 0.01; // very few records after June 2025
    return w;
  });
  const month = weightedPick([1,2,3,4,5,6,7,8,9,10,11,12], monthWeights);
  const maxDay = daysInMonth(year, month);
  const day = Math.floor(rand() * maxDay) + 1;
  const dow = dayOfWeek(year, month, day);

  return { year, month, day, dow };
}


// ─── FIR DESCRIPTION GENERATOR ───────────────────────────────────────────────
const DESCRIPTIONS = {
  'Murder':           (a) => [`Homicide case registered in ${a}`, `Suspicious death under investigation in ${a}`],
  'Kidnapping':       (a) => [`Kidnapping/abduction case registered from ${a}`, `Missing person report filed from ${a}`],
  'Arms Act Violation':(a) => [`Illegal arms recovered in ${a}`, `Arms act violation registered in ${a}`],
  'Robbery':          (a) => [`Armed robbery reported in ${a}`, `Cash robbery near ${a} ATM/shop`],
  'Burglary':         (a) => [`House break-in reported in ${a} residential area`, `Commercial establishment burgled in ${a}`],
  'Assault':          (a) => [`Physical assault case in ${a}`, `Victim assaulted near ${a} by unidentified persons`],
  'Drug Offense':     (a) => [`Drug peddling activity detected in ${a}`, `Narcotics seized from suspects in ${a}`],
  'Fraud':            (a) => [`Financial fraud case filed from ${a}`, `Cheating case involving cash registered in ${a}`],
  'Vehicle Theft':    (a) => [`Two-wheeler stolen from ${a} parking area`, `Car/bike theft reported in ${a}`],
  'Chain Snatching':  (a) => [`Gold chain snatching near ${a} market`, `Victim's jewellery snatched in ${a}`],
  'Domestic Violence':(a) => [`Domestic violence complaint from ${a}`, `Family dispute escalated in ${a}`],
  'Theft':            (a) => [`Property theft reported near ${a} market`, `Items stolen from ${a} residence`],
  'Mobile Theft':     (a) => [`Smartphone snatched/stolen in ${a}`, `Mobile phone theft reported from ${a}`],
  'Eve Teasing':      (a) => [`Eve teasing / harassment complaint near ${a}`, `Verbal/physical harassment reported in ${a}`],
  'Property Dispute': (a) => [`Property encroachment complaint from ${a}`, `Land dispute case filed in ${a}`],
};

function generateDescription(type, area) {
  const opts = DESCRIPTIONS[type]?.(area) || [`Incident reported in ${area}`];
  return opts[Math.floor(rand() * opts.length)];
}


// ─── MAIN CRIME GENERATOR ─────────────────────────────────────────────────────
function generateCrimes(count = 10000) {
  const crimes = [];

  for (let i = 0; i < count; i++) {
    // 1. Pick time with seasonal bias
    const { year, month, day, dow } = generateRealisticDate();

    // 2. Get festival context for this date
    const fest = getFestivalContext(year, month, day);

    // 3. Pick area with temporal hotspot weights
    const areaWeights = AREAS.map(a => getAreaTemporalWeight(a.name, year, month));
    // During festivals, boost certain festival-heavy areas (e.g., Navratri in Navrangpura)
    if (fest.isFestival) {
      AREAS.forEach((a, idx) => {
        if (['Navrangpura', 'Vastrapur', 'Paldi', 'Ellis Bridge'].includes(a.name)) {
          areaWeights[idx] *= 1.8; // festival venues area
        }
      });
    }
    const area = weightedPick(AREAS, areaWeights);

    // 4. Pick hour based on crime type (we'll pick crime type first using defaults,
    //    then refine — slight chicken-and-egg, solved by two-pass below)
    // Simple approach: pick hour first from general distribution
    const hour = Math.floor(rand() * 24);

    // 5. Pick crime type using all context
    const crimeType = pickCrimeType(area.name, hour, dow, fest.boosts);

    // 6. Refine hour using the actual crime type distribution
    const refinedHour = rand() < 0.65 ? pickHour(crimeType) : hour;

    // 7. Determine severity contextually
    const severity = determineSeverity(crimeType, refinedHour, dow, fest.isFestival);

    // 8. Build timestamp
    const mm = String(month).padStart(2, '0');
    const dd = String(day).padStart(2, '0');
    const hh = String(refinedHour).padStart(2, '0');
    const min = String(Math.floor(rand() * 60)).padStart(2, '0');
    const sec = String(Math.floor(rand() * 60)).padStart(2, '0');
    const timestamp = `${year}-${mm}-${dd} ${hh}:${min}:${sec}`;

    crimes.push({
      crime_id:    `CRM-${String(i + 1).padStart(6, '0')}`,
      crime_type:  crimeType,
      latitude:    parseFloat(jitter(area.lat, 0.018).toFixed(6)),
      longitude:   parseFloat(jitter(area.lng, 0.018).toFixed(6)),
      area:        area.name,
      zone:        area.zone,
      timestamp,
      severity,
      status:      weightedPick(['Reported', 'Under Investigation', 'Chargesheeted', 'Closed'], [0.35, 0.30, 0.15, 0.20]),
      fir_number:  `AHD/${year}/${String(Math.floor(rand() * 99999)).padStart(5, '0')}`,
      description: generateDescription(crimeType, area.name),
      hour:        refinedHour,
      day_of_week: dow,
      month,
      year,
      day,
      is_weekend:  dow === 0 || dow === 6,
      is_festival: fest.isFestival,
      festival_name: fest.name || null,
    });
  }

  return crimes;
}


// ─── CYBERCRIME GENERATOR WITH GROWTH TREND ───────────────────────────────────
// YoY growth rates reflecting real India cybercrime trends
const CYBER_GROWTH_BY_YEAR = { 2023: 1.0, 2024: 1.55, 2025: 2.30 };

// UPI fraud grows faster than other types
const CYBER_TYPE_GROWTH = {
  'UPI Fraud':           { 2023: 1.0, 2024: 1.8, 2025: 3.0 },
  'Online Banking Fraud':{ 2023: 1.0, 2024: 1.4, 2025: 1.9 },
  'Investment Scam':     { 2023: 1.0, 2024: 1.6, 2025: 2.5 },
  'Job Fraud':           { 2023: 1.0, 2024: 1.5, 2025: 2.2 },
  'OTP Scam':            { 2023: 1.0, 2024: 1.7, 2025: 2.8 },
  'Phishing':            { 2023: 1.0, 2024: 1.3, 2025: 1.7 },
  'Social Media Fraud':  { 2023: 1.0, 2024: 1.6, 2025: 2.4 },
  'Identity Theft':      { 2023: 1.0, 2024: 1.2, 2025: 1.5 },
  'Lottery Scam':        { 2023: 1.0, 2024: 1.1, 2025: 1.2 },
  'Cyberstalking':       { 2023: 1.0, 2024: 1.4, 2025: 1.8 },
};

const CYBER_AMOUNT_RANGES = {
  'UPI Fraud':            [500,   80000],
  'Online Banking Fraud': [5000,  600000],
  'Investment Scam':      [10000, 3000000],
  'Job Fraud':            [2000,  150000],
  'Lottery Scam':         [1000,  50000],
  'Phishing':             [1000,  100000],
  'OTP Scam':             [500,   120000],
  'Social Media Fraud':   [500,   30000],
  'Identity Theft':       [0,     15000],
  'Cyberstalking':        [0,     0],
};

function generateCybercrime(count = 1200) {
  const reports = [];

  for (let i = 0; i < count; i++) {
    const { year, month, day, dow } = generateRealisticDate();

    // Adjust year distribution to reflect growth: 2025 has more records
    const yearWeighted = weightedPick([2023, 2024, 2025], [0.22, 0.35, 0.43]);

    // Pick fraud type weighted by growth for this year
    const typeWeights = CYBER_TYPES.map(t => {
      const growth = CYBER_TYPE_GROWTH[t]?.[yearWeighted] || CYBER_GROWTH_BY_YEAR[yearWeighted] || 1;
      return growth;
    });
    const fraudType = weightedPick(CYBER_TYPES, typeWeights);

    const area = weightedPick(AREAS, AREAS.map(a => a.weight));
    const [minAmt, maxAmt] = CYBER_AMOUNT_RANGES[fraudType] || [500, 50000];

    // Amount lost also grows over time (larger scams)
    const amountGrowthFactor = yearWeighted === 2025 ? 1.6 : yearWeighted === 2024 ? 1.25 : 1.0;
    const amount = Math.round(randomInRange(minAmt, maxAmt) * amountGrowthFactor);

    const mm = String(month).padStart(2, '0');
    const dd = String(day).padStart(2, '0');
    const hh = String(Math.floor(rand() * 24)).padStart(2, '0');
    const min = String(Math.floor(rand() * 60)).padStart(2, '0');

    reports.push({
      report_id:       `CYB-${String(i + 1).padStart(5, '0')}`,
      fraud_type:      fraudType,
      latitude:        parseFloat(jitter(area.lat, 0.022).toFixed(6)),
      longitude:       parseFloat(jitter(area.lng, 0.022).toFixed(6)),
      area:            area.name,
      zone:            area.zone,
      amount_lost:     amount,
      timestamp:       `${yearWeighted}-${mm}-${dd} ${hh}:${min}:00`,
      status:          weightedPick(['Reported','Under Investigation','Chargesheeted','Closed'], [0.35,0.30,0.15,0.20]),
      platform:        weightedPick(['WhatsApp','Telegram','Phone Call','Email','Website','Instagram','OLX','Unknown'], [3,2,4,2,2,2,1,1]),
      victim_age_group:weightedPick(['18-25','26-35','36-45','46-60','60+'], [2,3,3,2,1]),
      hour:            parseInt(hh),
      month,
      year:            yearWeighted,
      day_of_week:     dow,
      is_weekend:      dow === 0 || dow === 6,
    });
  }

  return reports;
}


// ─── PATROL UNITS ─────────────────────────────────────────────────────────────
const OFFICER_NAMES = [
  'SI Rajan Patel','HC Amit Shah','ASI Meera Joshi','SI Suresh Kumar',
  'PSI Priya Desai','SI Vikram Singh','HC Rajesh Yadav','ASI Anjali Mehta',
  'SI Dinesh Chauhan','PSI Kavita Sharma','HC Mohan Trivedi','SI Ankit Patel',
  'ASI Sunita Rao','SI Manish Gupta','HC Dilip Solanki','PSI Rekha Nair',
  'SI Bharat Patel','HC Jignesh Modi','ASI Pooja Verma','SI Kiran Kumar',
  'PSI Sanjay Shah','HC Nita Pandya','SI Ashok Prajapati','PSI Leela Raj',
];

function generatePatrolUnits(count = 24) {
  const statuses = ['On Patrol','On Patrol','On Patrol','Responding','At Station','Standby'];
  const vehicles = ['PCR Van','Motorcycle','SUV','Jeep'];

  return Array.from({ length: count }, (_, i) => {
    const area = AREAS[i % AREAS.length];
    return {
      vehicle_id:       `AHD-PCR-${String(i + 1).padStart(3, '0')}`,
      officer_id:       `OFF-${String(1000 + i).padStart(4, '0')}`,
      officer_name:     OFFICER_NAMES[i % OFFICER_NAMES.length],
      current_location: { lat: parseFloat(jitter(area.lat, 0.01).toFixed(6)), lng: parseFloat(jitter(area.lng, 0.01).toFixed(6)) },
      area:             area.name,
      zone:             area.zone,
      status:           statuses[i % statuses.length],
      vehicle_type:     vehicles[i % vehicles.length],
      shift_time:       i % 3 === 0 ? '06:00–14:00' : i % 3 === 1 ? '14:00–22:00' : '22:00–06:00',
      incidents_handled:Math.floor(rand() * 8),
      last_update:      new Date(Date.now() - Math.floor(rand() * 3600000)).toISOString(),
    };
  });
}


// ─── HOTSPOTS (with temporal context) ────────────────────────────────────────
export function generateHotspots() {
  return [
    // Persistent high-crime zones
    { id:'HS-001', name:'Naroda Industrial Corridor', lat:23.0720, lng:72.6430, radius:850, risk:'Critical', score:94, crimes:487, primary_type:'Robbery',         trend:'+12%', emerged:'Jan 2023', zone:'East'    },
    { id:'HS-002', name:'Maninagar Junction Area',    lat:22.9960, lng:72.6055, radius:750, risk:'Critical', score:91, crimes:421, primary_type:'Chain Snatching', trend:'+8%',  emerged:'Jan 2023', zone:'South'   },
    { id:'HS-003', name:'Bapunagar Market Cluster',   lat:23.0540, lng:72.6175, radius:680, risk:'High',     score:83, crimes:356, primary_type:'Assault',         trend:'+6%',  emerged:'Mar 2023', zone:'East'    },
    { id:'HS-004', name:'Dariapur Old City',           lat:23.0315, lng:72.5970, radius:620, risk:'High',     score:78, crimes:312, primary_type:'Drug Offense',    trend:'+2%',  emerged:'Jan 2023', zone:'Central' },
    { id:'HS-005', name:'Asarwa Railway Corridor',     lat:23.0600, lng:72.6095, radius:580, risk:'High',     score:76, crimes:298, primary_type:'Theft',           trend:'-3%',  emerged:'Jan 2023', zone:'East'    },
    { id:'HS-006', name:'Gomtipur East Market',        lat:23.0270, lng:72.6310, radius:520, risk:'High',     score:72, crimes:267, primary_type:'Vehicle Theft',   trend:'+5%',  emerged:'May 2023', zone:'East'    },
    // Emerging hotspots (since mid-2024)
    { id:'HS-007', name:'Narol Industrial Zone',       lat:22.9700, lng:72.6200, radius:680, risk:'High',     score:74, crimes:285, primary_type:'Vehicle Theft',   trend:'+18%', emerged:'Jun 2024', zone:'South'   },
    { id:'HS-008', name:'Vatva GIDC Cluster',          lat:22.9600, lng:72.6400, radius:640, risk:'High',     score:70, crimes:265, primary_type:'Burglary',        trend:'+14%', emerged:'Aug 2024', zone:'South'   },
    // Moderate zones
    { id:'HS-009', name:'Isanpur Crossroads',          lat:22.9850, lng:72.6130, radius:480, risk:'Medium',   score:63, crimes:221, primary_type:'Assault',         trend:'+1%',  emerged:'Jan 2023', zone:'South'   },
    { id:'HS-010', name:'Nikol Highway Stretch',       lat:23.0510, lng:72.6540, radius:460, risk:'Medium',   score:58, crimes:198, primary_type:'Robbery',         trend:'-4%',  emerged:'Jan 2023', zone:'East'    },
    { id:'HS-011', name:'Vastral Bridge Vicinity',     lat:23.0265, lng:72.6590, radius:430, risk:'Medium',   score:54, crimes:176, primary_type:'Chain Snatching', trend:'+3%',  emerged:'Apr 2023', zone:'East'    },
    { id:'HS-012', name:'Ranip Junction',              lat:23.0940, lng:72.5625, radius:410, risk:'Medium',   score:49, crimes:154, primary_type:'Drug Offense',    trend:'+8%',  emerged:'Jul 2023', zone:'North'   },
    // Post-crackdown cooling zones
    { id:'HS-013', name:'Chandkheda Market',           lat:23.1190, lng:72.5920, radius:340, risk:'Low',      score:29, crimes:87,  primary_type:'Mobile Theft',    trend:'-18%', emerged:'Jan 2023', zone:'North'   },
    { id:'HS-014', name:'Shahibaug Junction',          lat:23.0660, lng:72.5910, radius:360, risk:'Low',      score:34, crimes:112, primary_type:'Theft',           trend:'-8%',  emerged:'Jan 2023', zone:'North'   },
    // New upscale area hotspot (2025)
    { id:'HS-015', name:'Satellite-Bodakdev Corridor', lat:23.0340, lng:72.5150, radius:580, risk:'High',     score:68, crimes:245, primary_type:'Vehicle Theft',   trend:'+22%', emerged:'Jan 2025', zone:'West'    },
  ];
}


// ─── ALERTS ───────────────────────────────────────────────────────────────────
export function generateAlerts(count = 50) {
  const templates = [
    { type:'Critical', title:'Crime Spike Detected',    msg:(a) => `Robbery incidents up 40% in ${a} in last 2 hours` },
    { type:'Critical', title:'New Hotspot Emerged',     msg:(a) => `New crime cluster detected near ${a} — 8 incidents in 1 hour` },
    { type:'Critical', title:'Armed Robbery Active',    msg:(a) => `Armed robbery in progress reported near ${a}` },
    { type:'High',     title:'Risk Threshold Breached', msg:(a) => `Risk score exceeded 85 in ${a}` },
    { type:'High',     title:'Patrol Gap Identified',   msg:(a) => `No patrol unit active in ${a} for 45+ mins` },
    { type:'High',     title:'Cyber Fraud Cluster',     msg:(a) => `UPI fraud cluster detected — 12 reports from ${a} in 3 hours` },
    { type:'High',     title:'Drug Peddling Alert',     msg:(a) => `Suspected drug peddling hub identified in ${a}` },
    { type:'Medium',   title:'Chain Snatching Alert',   msg:(a) => `3 chain snatching incidents near ${a} in 30 mins` },
    { type:'Medium',   title:'Vehicle Theft Pattern',   msg:(a) => `Multiple vehicle thefts near ${a} parking zone` },
    { type:'Medium',   title:'Festival Crowd Alert',    msg:(a) => `Large gathering near ${a} — increased patrol advised` },
    { type:'Low',      title:'Patrol Route Update',     msg:(a) => `AI-recommended patrol route updated for ${a} sector` },
    { type:'Low',      title:'Shift Change Alert',      msg:(a) => `Patrol handover scheduled for ${a} sector in 15 min` },
  ];

  const now = new Date();
  return Array.from({ length: count }, (_, i) => {
    const tpl = templates[i % templates.length];
    const area = AREAS[Math.floor(rand() * AREAS.length)].name;
    const minsAgo = Math.floor(rand() * 480);
    return {
      id:           `ALT-${String(i + 1).padStart(4, '0')}`,
      type:         tpl.type,
      title:        tpl.title,
      message:      tpl.msg(area),
      area,
      timestamp:    new Date(now.getTime() - minsAgo * 60000).toISOString(),
      acknowledged: rand() > 0.65,
      assigned_to:  rand() > 0.5 ? randomItem(OFFICER_NAMES) : null,
    };
  }).sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
}


// ─── AI PREDICTIONS ───────────────────────────────────────────────────────────
export function generatePredictions() {
  return [
    { area:'Naroda',          risk_level:'Critical', score:94, predicted_crimes:48, top_crime:'Robbery',         confidence:91, deployment:'4 units + 1 PCR van', lat:23.0695, lng:72.6415 },
    { area:'Maninagar',       risk_level:'Critical', score:89, predicted_crimes:42, top_crime:'Chain Snatching', confidence:88, deployment:'3 units + special team', lat:22.9970, lng:72.6043 },
    { area:'Bapunagar',       risk_level:'High',     score:81, predicted_crimes:34, top_crime:'Assault',         confidence:84, deployment:'3 units recommended', lat:23.0530, lng:72.6160 },
    { area:'Narol',           risk_level:'High',     score:74, predicted_crimes:28, top_crime:'Vehicle Theft',   confidence:80, deployment:'2 units + CCTV check', lat:22.9700, lng:72.6200 },
    { area:'Dariapur',        risk_level:'High',     score:72, predicted_crimes:26, top_crime:'Drug Offense',    confidence:78, deployment:'2 units recommended', lat:23.0310, lng:72.5960 },
    { area:'Satellite',       risk_level:'Medium',   score:68, predicted_crimes:22, top_crime:'Vehicle Theft',   confidence:74, deployment:'2 units — night shift', lat:23.0226, lng:72.5137 },
    { area:'Chandkheda',      risk_level:'Low',      score:29, predicted_crimes:7,  top_crime:'Mobile Theft',    confidence:68, deployment:'Standard patrol',       lat:23.1180, lng:72.5908 },
  ];
}


// ─── PATROL ROUTES ────────────────────────────────────────────────────────────
export function generatePatrolRoutes() {
  return [
    {
      id:'RT-001', vehicle_id:'AHD-PCR-001', name:'Naroda High-Risk Circuit', color:'#FF1744',
      waypoints:[
        { lat:23.0695, lng:72.6415, name:'Naroda PS (Start)' },
        { lat:23.0720, lng:72.6450, name:'Industrial Zone Entry' },
        { lat:23.0680, lng:72.6490, name:'Naroda Patiya' },
        { lat:23.0650, lng:72.6430, name:'Market Cluster' },
        { lat:23.0695, lng:72.6415, name:'Naroda PS (End)' },
      ],
      distance_km:8.4, coverage:'94%', eta_minutes:45,
    },
    {
      id:'RT-002', vehicle_id:'AHD-PCR-005', name:'Maninagar-Isanpur Route', color:'#FF6D00',
      waypoints:[
        { lat:22.9970, lng:72.6043, name:'Maninagar PS' },
        { lat:22.9920, lng:72.6100, name:'Station Road Jct.' },
        { lat:22.9860, lng:72.6130, name:'Isanpur Market' },
        { lat:22.9810, lng:72.6080, name:'Isanpur Crossing' },
        { lat:22.9970, lng:72.6043, name:'Maninagar PS' },
      ],
      distance_km:6.2, coverage:'87%', eta_minutes:35,
    },
    {
      id:'RT-003', vehicle_id:'AHD-PCR-010', name:'Central Ahmedabad Route', color:'#FFD600',
      waypoints:[
        { lat:23.0310, lng:72.5960, name:'Dariapur PS' },
        { lat:23.0350, lng:72.5910, name:'Teen Darwaja' },
        { lat:23.0395, lng:72.5613, name:'Navrangpura' },
        { lat:23.0328, lng:72.5716, name:'Ellis Bridge' },
        { lat:23.0310, lng:72.5960, name:'Dariapur PS' },
      ],
      distance_km:9.1, coverage:'78%', eta_minutes:52,
    },
  ];
}


// ─── ANALYTICS HELPERS ────────────────────────────────────────────────────────
export function getCrimesByType(crimes) {
  const counts = {};
  crimes.forEach(c => { counts[c.crime_type] = (counts[c.crime_type] || 0) + 1; });
  return Object.entries(counts).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value);
}

export function getCrimesByArea(crimes) {
  const counts = {};
  crimes.forEach(c => { counts[c.area] = (counts[c.area] || 0) + 1; });
  return Object.entries(counts).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value).slice(0, 10);
}

export function getCrimesByMonth(crimes) {
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const counts = Array(12).fill(0);
  crimes.forEach(c => { counts[(c.month || new Date(c.timestamp).getMonth() + 1) - 1]++; });
  return months.map((month, i) => ({ month, crimes: counts[i] }));
}

export function getCrimesByHour(crimes) {
  const counts = Array(24).fill(0);
  crimes.forEach(c => counts[c.hour || new Date(c.timestamp).getHours()]++);
  return counts.map((count, hour) => ({ hour: `${String(hour).padStart(2,'0')}:00`, count }));
}

export function getCyberByType(cybercrime) {
  const counts = {};
  cybercrime.forEach(c => { counts[c.fraud_type] = (counts[c.fraud_type] || 0) + 1; });
  return Object.entries(counts).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value);
}

export function getTotalAmountLost(cybercrime) {
  return cybercrime.reduce((sum, c) => sum + (c.amount_lost || 0), 0);
}

export function getDashboardStats(crimes, cybercrime, patrols, hotspots) {
  const now = new Date();
  const last24h = new Date(now.getTime() - 24 * 3600000);
  const recent = crimes.filter(c => new Date(c.timestamp) > last24h);
  return {
    total_crimes:      crimes.length,
    crimes_today:      recent.length,
    active_hotspots:   hotspots.filter(h => h.risk === 'Critical' || h.risk === 'High').length,
    high_risk_areas:   hotspots.filter(h => h.risk === 'Critical').length,
    active_patrols:    patrols.filter(p => p.status === 'On Patrol').length,
    total_patrols:     patrols.length,
    cybercrime_reports:cybercrime.length,
    cyber_today:       Math.floor(cybercrime.length * 0.04),
    critical_alerts:   recent.filter(c => c.severity === 'Critical').length,
    risk_index:        72,
    threat_level:      'HIGH',
  };
}


// ─── EXPORT PRE-GENERATED DATASETS ───────────────────────────────────────────
export const mockCrimes       = generateCrimes(10000);
export const mockCybercrime   = generateCybercrime(1200);
export const mockPatrolUnits  = generatePatrolUnits(24);
export const mockHotspots     = generateHotspots();
export const mockAlerts       = generateAlerts(50);
export const mockPredictions  = generatePredictions();
export const mockPatrolRoutes = generatePatrolRoutes();

export const dashboardStats   = getDashboardStats(
  mockCrimes, mockCybercrime, mockPatrolUnits, mockHotspots
);

// Map-optimized subset (first 2000 for performance)
export const mapCrimes    = mockCrimes.slice(0, 2000);
export const recentCrimes = [...mockCrimes]
  .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
  .slice(0, 20);
