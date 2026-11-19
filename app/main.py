from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.campaigns import router as campaigns_router


app = FastAPI(title="Keitaro Wrapper")

templates = Jinja2Templates(directory="app/templates")


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


app.include_router(campaigns_router)