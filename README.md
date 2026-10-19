# WTQ 2026 Build Track: Utility Bill Decoder

AI-powered decoder for Pakistani electricity bills (K-Electric, LESCO, IESCO). The solution extracts structured billing details according to the required schema (Level 1) and answers customer questions with grounded explanations and mathematical calculations (Level 2).

## Runtime
- **Python Version:** Python 3.14 (compatible with Python 3.11+)

## Setup Instructions

1. Clone or extract the repository:
   ```bash
   cd "AI-Powered Application"
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. Install pinned dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your API key in a `.env` file:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set your Google AI Studio API key:
   ```env
   MODEL_PROVIDER=google
   MODEL_NAME=gemini-3.5-flash-lite
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```

## Execution Commands

### Running on Test Data (Default)
When test data is available inside `test/bills` and templates in `test/csv/`:
```bash
python main.py
```
This automatically runs Level 1 extraction and Level 2 question answering on the 10 test bills, dynamically reads `test/csv/level2.csv`, and writes the completed files to:
- `output/level1.csv`
- `output/level2.csv`

### Running on Custom Folders / Train Mode
To test on the sample training bills:
```bash
python main.py --mode train
```

### Validating Results
The pipeline runs built-in validation after generation. You can also re-validate the CSV outputs:
```bash
python -c "from core.validator import validate_level1_csv, validate_level2_csv; from pathlib import Path; print('L1:', validate_level1_csv(Path('output/level1.csv'))); print('L2:', validate_level2_csv(Path('output/level2.csv')))"
```

### Packaging for Submission
To build the official submission ZIP:
```bash
python package_submission.py
```
This generates `your-submission.zip` matching the required structure, excluding `.venv` and `.env`, and verifies that it is well under the 15 MB limit.

---

## Interactive Web Application (VoltDecoder UI)

A modern, light, premium SaaS dashboard for uploading utility bills, viewing interactive breakdowns, and chatting with the grounded Q&A engine.

### Launching the Web App (Windows PowerShell)

#### Option 1: Unified Single-Server Mode (Recommended)
FastAPI directly serves the compiled React dashboard and all REST API endpoints from a single port:

```powershell
# In project root:
.\.venv\Scripts\Activate.ps1
uvicorn api:app --reload --port 8000
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

#### Option 2: Full Development Mode (Hot-Reloading)
Run backend and frontend independently in two PowerShell terminals:

**Terminal 1 (FastAPI Backend):**
```powershell
.\.venv\Scripts\Activate.ps1
uvicorn api:app --reload --port 8000
```

**Terminal 2 (Vite React Frontend):**
```powershell
cd frontend
npm run dev
```
Open **[http://localhost:5173](http://localhost:5173)** in your browser.

---

## AI Usage Section

In accordance with Section 7.4 of the WTQ Build Track Participant Guide:

- **Allowed LLMs Used by Application:**
  - `gemini-3.5-flash-lite` (Google AI Studio)
- **Other AI Models / LLMs Used:**
  - none
- **Cloud Extraction Services (Azure prebuilt, Textract, Mindee):**
  - none (strictly avoided)
- **Local OCR Libraries:**
  - none (multimodal vision capabilities of Gemini 3.5 Flash-Lite used directly)
- **AI Coding Assistants Used to Write Code:**
  - Antigravity AI pair programming assistant
