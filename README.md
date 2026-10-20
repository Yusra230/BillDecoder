# BillDecoder ⚡
### AI-Powered Utility Bill Intelligence for Pakistan

BillDecoder is an AI-powered web application that transforms Pakistani electricity bills into structured, understandable, and actionable information. Built for the **Women Tech Quest (WTQ) 2026 Build Track**, it supports bills from K-Electric (KE), LESCO, and IESCO, combining multimodal AI extraction with grounded question answering and mathematical calculations.

---

## 1. Problem Statement

Electricity bills contain a large amount of information, including meter readings, consumption units, tariff details, taxes, adjustments, and payment deadlines. For many consumers, understanding these details and verifying their charges can be difficult and time-consuming.

Traditional bill processing also presents challenges when extracting consistent data from differently formatted bills or answering questions that require calculations based on the actual bill.

**The challenge:** How can we turn unstructured electricity bills into reliable structured data while making billing information easier for consumers to understand?

## 2. The Solution

BillDecoder provides a unified workflow for extracting, exploring, and understanding electricity bills through an interactive web application.

- **AI-powered extraction:** Converts supported electricity bills into structured JSON following the required Level 1 schema.
- **Grounded question answering:** Answers customer questions using information extracted from the bill.
- **Mathematical calculations:** Supports calculation-based answers grounded in available bill data.
- **Interactive bill dashboard:** Presents billing information through organized cards, tables, and visualizations.
- **Bill management:** Allows users to review uploaded bills and revisit their extracted information.
- **Data export:** Provides structured JSON export for further analysis and integration.
- **Input validation:** Rejects unsupported files and detects duplicate uploads to help prevent invalid or repeated records.

## 3. Key Features

### Structured Bill Extraction
Extracts available billing information into a consistent structure designed around the competition's Level 1 requirements.

### Grounded AI Assistant
Lets users ask questions about their electricity bills and receive explanations based on the extracted bill information rather than relying solely on general model knowledge.

### Interactive Dashboard
Displays important billing details, itemized charges, taxes, meter information, and consumption trends in a clean, responsive interface.

### Bill Validation and Duplicate Detection
Validates incoming files and checks for duplicate uploads before saving new records.

### Export and Bill History
Supports reviewing previously processed bills and exporting extracted data as JSON.

## 4. How It Works

1. **Upload:** The user uploads a supported electricity bill.
2. **Validate:** The application checks whether the input is suitable for bill processing and whether it has already been uploaded.
3. **Extract:** Gemini's multimodal capabilities analyze the bill and extract available information.
4. **Structure:** The extracted information is organized into the required schema and validated.
5. **Explore:** The user reviews the bill through the dashboard and its detailed breakdowns.
6. **Ask questions:** The user queries the bill assistant for grounded explanations and calculations.
7. **Export:** The user can export the extracted data for downstream use.

## 5. Technical Approach

BillDecoder combines a Python-based AI processing pipeline with a React frontend and FastAPI backend.

### AI and Data Processing
- Multimodal bill understanding using Google Gemini
- Schema-based structured extraction
- Grounded question-answering engine
- Validation of extracted information and generated outputs
- CSV generation for the competition's Level 1 and Level 2 tasks

### Web Application
- REST API for bill uploads, bill retrieval, Q&A, and JSON export
- File validation and duplicate detection
- Local storage for uploaded files and processed bill records
- Interactive dashboard with bill details, charts, and question-answering interface

## 6. Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React 19, Vite, Tailwind CSS, Lucide |
| Data Visualization | Recharts |
| Backend | Python, FastAPI |
| AI Model | Google Gemini (`gemini-3.5-flash-lite`, as configured) |
| Data Processing | Python, JSON, CSV |
| Development Tools | Git, npm, Python virtual environments |

## 7. Architecture

```text
User
  |
  v
React Dashboard
  |
  v
FastAPI REST API
  |
  +--> File Validation & Duplicate Detection
  |
  +--> Gemini Multimodal Extraction
  |
  +--> Structured Data & Schema Validation
  |
  +--> Grounded Q&A & Calculations
  |
  +--> Local File Storage & JSON Export
```

The FastAPI application can also serve the compiled React frontend, allowing the web application and API to run from a single server.

## 8. Project Structure

```text
AI-Powered Application/
├── api.py
├── main.py
├── requirements.txt
├── core/
│   ├── config.py
│   ├── extractor.py
│   ├── qa_engine.py
│   ├── schemas.py
│   ├── validator.py
│   └── csv_writer.py
├── frontend/
│   ├── src/
│   ├── package.json
│   └── ...
├── test/
├── output/
└── package_submission.py
```

*The structure above highlights the main components. The exact contents may vary with the repository.*

## 9. Getting Started

### Prerequisites

- Python 3.11 or newer, subject to dependency compatibility
- Node.js and npm
- A Google AI Studio API key

Use the Python version tested successfully with your project's pinned dependencies.

### 1. Clone the Repository

```bash
git clone https://github.com/Yusra230/BillDecoder.git
cd "AI-Powered Application"
```

### 2. Create a Virtual Environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the location expected by your backend configuration. If `.env.example` is provided, copy it and update the values.

```env
MODEL_PROVIDER=google
MODEL_NAME=gemini-3.5-flash-lite
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

**Security:** Never commit your actual `.env` file or API key to GitHub.

### 5. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 6. Build the Frontend

```bash
npm run build
```

Return to the project root before running the backend.

## 10. Running the Application

### Option A: Unified Server

From the project root, activate the virtual environment and run:

```powershell
uvicorn api:app --reload --port 8000
```

Open [http://localhost:8000](http://localhost:8000).

This option requires the frontend build to be available at the location expected by FastAPI.

### Option B: Development Mode

Run the backend in one terminal:

```powershell
uvicorn api:app --reload --port 8000
```

Run the frontend in a second terminal:

```powershell
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

## 11. Competition Pipeline

BillDecoder also includes a command-line pipeline for the WTQ Build Track's Level 1 extraction and Level 2 question-answering tasks.

```bash
python main.py
```

Run in training mode:

```bash
python main.py --mode train
```

Validate the generated CSV files:

```bash
python -c "from core.validator import validate_level1_csv, validate_level2_csv; from pathlib import Path; print('L1:', validate_level1_csv(Path('output/level1.csv'))); print('L2:', validate_level2_csv(Path('output/level2.csv')))"
```

## 12. Testing

The repository includes test scripts covering areas such as API endpoints, bill extraction, question answering, and input validation.

Run the relevant tests using the commands and dependencies supported by the repository. Ensure any required sample data and environment variables are configured first.

## 13. Limitations and Future Improvements

Potential next steps include:

- Persistent cloud storage for uploaded bills and processed records
- Database-backed bill history and user accounts
- Stronger validation for uncertain or incomplete AI extractions
- Expanded testing across bill formats and edge cases
- Production deployment with appropriate security, monitoring, and error handling

The current application uses local file storage, so uploaded bills and history should not be assumed to persist across all hosting environments.

## 14. Acknowledgements

Developed for the **Women Tech Quest 2026 Build Track: Build with AI**.

---

**BillDecoder** — Making electricity bills easier to understand, one bill at a time.
