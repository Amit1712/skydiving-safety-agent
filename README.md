# 🪂 Skydiving Safety Autonomous Agent

An intelligent, autonomous AI Agent built with Python and the **Google Gemini SDK** (`google-genai`). 

The agent accepts skydiving queries for any dropzone worldwide, autonomously searches for location coordinates, checks real-time weather and wind conditions, cross-references them against safety regulations (e.g., student AFF safety limits), and delivers a clear **Go / No-Go** safety verdict.

---

## 🏗️ Architecture & Project Structure

The project follows a clean, modular 3-tier software architecture (**Separation of Concerns**):

```text
skydiving-agent/
│
├── services/                 # 🌐 API Layer (Deterministic HTTP & External APIs)
│   ├── http_client.py        # Generic HTTP client with robust Error Handling & Timeouts
│   ├── weather_service.py     # Open-Meteo Weather API integration
│   ├── geocoding_service.py   # Open-Meteo Geocoding API integration
│   └── gemini_service.py     # Gemini Client lifecycle & chat orchestration
│
├── tools/                    # 🛠️ Agent Tool Layer (Wrappers exposed to Gemini)
│   └── skydiving_tools.py    # Function definitions, JSON parsing & error formatting
│
├── agent.py                  # 🚀 Core CLI Execution & Interactive Agent Loop
├── .env                      # Environment variables (API Keys)
├── requirements.txt          # Python dependencies
└── README.md

```

---



## ✨ Features & Capabilities

- **Autonomous Tool Calling (ReAct Loop):** The LLM independently determines which tools to invoke and in what order based on context.
- **Geocoding Support:** Accepts human-readable locations (e.g., *"Dead Sea dropzone"*, *"Prague"*) and resolves them to exact coordinates.
- **Real-Time Weather Integration:** Fetches live temperature, wind speed, and wind gusts using the free **Open-Meteo API** (no API keys required for weather/geocoding).
- **Safety Decision Logic:** Cross-references wind data against predefined safety thresholds for AFF students.
- **Resilient Error Handling:** External API errors (timeouts, 404s) are caught and formatted into structured JSON error payloads, preventing LLM crashes and allowing the agent to gracefully adapt.
- **Flexible CLI:** Supports single-prompt queries via CLI flags or a continuous interactive chat session.

---



## 🛠️ Prerequisites & Installation

1. **Clone or navigate to the project directory:**

```bash
cd skydiving-agent

```

1. **Create and activate a Python virtual environment:**

```bash
python -m venv venv

# Mac/Linux:
source venv/bin/activate

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

```

1. **Install dependencies:**

```bash
pip install google-genai python-dotenv requests

```

1. **Configure Environment Variables:**

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here

```

> 💡 *Get a free API key from [Google AI Studio](https://aistudio.google.com/?utm_source=gemini).*

---



## 🚀 Usage



### 1. Single Prompt Execution (`-p` / `--prompt`)

Pass a query directly from your terminal:

```bash
python agent.py -p "I am an AFF student. Can I jump right now at the Dead Sea dropzone?"

```



### 2. Interactive CLI Mode (`-i` / `--interactive`)

Run a continuous chat loop in the terminal:

```bash
python agent.py -i

```

**Example Conversation:**

```text
🪂 Skydiving Safety Agent - Interactive CLI Mode
Type 'exit' or 'quit' to stop.
==================================================

[You]: Can I jump right now at the Dead Sea as an AFF student?

🤖 [Agent Decision]: Calling Tool 'get_dz_coordinates_tool' with args {'location_name': 'Dead Sea'}
📡 [Tool Result]: {"status": "success", "data": {"latitude": 31.05, "longitude": 35.36}}

🤖 [Agent Decision]: Calling Tool 'get_weather_and_wind_tool' with args {'latitude': 31.05, 'longitude': 35.36}
📡 [Tool Result]: {"status": "success", "data": {"wind_speed_kmh": 14.2, "wind_gusts_kmh": 18.5}}

🤖 [Agent Decision]: Calling Tool 'get_aff_student_safety_limits_tool' with args {}
📡 [Tool Result]: {"status": "success", "data": {"max_allowed_wind_speed_kmh": 25}}

[Agent Final Answer]:
Based on current weather data at the Dead Sea dropzone:
- Surface Wind: 14.2 km/h (Gusts up to 18.5 km/h)
- AFF Student Limit: 25 km/h

Verdict: GO 🪂
Current wind conditions are well within your student safety limits.

```

---



## ⚙️ Key Technical Stack

- **Language:** Python 3.10+
- **LLM Engine:** Google Gemini (`gemini-3.1-flash-lite`) via `google-genai` SDK
- **Data & Geocoding APIs:** Open-Meteo REST APIs
- **Design Patterns:** ReAct (Reason + Act), 3-Tier Layered Architecture, Structured Output Parsing

