FROM python:3.11-slim

RUN apt-get update && apt-get install -y pandoc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY script.py .

RUN pip install requests

ENTRYPOINT ["python", "script.py"]

# docker build -t googledoc-to-book .
# docker run --rm -v $(pwd):/app googledoc-to-book "https://docs.google.com/document/d/1rsaK53T3Lg5KoGwvf8ukOUvbELRtH-V0LnOIFDxBryE/export?format=docx" combined.epub

