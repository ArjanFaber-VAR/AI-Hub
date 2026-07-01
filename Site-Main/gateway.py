from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI()


# -------------------------
# HOME
# -------------------------
@app.get("/")
def home():
    return {
        "message": "AI Gateway running",
        "routes": {
            "f3": "http://localhost:8083",
            "chat": "http://localhost:8084",
            "tools": "http://localhost:8085",
            "api": "http://localhost:5001"
        }
    }


# -------------------------
# REDIRECT ROUTES
# -------------------------

@app.get("/f3")
def f3():
    return RedirectResponse(url="http://localhost:8083/")


@app.get("/chat")
def chat():
    return RedirectResponse(url="http://localhost:8084/")


@app.get("/tools")
def tools():
    return RedirectResponse(url="http://localhost:8085/")


@app.get("/api")
def api():
    return RedirectResponse(url="http://localhost:5001/")