# MIST-JP/ES
Pragmatic Neural Machine Translation (Japanese to Spanish).

This project uses a modular machine learning pipeline to analyze the intent and tone of a Japanese dialogue to provide a context-aware and pragmatic translation to Spanish.

## Prerequisites
- Python 3.9+
- Node.js (for the frontend UI)
- **Git LFS** (Crucial: the classification models are stored using Git LFS. If you don't use Git LFS, the models will be downloaded as tiny pointer files and the backend will fail to start).

## Getting Started

### 1. Clone the repository
Since the models are large (~850 MB), make sure you have Git LFS installed and pull the models after cloning.
```bash
git clone git@github.com:unmsm8182/mist-jp-es.git
cd mist-jp-es
git lfs pull
```

### 2. Backend Setup (FastAPI + ML Pipeline)
Create a virtual environment, install the dependencies, and start the server.
```bash
python -m venv .venv
source .venv/bin/activate
make install
# o alternativamente: pip install -r requirements.txt

python server.py
```
The API will run at `http://localhost:8000`. It will take a few seconds to load the models into memory during startup.

### 3. Frontend Setup (React + Vite)
In a new terminal window, navigate to the `ui` directory to start the frontend interface.
```bash
cd ui
npm install
npm run dev
```
The application will be available at `http://localhost:5173`.
