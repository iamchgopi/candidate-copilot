from aggregator import analyze_job_search
import uuid
import shutil
import os
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from jd_parser import parse_jd
from match_agent import match_jd
from mock_interview import generate_question, judge_answer
from ingest import ingest_resume

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)


class JDRequest(BaseModel):
    jd_text: str
    user_id: str


class QuestionRequest(BaseModel):
    jd_text: str
    asked_so_far: list[str] = []


class FeedbackRequest(BaseModel):
    question: str
    answer: str

class BatchJDRequest(BaseModel):
    jd_list: list[str]
    user_id: str


@app.post("/analyze-job-search")
def analyze_job_search_endpoint(req: BatchJDRequest):
    return analyze_job_search(req.jd_list, user_id=req.user_id)

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Accepts a PDF upload, extracts it, and stores it under a new random user_id."""
    user_id = str(uuid.uuid4())[:8]
    save_path = f"uploads/{user_id}.pdf"

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    chunk_count = ingest_resume(save_path, user_id=user_id)

    return {"user_id": user_id, "chunks_stored": chunk_count}


@app.post("/parse-jd")
def parse_jd_endpoint(req: JDRequest):
    return parse_jd(req.jd_text)


@app.post("/match")
def match_endpoint(req: JDRequest):
    return match_jd(req.jd_text, user_id=req.user_id)


@app.post("/interview/question")
def question_endpoint(req: QuestionRequest):
    parsed = parse_jd(req.jd_text)
    question = generate_question(parsed, req.asked_so_far)
    return {"question": question}


@app.post("/interview/feedback")
def feedback_endpoint(req: FeedbackRequest):
    feedback = judge_answer(req.question, req.answer)
    return {"feedback": feedback}