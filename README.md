# 🛡️ AI Resume Screener & Intelligence

An ultra-premium AI-powered resume screening and analysis tool.

## 🐳 Option 1: Running with Docker (Recommended)

When using Docker, you **do not** need to create or activate a virtual environment manually. Docker creates its own isolated environment inside the container.

### Fast Start
1.  **Build and start:**
    ```bash
    docker-compose build --no-cache
    docker-compose up
    ```
2.  **Access:** `http://localhost:8501`

---

## 🪟 Option 2: Running Natively on Windows (Local)

Use this if you want to run the code directly on your machine using your local Python installation.

1.  **Setup Virtual Environment:**
    ```powershell
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    ```
2.  **Install & Run:**
    ```powershell
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
    streamlit run app.py
    ```

---

## 🛠️ Docker Desktop GUI Tips
- Once started via terminal, the project `ai-resume-screener` will appear in your **Docker Desktop Dashboard**.
- You can stop/start it there with one click.
- You can view logs to see the AI processing in real-time.