from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from jd_parser import parse_jd
from match_agent import match_jd
from mock_interview import generate_question, judge_answer

app = FastAPI()

# Allows our browser page to talk to this server (otherwise browsers block it by default)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class JDRequest(BaseModel):
    jd_text: str

class QuestionRequest(BaseModel):
    jd_text: str
    asked_so_far: list[str] = []

class FeedbackRequest(BaseModel):
    question: str
    answer: str


@app.post("/parse-jd")
def parse_jd_endpoint(req: JDRequest):
    return parse_jd(req.jd_text)


@app.post("/match")
def match_endpoint(req: JDRequest):
    return match_jd(req.jd_text)


@app.post("/interview/question")
def question_endpoint(req: QuestionRequest):
    parsed = parse_jd(req.jd_text)
    question = generate_question(parsed, req.asked_so_far)
    return {"question": question}


@app.post("/interview/feedback")
def feedback_endpoint(req: FeedbackRequest):
    feedback = judge_answer(req.question, req.answer)
    return {"feedback": feedback}