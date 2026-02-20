import os

from config import load_env

load_env()

PDF_PATH = os.getenv("PDF_PATH")

def ingest_pdf():
    pass


if __name__ == "__main__":
    ingest_pdf()
