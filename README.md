# MindEaseAI-Agent (Prototype)

MindEaseAI-Agent is a prototype AI Mental Health Assistant (voice + text). Use for demo / hackathon only.

## Quick start
1. Copy `.env.example` to `.env` and fill API keys.
2. Create virtual env & install:
   python -m venv venv
   source venv/Scripts/activate   # on Git Bash
   pip install -r requirements.txt
3. Run backend:
   uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
4. Open frontend/index.html in your browser (or serve it via simple http server).

## Notes
- This is for demo only. Not a clinical product.
- Add consent screen + helplines before testing with real users.
