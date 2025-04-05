from typing import List, Tuple, Any
from pathlib import Path
from pydantic import BaseModel, field_validator, Field
import whisper
from pyannote.audio import Pipeline
from textblob import TextBlob
from pyannote_utils import diarize_text

class DiarizationSegment(BaseModel):
    start: float = Field(..., ge=0, description="Start time of the speech segment")
    end: float = Field(..., gt=0, description="End time of the speech segment")
    speaker: str = Field(..., min_length=1, description="Speaker label")
    text: str = Field(..., min_length=1, description="Transcribed text")

class AudioFile(BaseModel):
    path: str

    @field_validator("path")
    def check_file_exists(cls, value):
        if not Path(value).is_file():
            raise ValueError(f"File does not exist: {value}")
        return value

def speaker_diarize(file: str) -> Any:
    """
    Performs speaker diarization on the given audio file.

    Args:
        file (str): Path to the audio file.

    Returns:
        Any: The diarization result containing speaker segmentation.
    """
    validated_file = AudioFile(path=file)
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization",
        use_auth_token="Hugging Face token"
    )
    diarization_result = pipeline(validated_file.path)
    return diarization_result

def load_and_transcribe(file: str) -> List[Tuple[Any, str, str]]:
    """
    Transcribes the given audio file using Whisper ASR and performs speaker diarization.

    Args:
        file (str): Path to the audio file.

    Returns:
        List[Tuple[Any, str, str]]: A list of tuples containing segment details,
                                  speaker label, and transcribed text.
    """
    validated_file = AudioFile(path=file)
    model = whisper.load_model("turbo")
    asr_result = model.transcribe(validated_file.path)
    diarization_result = speaker_diarize(validated_file.path)
    final_result = diarize_text(asr_result, diarization_result)
    validated_segment = [
        DiarizationSegment(start=seg.start, end=seg.end, speaker=spk, text=text) for seg,spk,text in final_result
    ]

    return validated_segment

def get_sentiment(sent: str = Field(... ,min_length=1)) -> str:
    """
    Analyzes the sentiment of a given text.

    Args:
        sent (constr): The input text.

    Returns:
        str: The sentiment label ('positive', 'negative', or 'neutral').
    """
    blob = TextBlob(sent)
    polarity: float = blob.sentiment.polarity
    sentiment: str = (
        "positive" if polarity > 0 else
        "negative" if polarity < 0 else
        "neutral"
    )
    return sentiment

def save_in_txt(result: List[DiarizationSegment]) -> List[str]:
    """
    Formats the diarized and transcribed text with sentiment analysis.

    Args:
        result (List[DiarizationSegment]): A list of DiarizationSegment objects.

    Returns:
        List[str]: A list of formatted transcript lines with timestamps, speaker labels,
                   transcribed text, and sentiment analysis.
    """
    script_lines: List[str] = []
    for segment in result:
        line: str = f'{segment.start:.2f} {segment.end:.2f} {segment.speaker} {segment.text}'
        sentiment: str = get_sentiment(segment.text)
        line = line + f" SENTIMENT:{sentiment}"
        script_lines.append(line)
    return script_lines
