import sys
from fastapi import FastAPI

app = FastAPI()


@app.get("/py-version")
def py_version():
    return {"python_version": sys.version}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "teen-poll-backend running"}
