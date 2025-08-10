from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class AudiobookCandidate:
    path: Path
    track_count: int
    total_audio_bytes: int
    has_cover: bool
    unit_type: str  # "single_file" | "directory_tracks" | "multi_disc"
    author_guess: Optional[str]
    title_guess: Optional[str]
    confidence: float
    reason: str