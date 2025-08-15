from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import torch
from TTS.api import TTS
import uuid
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تحميل النموذج عند الحاجة فقط لتحسين الأداء
tts = None
device = "cuda" if torch.cuda.is_available() else "cpu"

def load_tts():
    global tts
    if tts is None:
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    return tts

@app.get("/", response_class=HTMLResponse)
def main_page():
    return '''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>تحويل النص إلى صوت</title>
        <style>
            body {
                font-family: 'Cairo', Tahoma, Arial, sans-serif;
                background: linear-gradient(120deg, #e0eafc, #cfdef3);
                min-height: 100vh;
                margin: 0;
                padding: 0;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: #fff;
                border-radius: 16px;
                box-shadow: 0 4px 24px rgba(0,0,0,0.08);
                padding: 32px 24px;
                max-width: 420px;
                width: 100%;
            }
            h2 {
                color: #2b5876;
                margin-bottom: 24px;
                text-align: center;
            }
            label {
                font-weight: bold;
                color: #333;
                display: block;
                margin-bottom: 8px;
            }
            textarea, select {
                width: 100%;
                margin-bottom: 16px;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #b2bec3;
                font-size: 1em;
                box-sizing: border-box;
                resize: vertical;
            }
            input[type="submit"] {
                background: linear-gradient(90deg, #36d1c4, #5b86e5);
                color: #fff;
                border: none;
                border-radius: 8px;
                padding: 12px 0;
                width: 100%;
                font-size: 1.1em;
                font-weight: bold;
                cursor: pointer;
                transition: background 0.2s;
            }
            input[type="submit"]:hover {
                background: linear-gradient(90deg, #5b86e5, #36d1c4);
            }
            .footer {
                text-align: center;
                margin-top: 18px;
                color: #888;
                font-size: 0.95em;
            }
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap" rel="stylesheet">
    </head>
    <body>
        <div class="container">
            <h2>تحويل النص إلى صوت <span style="font-size:0.7em;color:#36d1c4;">(يدعم العربية)</span></h2>
            <form action="/synthesize" method="post">
                <label for="text">النص:</label>
                <textarea name="text" id="text" rows="4" placeholder="أدخل النص هنا...">مرحبا بك في تجربة تحويل النص إلى صوت باستخدام كوكوي.</textarea>
                
                <label for="speaker">المتحدث:</label>
                <select name="speaker" id="speaker">
                    <option value="Claribel Dervla">Claribel Dervla</option>
                    <option value="Daisy Studious">Daisy Studious</option>
                    <option value="Gracie Wise">Gracie Wise</option>
                    <option value="Ana Florence">Ana Florence</option>
                    <option value="Craig Gutsy">Craig Gutsy</option>
                </select>
                
                <label for="language">اللغة:</label>
                <select name="language" id="language">
                    <option value="ar">العربية</option>
                    <option value="en">English</option>
                    <option value="fr">Français</option>
                    <option value="es">Español</option>
                    <option value="de">Deutsch</option>
                    <option value="it">Italiano</option>
                    <option value="tr">Türkçe</option>
                    <option value="ru">Русский</option>
                    <option value="zh-cn">中文</option>
                    <option value="ja">日本語</option>
                </select>
                
                <input type="submit" value="حوّل إلى صوت">
            </form>
            <div class="footer">&copy; 2025 - مشروع تحويل النص إلى صوت باستخدام Coqui TTS</div>
        </div>
    </body>
    </html>
    '''

@app.post("/synthesize")
def synthesize(text: str = Form(...), speaker: str = Form(...), language: str = Form(...)):
    try:
        tts_model = load_tts()
        output_path = f"output_{uuid.uuid4().hex}.wav"
        tts_model.tts_to_file(text=text, speaker=speaker, language=language, file_path=output_path)
        return FileResponse(output_path, media_type="audio/wav", filename="tts_output.wav")
    except Exception as e:
        return HTMLResponse(f"<h3>خطأ: {str(e)}</h3><a href='/'>العودة</a>")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
