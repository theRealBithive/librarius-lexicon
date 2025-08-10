import os
from loguru import logger
from src.apps.importer.detect import find_audiobooks
from src.apps.importer.dataclasses import AudiobookCandidate
from src.apps.core.models import Audiobook

logger.add("importer.log", rotation="100 MB", retention="10 days", enqueue=True)

def import_audiobooks():
    """
    This function is called by the Django Q scheduler.
    It will import all audiobooks from the input path, which is always /app/input. To Change the path, change the docker mount point in docker-compose.yml.
    """
    logger.info("Importing audiobooks")
    importer = Importer()
    importer.run()

class Importer:
    def __init__(self):
        self.input_path = "/app/input"
        self.output_path = "/app/output"

    def process_candidate(self, candidate: AudiobookCandidate):
            logger.info(f"Processing {candidate.path}")
            logger.info(f"Author: {candidate.author_guess}")
            logger.info(f"Title: {candidate.title_guess}")
            logger.info(f"Confidence: {candidate.confidence}")
            logger.info(f"Reason: {candidate.reason}")
            logger.info(f"Unit Type: {candidate.unit_type}")
            logger.info(f"Has Cover: {candidate.has_cover}")
            logger.info(f"Track Count: {candidate.track_count}")
            logger.info(f"Total Audio Bytes: {candidate.total_audio_bytes}")
            # Check if the audiobook already exists
            if Audiobook.objects.filter(input_path=candidate.path).exists():
                logger.info(f"Audiobook already exists: {candidate.path}")
                return
            Audiobook.objects.create(
                title=candidate.title_guess,
                author=candidate.author_guess,
                input_path=candidate.path,
                output_path=self.output_path,
                status="pending",
            )

    def run(self):
        logger.info("Running Importer")
        logger.info("Checking for new audiobooks in /app/input")
        candidates = find_audiobooks(self.input_path)
        logger.info(f"Found {len(candidates)} candidates")
        for candidate in candidates:
            self.process_candidate(candidate)

        

