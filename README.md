# Motor Insurance Claim Triage Assistant

---

## Setup Instructions

1. Clone the repository
```bash
git clone https://github.com/your-username/claim-triage.git
cd claim-triage
```

2. Create virtual environment
```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create `.env` file in the root folder
```
OPENAI_API_KEY=sk-your-api-key-here
```

> Never commit your `.env` file. It is already listed in `.gitignore`.

---

## Dependencies

```
openai
streamlit
python-dotenv
```

Install all with:
```bash
pip install -r requirements.txt
```

---

## How to Run

**Streamlit app**
```bash
streamlit run app.py
```

Browser will open automatically at `http://localhost:8501`

**Jupyter notebook prototype**
```bash
jupyter notebook notebook/prototype.ipynb
```

---

## Model and API Used

| Item | Detail |
|------|--------|
| Model | OpenAI GPT-4o-mini |
| API | OpenAI Chat Completions API |
| Temperature | 0.0 (for consistent output) |
| Max Tokens | 1000 per request |

---

## Assumptions

1. Policy rules are static and sourced directly from the assignment PDF.
2. Input is text-based only. Actual document files (PDFs, images) are not processed.
3. Dates must be entered in YYYY-MM-DD format for accurate day calculation.
4. English language is used for all prompts and outputs.
5. Policy rules are short enough to be injected directly into the System Prompt. No RAG pipeline is required for this prototype.
6. GPT-4o-mini provides sufficient reasoning capability for structured rule-based triage at the prototype level.

---

## Limitations

1. The system cannot verify whether submitted documents are authentic. It only checks whether required document types are mentioned in the input.
2. Actual PDF or image files cannot be uploaded or read.
3. Policy rules must be manually updated in code if they change.
4. Minor output variance may occur across runs even at temperature=0.0 due to floating-point differences in OpenAI infrastructure.
5. No audit trail or logging is implemented. Production systems would require full logging of AI recommendations and officer decisions.
6. No authentication or role-based access control is included.
7. The AI assistant does not make final claim decisions. All recommendations require human review by a claim officer.