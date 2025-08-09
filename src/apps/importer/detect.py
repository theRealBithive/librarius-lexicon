# place in src/apps/importer/main.py or a new module like src/apps/importer/detect.py

import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

AUDIO_EXTS = {".m4b", ".mp3", ".m4a", ".flac", ".ogg", ".opus", ".aac", ".wav"}
COVER_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
TEMP_EXTS = {".part", ".tmp", ".crdownload", ".download"}

MIN_TRACKS = 2
SINGLE_MIN_BYTES = 10 * 1024 * 1024  # 10 MB
MIN_STABLE_AGE_SECONDS = 120

DISC_PATTERN = re.compile(r"(cd|disc|part|pt|vol|volume|book)\s*\d+", re.I)
SAMPLE_PATTERN = re.compile(r"(sample|preview|excerpt)", re.I)

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

def is_temp(p: Path) -> bool:
    return p.suffix.lower() in TEMP_EXTS

def is_audio(p: Path) -> bool:
    return p.suffix.lower() in AUDIO_EXTS

def is_cover(p: Path) -> bool:
    return p.suffix.lower() in COVER_EXTS and not SAMPLE_PATTERN.search(p.name)

def is_disc_like(name: str) -> bool:
    return bool(DISC_PATTERN.search(name))

def is_sample(name: str) -> bool:
    return bool(SAMPLE_PATTERN.search(name))

def newest_mtime_recursive(path: Path) -> float:
    newest = 0.0
    for root, dirs, files in os.walk(path):
        for f in files:
            fp = Path(root) / f
            try:
                mt = fp.stat().st_mtime
                if mt > newest:
                    newest = mt
            except FileNotFoundError:
                continue
    return newest

def collapse_single_child_chain(path: Path) -> Path:
    p = path
    while True:
        try:
            entries = [e for e in p.iterdir()]
        except FileNotFoundError:
            break
        subdirs = [e for e in entries if e.is_dir()]
        files = [e for e in entries if e.is_file()]
        if files:  # stop; we reached a directory with files
            break
        if len(subdirs) != 1:
            break
        p = subdirs[0]
    return p

def analyze_directory(dir_path: Path) -> Optional[AudiobookCandidate]:
    if not dir_path.exists() or not dir_path.is_dir():
        return None

    # stability check
    newest = newest_mtime_recursive(dir_path)
    if newest and (time.time() - newest) < MIN_STABLE_AGE_SECONDS:
        return None  # in-progress

    entries = [e for e in dir_path.iterdir()]
    files = [e for e in entries if e.is_file()]
    subdirs = [e for e in entries if e.is_dir()]

    # Direct audio in this directory
    audio_files = [f for f in files if is_audio(f) and not is_temp(f) and not is_sample(f.name)]
    covers = [f for f in files if is_cover(f)]

    # If direct audio, treat as directory_tracks (or single)
    if audio_files:
        track_count = len(audio_files)
        total_bytes = sum(f.stat().st_size for f in audio_files)
        unit_type = "single_file" if track_count == 1 else "directory_tracks"
        # Single-file still needs size sanity
        if unit_type == "single_file" and total_bytes < SINGLE_MIN_BYTES and audio_files[0].suffix.lower() != ".m4b":
            return None
        author_guess, title_guess = guess_author_title(dir_path)
        conf = 0.55 + (0.15 if unit_type == "single_file" else 0.2) + (0.1 if covers else 0) + min(0.2, track_count * 0.02)
        reason = f"{track_count} audio files found directly; cover={bool(covers)}"
        return AudiobookCandidate(dir_path, track_count, total_bytes, bool(covers), unit_type, author_guess, title_guess, min(conf, 0.95), reason)

    # Multidisc pattern: subdirs are disc-like; aggregate audio
    disc_like_subdirs = [d for d in subdirs if is_disc_like(d.name)]
    if disc_like_subdirs:
        all_audio = []
        for d in disc_like_subdirs:
            for root, _, fs in os.walk(d):
                for fn in fs:
                    fp = Path(root) / fn
                    if fp.is_file() and is_audio(fp) and not is_temp(fp) and not is_sample(fp.name):
                        all_audio.append(fp)
        if len(all_audio) >= MIN_TRACKS:
            total_bytes = sum(f.stat().st_size for f in all_audio)
            author_guess, title_guess = guess_author_title(dir_path)
            conf = 0.65 + 0.15 + min(0.15, len(all_audio) * 0.01)
            reason = f"Multidisc aggregate across {len(disc_like_subdirs)} subdirs with {len(all_audio)} tracks"
            return AudiobookCandidate(dir_path, len(all_audio), total_bytes, False, "multi_disc", author_guess, title_guess, min(conf, 0.95), reason)

    # No direct audio; maybe each child is a separate audiobook container (e.g., Author has many titles)
    # We don’t classify this dir; caller should descend and classify children.
    return None

def guess_author_title(path: Path) -> tuple[Optional[str], Optional[str]]:
    # Heuristic: root/.../Author/Title[/disc] or root/.../Title
    parts = [p.name for p in path.parts]
    # Use last two meaningful parts as author/title if parent has no audio and siblings look like other books
    if len(parts) >= 2:
        author = parts[-2]
        title = parts[-1]
        # If title looks disc-like, go up one
        if is_disc_like(title) and len(parts) >= 3:
            title = parts[-2]
            author = parts[-3] if len(parts) >= 3 else None
        return sanitize_meta(author), sanitize_meta(title)
    return (None, None)

def sanitize_meta(s: Optional[str]) -> Optional[str]:
    if not s:
        return s
    # remove disc markers and extra spaces
    s2 = DISC_PATTERN.sub("", s)
    s2 = re.sub(r"[_\-\.]+", " ", s2)
    s2 = re.sub(r"\s+", " ", s2).strip()
    return s2 or None

def find_audiobooks(root: str | Path) -> List[AudiobookCandidate]:
    root = Path(root)
    candidates: List[AudiobookCandidate] = []

    # First, handle single-file audiobooks at root
    for f in root.glob("*"):
        if f.is_file() and is_audio(f) and not is_temp(f) and not is_sample(f.name):
            if f.stat().st_size >= SINGLE_MIN_BYTES or f.suffix.lower() == ".m4b":
                # Single-file unit at root
                if (time.time() - f.stat().st_mtime) >= MIN_STABLE_AGE_SECONDS:
                    author, title = guess_author_title(f.parent)
                    candidates.append(
                        AudiobookCandidate(
                            path=f,
                            track_count=1,
                            total_audio_bytes=f.stat().st_size,
                            has_cover=False,
                            unit_type="single_file",
                            author_guess=author,
                            title_guess=sanitize_meta(f.stem),
                            confidence=0.75,
                            reason="Single large audio file at root",
                        )
                    )

    # Then, scan subdirectories (up to a reasonable breadth)
    queue = [d for d in root.iterdir() if d.is_dir()]
    visited = set()

    while queue:
        d = queue.pop(0)
        if d in visited:
            continue
        visited.add(d)

        collapsed = collapse_single_child_chain(d)
        cand = analyze_directory(collapsed)
        if cand:
            candidates.append(cand)
            continue

        # Not a unit yet; descend further unless depth is too large
        try:
            subdirs = [e for e in collapsed.iterdir() if e.is_dir()]
        except FileNotFoundError:
            subdirs = []
        queue.extend(subdirs)

    # De-duplicate by canonical path
    uniq = {}
    for c in candidates:
        key = str(c.path.resolve())
        if key not in uniq or uniq[key].confidence < c.confidence:
            uniq[key] = c
    return list(uniq.values())