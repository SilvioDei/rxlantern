r"""Start RxLantern (API + website) with one command.

From the rxcompass/ folder:  ..\.venv\Scripts\python.exe run.py
Then open http://127.0.0.1:8000
"""

import uvicorn

if __name__ == "__main__":
    print("RxLantern is starting at http://127.0.0.1:8000  (press Ctrl+C to stop)")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000)
