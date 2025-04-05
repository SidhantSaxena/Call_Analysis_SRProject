from fastapi import FastAPI, File, UploadFile
import shutil
import os
import asyncio
import aiofiles
from fastapi.responses import FileResponse, JSONResponse
from speech_to_text import load_and_transcribe, save_in_txt
from logger_setup import logger  # Import the logger

# Initialize FastAPI application
app = FastAPI()

# Log FastAPI initialization
logger.info("FastAPI application initialized.")

# Directories for uploads and transcripts
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
TRANSCRIPT_DIR = "transcripts"
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    """Endpoint to upload an audio file."""
    file_location = os.path.join(UPLOAD_DIR, file.filename)

    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"File '{file.filename}' uploaded successfully.")
        return {"filename": file.filename, "message": "File saved successfully", "path": file_location}

    except Exception as e:
        logger.exception(f"Error while uploading file '{file.filename}': {e}")
        return JSONResponse(status_code=500, content={"error": "File upload failed"})

@app.get("/process-audio/")
async def process_audio(file_path: str):
    """Endpoint to process an audio file."""
    if not os.path.exists(file_path):
        logger.warning(f"File not found: {file_path}")
        return JSONResponse(status_code=404, content={"error": "File not found"})

    try:
        filename = os.path.basename(file_path)
        transcript_filename = f"{filename}.txt"
        transcript_path = os.path.join(TRANSCRIPT_DIR, transcript_filename)

        if os.path.exists(transcript_path):
            logger.info(f"Returning existing transcript: {transcript_path}")
            return FileResponse(transcript_path, media_type="text/plain", filename=transcript_filename)

        # Perform transcription and diarization asynchronously
        result = await asyncio.to_thread(load_and_transcribe, file_path)
        result_txt = await asyncio.to_thread(save_in_txt, result)

        async with aiofiles.open(transcript_path, "w") as f:
            for line in result_txt:
                await f.write(line + "\n")

        logger.info(f"Transcript generated: {transcript_path}")
        return FileResponse(transcript_path, media_type="text/plain", filename=transcript_filename)

    except Exception as e:
        logger.exception(f"Error processing file '{file_path}': {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing audio file"})

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
