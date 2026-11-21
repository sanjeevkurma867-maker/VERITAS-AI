from pathlib import Path
from threading import BoundedSemaphore
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

if __package__:
    from .claims import MAX_ANSWER_LENGTH
    from .demo import demo_report
    from .report_models import DemoResponse, VerifyResponse
    from .verifier import VerificationTimeout, VerificationUnavailable, verify_answer
else:
    from claims import MAX_ANSWER_LENGTH
    from demo import demo_report
    from report_models import DemoResponse, VerifyResponse
    from verifier import VerificationTimeout, VerificationUnavailable, verify_answer


app = FastAPI(
    title="VERITAS AI",
    description="Temporal Claim Intelligence for AI answers",
    version="2.0.0",
)
capacity = BoundedSemaphore(3)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class VerifyRequest(BaseModel):
    answer: str = Field(min_length=3, max_length=MAX_ANSWER_LENGTH)


@app.get("/")
def home():
    return {"message": "Welcome to VERITAS AI", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "VERITAS AI Backend"}


@app.get("/demo", response_model=DemoResponse)
def demo(scenario: Literal["pluto", "python", "mixed"] = "pluto"):
    return demo_report(scenario)


@app.post("/verify", response_model=VerifyResponse)
def verify(request: VerifyRequest):
    if not capacity.acquire(blocking=False):
        raise HTTPException(status_code=429, detail="Verification is busy. Try again shortly.")
    try:
        return verify_answer(request.answer)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from None
    except VerificationTimeout as error:
        raise HTTPException(status_code=504, detail=str(error)) from None
    except VerificationUnavailable as error:
        raise HTTPException(status_code=503, detail=str(error)) from None
    finally:
        capacity.release()


dashboard = Path(__file__).resolve().parents[1] / "frontend" / "dist"
if dashboard.is_dir():
    app.mount("/app", StaticFiles(directory=dashboard, html=True), name="dashboard")
else:
    @app.get("/app/")
    def frontend_setup():
        raise HTTPException(status_code=503, detail="Build the dashboard with npm --prefix frontend run build, then restart FastAPI.")
