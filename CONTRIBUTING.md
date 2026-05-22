# Contributing to Climate-Shield

Thank you for your interest in contributing. This file describes the minimal, practical steps to contribute fixes, improvements, or documentation to this repository. It reflects the current contents of the project (static frontend and two small Flask backends).

Please do not add configuration secrets (API keys, credentials) to the repository. Use environment variables or a local `.env` file in `backend/` when needed.

## Basic workflow

1. Fork the repository and clone your fork:

```bash
git clone <your-fork-url>
cd Climate-Shield
```

2. Create a branch for your change. Use descriptive names, for example:

```bash
git checkout -b feature/improve-ux
# or for a bugfix
git checkout -b fix/weather-api-error
```

3. Make your change in the workspace. Keep changes small and focused.

4. Test locally (see Local testing below).

5. Commit with a clear message and push your branch:

```bash
git add .
git commit -m "Short summary: what and why"
git push origin <your-branch>
```

6. Open a Pull Request from your branch into the repository's `main` branch. In the PR description include:
- What the change does
- Why it's needed
- How to test it locally (commands or screenshots)

## Opening issues

When opening an issue, include:
- A short, descriptive title
- Steps to reproduce the problem (if applicable)
- Expected vs actual behavior
- Any relevant logs or screenshots

## Local testing

This repository contains three runnable parts:

- Frontend static files in `Frontend/` (open `Index.html` or `Analysis/analysis.html`).
- Weather alert API in `backend/alertsystem.py` (Flask app).
- Chatbot API in `AI-chatbot/chatbot.py` (Flask app or CLI).

Recommended local test steps:

1. Create and activate a Python virtual environment and install dependencies:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

2. Start the weather API (default port 5000):

```bash
python backend/alertsystem.py
```

3. Start the chatbot API (default port 5001):

```bash
python AI-chatbot/chatbot.py --mode api --host 127.0.0.1 --port 5001
```

4. Serve or open the frontend:

- You can open `Frontend/Index.html` directly in the browser, but some browsers restrict fetch requests over `file://`. To avoid that, serve the folder:

```bash
cd Frontend
python -m http.server 8000
# open http://localhost:8000
```

5. Use the analysis page at `Frontend/Analysis/analysis.html` to test the `/weather` endpoint and the chatbot widget.

## Pull request checklist

Before requesting review, please ensure:

- [ ] Your PR targets `main` and contains a clear title and description.
- [ ] You included steps to test the change locally.
- [ ] You did not commit secrets or large binary files.
- [ ] If you modified documentation or added features, update `README.md` or add new docs.

## Coding style and tests

- There is no enforced test suite or linter configured in this repository. Follow the existing project style: plain JavaScript for frontend, readable and well‑documented Python for backends.
- If you add dependencies, update `requirements.txt` and mention them in the PR description.

## Contact and support

Open an issue for questions, feature requests, or help running the services.

Thank you for helping improve Climate-Shield.
