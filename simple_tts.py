from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, HTMLResponse
import uvicorn
import uuid

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def main_page():
    return '''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>تحويل النص إلى صوت - نسخة مبسطة</title>
        <style>
            body {
                font-family: 'Cairo', Tahoma, Arial, sans-serif;
                background: linear-gradient(120deg, #e0eafc, #cfdef3);
                min-height: 100vh;
                margin: 0;
                padding: 20px;
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
            .status {
                text-align: center;
                margin-top: 16px;
                color: #666;
                font-size: 0.9em;
            }
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap" rel="stylesheet">
    </head>
    <body>
        <div class="container">
            <h2>تحويل النص إلى صوت</h2>
            <div class="status">جاري تحميل النموذج...</div>
            <form action="/synthesize" method="post">
                <label for="text">النص:</label>
                <textarea name="text" id="text" rows="4" placeholder="أدخل النص هنا...">مرحبا بك في تجربة تحويل النص إلى صوت.</textarea>
                
                <label for="language">اللغة:</label>
                <select name="language" id="language">
                    <option value="ar">العربية</option>
                    <option value="en">English</option>
                </select>
                
                <input type="submit" value="حوّل إلى صوت">
            </form>
        </div>
        <script>
            document.querySelector('.status').textContent = 'جاهز للاستخدام!';
        </script>
    </body>
    </html>
    '''

@app.post("/synthesize")
def synthesize(text: str = Form(...), language: str = Form(...)):
    # تحميل النموذج فقط عند الحاجة
    try:
        import torch
        from TTS.api import TTS
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        
        output_path = f"output_{uuid.uuid4().hex}.wav"
        
        # استخدام متحدث افتراضي
        default_speaker = tts.speakers[0] if tts.speakers else "Claribel Dervla"
        
        tts.tts_to_file(
            text=text, 
            speaker=default_speaker, 
            language=language, 
            file_path=output_path
        )
        
        return FileResponse(output_path, media_type="audio/wav", filename="tts_output.wav")
    
    except Exception as e:
        return HTMLResponse(f"<h3>خطأ: {str(e)}</h3><a href='/'>العودة</a>")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
