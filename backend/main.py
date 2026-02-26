from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
import io
from groq import Groq
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Secure API key from environment
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


@app.get("/")
def home():
    return {"message": "AI Research Tool Backend Running"}


# Extract text from PDF
def extract_text_from_pdf(file_bytes):
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted

    return text


# Main research analysis
@app.post("/analyze")
async def analyze_pdf(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text = extract_text_from_pdf(content)

        prompt = f"""
You are a financial research analyst.

Analyze the earnings call transcript and return ONLY JSON in this format:

{{
"tone": "",
"confidence": "",
"positives": [],
"concerns": [],
"forward_guidance": "",
"capacity_trends": "",
"growth_initiatives": []
}}

Rules:
- If not mentioned, return "Not discussed".
- 3–5 bullet points.
- No extra text.

Transcript:
{text[:12000]}
"""

        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
        )

        result = chat.choices[0].message.content

        try:
            structured = json.loads(result)
        except:
            structured = {"raw_output": result}

        return structured

    except Exception as e:
        return {"error": str(e)}


# 🔥 Needed for Render deployment
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)