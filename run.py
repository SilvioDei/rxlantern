r"""Start RxLantern (API + website) with one command.

From the repository folder:
    Windows:      .venv\Scripts\python.exe run.py
    Mac / Linux:  .venv/bin/python run.py
Then open http://127.0.0.1:8000 (or the port in RXLANTERN_PORT).
"""

import os
import sys

if sys.version_info < (3, 11):
    sys.exit(f"RxLantern needs Python 3.11 or newer (this is Python {sys.version.split()[0]}). See README.md.")

import uvicorn  # noqa: E402

if __name__ == "__main__":
    from backend import config  # loads .env from this folder or the folder one level above

    port = int(os.getenv("RXLANTERN_PORT") or 8000)
    if not os.getenv("PORTKEY_API_KEY", "").strip():
        print("Note: PORTKEY_API_KEY was not found (put it in a .env file in this folder or the folder above it).\n"
              "      Every page works, but the 'Ask RxLantern' chat will not answer until the key is set.")
    else:
        print(f"PORTKEY_API_KEY loaded from {config.ENV_FILE or 'the environment'}.")
    print(f"RxLantern is starting at http://127.0.0.1:{port}  (the first start builds the database: a few seconds)")
    print("Press Ctrl+C to stop.")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=port)
