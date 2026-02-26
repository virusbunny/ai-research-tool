from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
import io
from groq import Groq
import json
import os
from dotenv import load_dotenv

# ✅ Load environment variables from .env
load_dotenv()

app = FastAPI()

# ✅ Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Secure Groq API key (NO key in code)
# client = Groq(api_key=os.getenv("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"))


# Home route
@app.get("/")
def home():
    return {"message": "AI Research Tool Backend Running"}


# ✅ Extract text from PDF
def extract_text_from_pdf(file_bytes):
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted

    return text


# 🔥 Main AI Research Tool
@app.post("/analyze")
async def analyze_pdf(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text = extract_text_from_pdf(content)

        # Structured AI prompt
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
- Do not add extra text.
- If something is missing, write "Not discussed".
- Keep positives and concerns 3-5 points.
- Be concise and professional.

Transcript:
{text[:12000]}
"""

        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
        )

        result = chat.choices[0].message.content

        # Convert AI output to JSON
        try:
            structured = json.loads(result)
        except:
            structured = {"raw_output": result}

        return structured

    except Exception as e:
        return {"error": str(e)}