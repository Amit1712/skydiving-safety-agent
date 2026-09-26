# 🗺️ Skydiving Safety Agent - Product & Feature Roadmap

This roadmap outlines the planned future enhancements for the Skydiving Safety Autonomous Agent.

---

## 🎯 Phase 1: Architecture & UX Improvements (Completed ✅)
- [x] Implement Rich CLI Output (Panels, Colored Verdicts, Spinners).
- [x] Conversation Memory support in interactive mode (`-i`).
- [x] Centralized configuration (`config.py`).
- [x] Output Guardrails for explicit `GO / NO-GO` verdicts.

---

## 🛠️ Phase 2: Advanced Domain Tools & Meteorological Data (Completed ✅)
- [x] **Aviation Weather Integration (METAR / TAF):**
  - Add tool to query aviation weather stations near dropzones (using CheckWX API).
- [x] **Hourly Weather Forecast:**
  - Support specific jump timestamps (e.g., *"Can I jump today at 15:00?"*).
- [x] **Sun Phase Calculator (Daylight Verification):**
  - Verify civil twilight / sunset times to ensure jumps occur during daylight hours.
- [x] **Cloud Ceiling & Visibility Check (VMC Rules):**
  - Validate cloud base heights against minimum altitude safety requirements.
- [x] **Improved Dropzone Geocoding:**
  - Curated dropzone registry, Nominatim/OSM search, and confidence scoring.
- [x] **Wind in Knots:**
  - All wind outputs now include both km/h and knots.

---

## 🪂 Phase 3: Dynamic Safety Rules & License Support (Completed ✅)
- [x] **Multi-License Support:**
  - Differentiate safety limits for AFF Students, License A/B, License C/D, and Tandem Instructors.
  - Default to AFF student regulations when the user does not specify a license in their prompt.
- [x] **Custom Dropzone Rules Engine (`data/safety_rules.yaml`):**
  - Allow dropzones to supply custom safety limits via YAML overrides (e.g., local DZ canopy limits).

---

## 🌐 Phase 4: Web Interface & API Integration
- [ ] **FastAPI Backend:**
  - Wrap the agent logic in a RESTful / WebSocket API.
- [ ] **Web Dashboard (Streamlit / React):**
  - Interactive UI with maps showing DZ conditions and wind vectors.