from typing import List, Tuple, Dict, Any
from pyannote.core import Segment, Annotation
from pydantic import BaseModel, field_validator, ValidationInfo, Field

class TranscriptionSegment(BaseModel):
    """
    Represents a segment of transcribed text with timestamps.
    
    Attributes:
        start (float): Start time of the segment in seconds.
        end (float): End time of the segment in seconds.
        text (str): Transcribed text of the segment.
    """
    start: float = Field(..., ge=0, description="Start time of the speech segment")
    end: float = Field(..., gt=0, description="End time of the speech segment")
    text: str = Field(..., min_length=1, description="Transcribed text")

    @field_validator("start", "end")
    @classmethod
    def validate_timestamps(cls, value: float, values: ValidationInfo) -> float:
        """
        Ensures that timestamps are non-negative and end is greater than start.
        
        Args:
            value (float): The timestamp value to validate.
            values (ValidationInfo): Contains validated fields.
        
        Returns:
            float: The validated timestamp.
        
        Raises:
            ValueError: If the timestamp is negative or end <= start.
        """
        if value < 0:
            raise ValueError("Timestamps must be non-negative.")
        start = values.data.get("start")
        end = values.data.get("end")
        if start is not None and end is not None and end <= start:
            raise ValueError("End time must be greater than start time.")
        return value

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        """
        Ensures that text is non-empty or whitespace-only.
        
        Args:
            value (str): The text value to validate.
        
        Returns:
            str: The validated text.
        
        Raises:
            ValueError: If the text is empty or contains only whitespace.
        """
        if not value.strip():
            raise ValueError("Text cannot be empty or whitespace.")
        return value

class TranscriptionResult(BaseModel):
    """
    Represents the complete transcription result containing multiple segments.
    
    Attributes:
        segments (List[TranscriptionSegment]): List of transcription segments.
    """
    segments: List[TranscriptionSegment]

def get_text_with_timestamp(transcribe_res: Dict[str, Any]) -> List[Tuple[Segment, str]]:
    """
    Extracts text segments with their corresponding timestamps from transcription results.
    
    Args:
        transcribe_res (Dict[str, Any]): Dictionary containing transcription results.
    
    Returns:
        List[Tuple[Segment, str]]: A list of tuples containing Segment objects and their respective transcribed texts.
    """
    validated_transcribe_res = TranscriptionResult(**transcribe_res)
    timestamp_texts: List[Tuple[Segment, str]] = []
    for item in validated_transcribe_res.segments:
        timestamp_texts.append((Segment(item.start, item.end), item.text))
    return timestamp_texts

def add_speaker_info_to_text(timestamp_texts: List[Tuple[Segment, str]], ann: Annotation) -> List[Tuple[Segment, str, str]]:
    """
    Adds speaker information to each text segment based on diarization results.
    
    Args:
        timestamp_texts (List[Tuple[Segment, str]]): List of segments with their respective texts.
        ann (Annotation): Speaker diarization annotation.
    
    Returns:
        List[Tuple[Segment, str, str]]: A list of tuples containing Segment objects, speaker labels, and transcribed texts.
    """
    spk_text: List[Tuple[Segment, str, str]] = []
    for seg, text in timestamp_texts:
        spk: str = ann.crop(seg).argmax()
        spk_text.append((seg, spk, text))
    return spk_text

def merge_data(text_data: List[Tuple[Segment, str, str]]) -> Tuple[Segment, str, str]:
    """
    Merges multiple text segments from the same speaker into a single consolidated segment.
    
    Args:
        text_data (List[Tuple[Segment, str, str]]): List of tuples containing segments, speaker labels, and texts.
    
    Returns:
        Tuple[Segment, str, str]: A tuple containing the merged segment, speaker label, and concatenated text.
    """
    sentence: str = ''.join([item[-1] for item in text_data])
    spk: str = text_data[0][1]
    start: float = text_data[0][0].start
    end: float = text_data[-1][0].end
    return Segment(start, end), spk, sentence

# Punctuation marks that typically indicate the end of a sentence
PUNC_SENT_END: List[str] = ['.', '?', '!']

def merge_sentence(spk_text: List[Tuple[Segment, str, str]]) -> List[Tuple[Segment, str, str]]:
    """
    Merges text segments into coherent sentences based on speaker changes and 
    sentence-ending punctuation.
    
    This function consolidates text segments by:
    1. Merging segments from the same speaker.
    2. Breaking segments when a sentence-ending punctuation is encountered.
    3. Handling speaker transitions.
    
    Args:
        spk_text (List[Tuple[Segment, str, str]]): List of tuples containing segments, speaker labels, and texts.
    
    Returns:
        List[Tuple[Segment, str, str]]: A list of merged tuples containing segments, speaker labels, and texts.
    """
    merged_spk_text: List[Tuple[Segment, str, str]] = []
    pre_spk: str = None
    text_data: List[Tuple[Segment, str, str]] = []
    
    for seg, spk, text in spk_text:
        if spk != pre_spk and pre_spk is not None and len(text_data) > 0:
            merged_spk_text.append(merge_data(text_data))
            text_data = [(seg, spk, text)]
            pre_spk = spk

        elif text and len(text) > 0 and text[-1] in PUNC_SENT_END:
            text_data.append((seg, spk, text))
            merged_spk_text.append(merge_data(text_data))
            text_data = []
            pre_spk = spk
        else:
            text_data.append((seg, spk, text))
            pre_spk = spk
    
    if len(text_data) > 0:
        merged_spk_text.append(merge_data(text_data))
    
    return merged_spk_text

def diarize_text(transcribe_res: Dict[str, Any], diarization_result: Annotation) -> List[Tuple[Segment, str, str]]:
    """
    Performs full text diarization by combining transcription and speaker 
    diarization results.
    
    This function orchestrates the entire diarization process by:
    1. Extracting text with timestamps.
    2. Adding speaker information.
    3. Merging segments into coherent sentences.
    
    Args:
        transcribe_res (Dict[str, Any]): Dictionary containing transcription results.
        diarization_result (Annotation): Speaker diarization annotation.
    
    Returns:
        List[Tuple[Segment, str, str]]: A list of tuples containing segments, speaker labels, and texts.
    """
    timestamp_texts = get_text_with_timestamp(transcribe_res)
    spk_text = add_speaker_info_to_text(timestamp_texts, diarization_result)
    res_processed = merge_sentence(spk_text)
    return res_processed