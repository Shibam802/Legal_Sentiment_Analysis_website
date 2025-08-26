import os


os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import torch

from legal_sentiment import LegalSentimentAnalyzer  # Your class in a separate file

# Reduce PyTorch memory usage
torch.set_num_threads(1)

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy load analyzer (model loads only when needed)
analyzer = None

def get_analyzer():
    global analyzer
    if analyzer is None:
        analyzer = LegalSentimentAnalyzer()  # uses smaller model internally
    return analyzer

# API for single text
class TextInput(BaseModel):
    text: str

@app.post("/analyze_text")
def analyze_text(input: TextInput):
    analyzer_instance = get_analyzer()
    cleaned_text = analyzer_instance.preprocess_text(input.text)
    sentences = cleaned_text.split('.')  # simple sentence split
    results = []
    for sentence in sentences:
        if len(sentence.strip()) > 10:
            sentiment = analyzer_instance.analyze_sentiment(sentence)
            results.append({"text": sentence, "sentiment": sentiment})
    summary = analyzer_instance.summarize_insights(
        [r['sentiment'] for r in results],
        [r['text'] for r in results]
    )
    return {"results": results, "summary": summary}

# API for file upload (CSV or TXT)
@app.post("/analyze_file")
async def analyze_file(file: UploadFile = File(...)):
    analyzer_instance = get_analyzer()

    if not file.filename.endswith(('.txt', '.csv')):
        return {"error": "Only TXT or CSV files allowed"}

    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    try:
        output_df, summary = analyzer_instance.process_file(temp_path)
    except Exception as e:
        os.remove(temp_path)
        return {"error": str(e)}

    os.remove(temp_path)
    return {
        "results": output_df.to_dict(orient="records"),
        "summary": summary
    }

# Root check
@app.get("/")
def read_root():
    return {"message": "Backend is running 🚀"}


@app.post("/ping")
def ping():
    return {"status": "ok"}


