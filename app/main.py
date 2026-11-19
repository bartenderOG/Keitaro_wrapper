from fastapi import FastAPI

app = FastAPI(title="Keitaro Wrapper")


@app.get("/health")
def health_check():
    return {"status": "ok"}