# 🤖 InsightAI — India Life Insurance Intelligence Dashboard

> Conversational AI for Instant Business Intelligence Dashboards

![Tech Stack](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square)
![AI](https://img.shields.io/badge/AI-Gemini%20%2F%20Claude-4285F4?style=flat-square)
![Charts](https://img.shields.io/badge/Charts-Chart.js-FF6384?style=flat-square)
![Data](https://img.shields.io/badge/Data-India%20Life%20Insurance%20Claims-orange?style=flat-square)

---

## 📁 Project Structure

```
ai-dashboard/
│
├── backend/
│   ├── main.py           # FastAPI server — REST API endpoints
│   ├── gemini_query.py   # Gemini AI integration: NL → SQL + insights
│   └── database.py       # SQLite in-memory DB + data access layer
│
├── frontend/
│   └── index.html        # Full-stack SPA dashboard (Chart.js + AI chat)
│
├── data/
│   └── sales_data.csv    # India Life Insurance Claims dataset (IRDAI)
│
├── requirements.txt      # Python dependencies
└── README.md
```

---

## 🏗 Architecture Blueprint

```
User Query (Natural Language)
        ↓
Frontend (index.html — SPA Dashboard)
        ↓
Backend API (FastAPI — main.py)
        ↓
LLM Engine (Gemini AI — gemini_query.py)
        ↓
SQL Query Generation
        ↓
Database (SQLite in-memory — database.py)
        ↓
Data Returned (JSON)
        ↓
Chart Generator (Chart.js — 6 interactive charts)
        ↓
Interactive Dashboard (Rendered in browser)
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your Gemini API Key
```bash
export GEMINI_API_KEY="your-key-here"
```

### 3. Start the Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 4. Open the Dashboard
```
Open frontend/index.html in your browser
# OR navigate to http://localhost:8000/static/index.html
```

---

## 📊 Dataset

**Source:** India Life Insurance — Individual Death Claims (IRDAI)  
**File:** `data/sales_data.csv`  
**Coverage:** 2017-18 → 2021-22 | 20+ insurers | ~150 records

**Key Columns:**
| Column | Description |
|---|---|
| `life_insurer` | Insurance company name |
| `year` | Financial year (e.g., 2021-22) |
| `total_claims_no` | Total claims received |
| `claims_paid_no` | Claims settled/paid |
| `claims_paid_amt` | Amount paid in ₹ Crore |
| `claims_paid_ratio_no` | Settlement ratio (0–1 scale) |
| `claims_repudiated_no` | Claims denied after investigation |
| `claims_pending_end_no` | Pending at year end |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/data` | Filtered claims records |
| GET | `/api/kpis` | KPI summary metrics |
| GET | `/api/trend` | Year-over-year trends |
| GET | `/api/insurers` | List of all insurers |
| POST | `/api/ask` | AI natural language query |
| GET | `/api/health` | Health check |

---

## 💡 Example AI Questions

- *"Which insurer had the highest claims paid ratio in 2021-22?"*
- *"Compare HDFC Life vs ICICI Prudential over 5 years"*
- *"Which insurer improved the most from 2017 to 2022?"*
- *"What is the total amount paid by SBI Life?"*
- *"Show insurers with repudiation rate above 5%"*

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Vanilla JS |
| Charts | Chart.js 4.x |
| AI (NL→SQL) | Google Gemini 1.5 Flash |
| AI (Fallback) | Anthropic Claude API |
| Backend | Python + FastAPI |
| Database | SQLite (in-memory) |
| Data | CSV → Pandas → SQLite |

---

*Built for the Conversational AI BI Dashboard project — India Life Insurance Claims Intelligence*