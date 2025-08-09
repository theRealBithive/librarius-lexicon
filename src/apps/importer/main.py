import os
from loguru import logger
from src.apps.importer.detect import find_audiobooks

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

    def run(self):
        logger.info("Running Importer")
        logger.info("Checking for new audiobooks in /app/input")
        candidates = find_audiobooks(self.input_path)
        logger.info(f"Found {len(candidates)} candidates")
        for candidate in candidates:
            logger.info(f"Processing {candidate.path}")


