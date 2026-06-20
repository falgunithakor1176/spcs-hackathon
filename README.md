# 🚔 SPCS — Smart Policing Command System

**GIS Crime Hotspot Mapping and Predictive Patrol Routing System**
*Ahmedabad City Police Department*

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Start development server
npm run dev

# 3. Open browser at http://localhost:3000
```

---

## 🔐 Demo Login Accounts

| Role | Username | Password |
|------|----------|----------|
| Admin (Commissioner) | `commissioner` | `admin123` |
| Crime Analyst | `analyst` | `analyst123` |
| Patrol Officer | `officer` | `officer123` |
| Cyber Analyst | `cyber` | `cyber123` |

---

## 📁 Project Structure

```
src/
├── components/
│   ├── layout/        # Sidebar, TopHeader, AppLayout
│   ├── panels/        # LeftPanel, RightPanel (Command Center)
│   ├── map/           # CommandMap (Leaflet GIS)
│   ├── charts/        # BottomPanel (tabbed analytics)
│   └── widgets/       # StatCard, etc.
├── pages/
│   ├── Login.jsx          # Futuristic login screen
│   ├── CommandCenter.jsx  # Main GIS-first command view
│   ├── CrimeAnalytics.jsx # Crime trend analysis
│   ├── CyberCrime.jsx     # Cybercrime intelligence
│   ├── PatrolRouting.jsx  # Patrol route optimizer
│   ├── Alerts.jsx         # Alert center
│   └── Settings.jsx       # Admin settings
├── data/
│   └── mockData.js    # 10,000 Ahmedabad crime records generator
└── context/
    └── AuthContext.jsx # JWT-ready auth (mock)
```

---

## 🗺️ Features (Phase 1)

### Command Center
- Live GIS map (Leaflet + OpenStreetMap Dark)
- Crime incident markers (color-coded by severity)
- Hotspot zone overlays (animated risk circles)
- Patrol vehicle tracking
- AI-optimized patrol routes
- Left panel: incidents, filters, hotspot summary
- Right panel: AI predictions, live risk scores, alert feed
- Bottom: tabbed analytics charts

### Crime Analytics
- Monthly crime trends
- Hourly crime patterns
- Area-wise breakdown
- Severity distribution
- Crime type analysis

### Cybercrime Intelligence
- Fraud type distribution
- Monthly trend analysis
- Platform breakdown (WhatsApp, Telegram, etc.)
- Victim demographics
- Cyber vs. Physical crime correlation

### Patrol Routing
- Route selection panel
- Live patrol unit tracker
- Dijkstra/A* algorithm info
- Waypoint visualization on map

### Alert Center
- Severity-filtered alert list
- Acknowledge workflow
- Search functionality

### Settings (Admin only)
- Alert notification config
- ML threshold tuning (DBSCAN params)
- Security settings
- Map configuration

---

## 🎨 Design System

- **Theme**: Professional Police Command Center (dark)
- **Primary BG**: `#081120` (Deep Navy)
- **Accent**: `#00D4FF` (Electric Blue)
- **Critical**: `#FF1744` | **High**: `#FF6D00` | **Medium**: `#FFD600` | **Low**: `#00E676`
- **Fonts**: Orbitron (headings) + Inter (body) + JetBrains Mono (data)
- **Effects**: Glassmorphism, HUD corners, scan lines, glow effects, pulse animations

---

## 📊 Mock Data

Generated using seeded random (reproducible):
- **10,000** Ahmedabad crime incidents (2023–2025)
- **1,200** cybercrime reports
- **24** patrol units across city
- **15** pre-computed hotspot zones
- **50** alert notifications
- **7** AI prediction entries
- **3** patrol routes

Data covers **25 Ahmedabad areas** weighted by real crime density (Naroda, Maninagar, Bapunagar = high density; Satellite, Bopal, Bodakdev = low density).

---

## 📦 Tech Stack (Phase 1)

| Package | Version | Purpose |
|---------|---------|---------|
| React | 18.x | UI framework |
| Vite | 5.x | Build tool |
| Tailwind CSS | 3.x | Styling |
| React Router | 6.x | Routing |
| Leaflet + React-Leaflet | 1.9.x / 4.x | GIS maps |
| Recharts | 2.x | Charts |
| Lucide React | latest | Icons |
| date-fns | 3.x | Date utilities |

---

## 🔮 Upcoming Phases

- **Phase 2**: Flask REST API + JWT authentication
- **Phase 3**: PostgreSQL + PostGIS spatial database
- **Phase 4**: Real data API integration
- **Phase 5**: DBSCAN hotspot detection + Random Forest prediction
- **Phase 6**: Patrol route optimization (NetworkX + OSMnx)
- **Phase 7**: Real-time WebSocket alerts
- **Phase 8**: Docker deployment
