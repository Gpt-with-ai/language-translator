import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from groq import Groq

from flask import Flask
from flask_cors import CORS
 
app = Flask(__name__)
CORS(app, origins=["https://hub.decipherinc.com"], supports_credentials=True)

 

from langdetect import detect
# Load environment
load_dotenv()

# app = Flask(__name__)
app.secret_key = "supersecretkey"

# Groq client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is required")
groq_client = Groq(api_key=GROQ_API_KEY)

def detect_language_with_groq(text: str) -> str:
    """Detect language and return 2-letter ISO code."""
    try:
        sample_text = text[:300].strip()
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": """Respond with ONLY the 2-letter ISO 639-1 code of the text language."""
                },
                {"role": "user", "content": sample_text}
            ],
            temperature=0,
            max_tokens=10
        )
        detected = response.choices[0].message.content.strip().lower()
        lang_code = ''.join(c for c in detected if c.isalpha())
        if len(lang_code) == 2:
            return lang_code
        return "en"
    except:
        return "en"
    # try:
    #     return detect(text)
    # except:
    #     return "en"

def translate_with_groq(text: str, src_lang: str, tgt_lang: str = "en") -> str:
    """Translate text to English using Groq."""
    if not text.strip() or src_lang == tgt_lang:
        return text
    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system",
                 "content": f"Translate from {src_lang} to {tgt_lang}. Output ONLY the translated text."},
                {"role": "user", "content": text}
            ],
            temperature=0,
            max_tokens=4096
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[Translation failed: {e}]"

@app.route("/")
def home():
    return render_template("indexh.html")
@app.route("/detect-language", methods=["POST", "OPTIONS"])
def detect():
    return {"message": "CORS working!"}


@app.route("/ajax_translate", methods=["POST"])
def ajax_translate():
    try:
        data = request.get_json()
        text = data.get("text", "").strip()
        if not text:
            return jsonify({"translation": "", "detected_lang": ""})
        src_lang = detect_language_with_groq(text)
        if src_lang == "en":
            return jsonify({
                "translation": text,
                "detected_lang": src_lang,
                "message": "Text is already in English"
            })
        translated = translate_with_groq(text, src_lang, "en")
        return jsonify({"translation": translated, "detected_lang": src_lang})
    except Exception as e:
        return jsonify({"translation": "[Translation service unavailable]", "error": str(e)})

if __name__ == "__main__":
    print("🚀 Starting Live Translator...")
    app.run(port=5080, debug=True)




