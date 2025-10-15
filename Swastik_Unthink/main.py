import os
import shutil
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from dotenv import load_dotenv
import speech_recognition as sr
from pydub import AudioSegment

# Load environment variables (for GEMINI_API_KEY)
load_dotenv()

app = FastAPI()

# Enable CORS so frontend or API tools can call it easily
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


@app.get("/")
def read_root():
    return {"message": "Welcome to the Meeting Summarizer API"}


@app.post("/summarize")
async def summarize_meeting(audio_file: UploadFile = File(...)):
    import tempfile

    try:
        # Step 1: Save uploaded file safely
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp:
            shutil.copyfileobj(audio_file.file, tmp)
            input_path = tmp.name

        output_path = input_path + "_converted.wav"

        # Step 2: Convert to WAV
        try:
            audio = AudioSegment.from_file(input_path)
            audio.export(output_path, format="wav")
        except Exception as e:
            raise ValueError(f"Audio conversion failed. Details: {e}")

        # Step 3: Transcribe
        recognizer = sr.Recognizer()
        with sr.AudioFile(output_path) as source:
            audio_data = recognizer.record(source)
            transcript = recognizer.recognize_google(audio_data)

        # Step 4: Summarize with Gemini
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = (
            f"Summarize this meeting transcript into concise key points, "
            f"decisions, and action items:\n\n{transcript}"
        )
        response = model.generate_content(prompt)
        print(transcript)
        print("summary:", getattr(response, "text", "No summary generated"))
        return {
            "transcript": transcript,
            "summary": getattr(response, "text", "No summary generated"),
        }

    except sr.UnknownValueError:
        return {"error": "Speech recognition could not understand the audio."}
    except sr.RequestError as e:
        return {"error": f"Speech recognition API error: {e}"}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Internal server error: {e}"}
    finally:
        for path in [locals().get("input_path"), locals().get("output_path")]:
            if path and os.path.exists(path):
                os.remove(path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)