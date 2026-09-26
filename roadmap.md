# 🗺️ Skydiving Safety Agent - Product & Feature Roadmap

This roadmap outlines the planned future enhancements for the Skydiving Safety Autonomous Agent.

---

## 🎯 Phase 1: Architecture & UX Improvements (Completed ✅)
- [x] Implement Rich CLI Output (Panels, Colored Verdicts, Spinners).
- [x] Conversation Memory support in interactive mode (`-i`).
- [x] Centralized configuration (`config.py`).
- [x] Output Guardrails for explicit `GO / NO-GO` verdicts.

---

## 🛠️ Phase 2: Advanced Domain Tools & Meteorological Data
- [ ] **Aviation Weather Integration (METAR / TAF):**
  - Add tool to query aviation weather stations near dropzones (using CheckWX API).
- [ ] **Hourly Weather Forecast:**
  - Support specific jump timestamps (e.g., *"Can I jump today at 15:00?"*).
- [ ] **Sun Phase Calculator (Daylight Verification):**
  - Verify civil twilight / sunset times to ensure jumps occur during daylight hours.
- [ ] **Cloud Ceiling & Visibility Check (VMC Rules):**
  - Validate cloud base heights against minimum altitude safety requirements.

---

## 🪂 Phase 3: Dynamic Safety Rules & License Support
- [ ] **Multi-License Support:**
  - Differentiate safety limits for AFF Students, License A/B, License C/D, and Tandem Instructors.
- [ ] **Custom Dropzone Rules Engine (`config.yaml`):**
  - Allow dropzones to supply custom safety limits via YAML files (e.g., local DZ canopy limits).

---

## 🌐 Phase 4: Web Interface & API Integration
- [ ] **FastAPI Backend:**
  - Wrap the agent logic in a RESTful / WebSocket API.
- [ ] **Web Dashboard (Streamlit / React):**
  - Interactive UI with maps showing DZ conditions and wind vectors.