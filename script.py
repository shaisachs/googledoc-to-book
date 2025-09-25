import os
import re
import sys
import subprocess
import requests

TEMP_DIR = "docs_tmp"

def extract_doc_id(url: str) -> str | None:
    """Extract Google Doc ID from URL."""
    match = re.search(r"/document/d/([a-zA-Z0-9-_]+)", url)
    return match.group(1) if match else None

def download_hub_doc(hub_doc_id: str) -> str:
    """Download hub doc as plain text."""
    url = f"https://docs.google.com/document/d/{hub_doc_id}/export?format=html"
    print(f"Fetching hub doc text from {url}")
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text

def extract_links(text: str) -> list[str]:
    """Extract Google Docs links from hub text."""
    return re.findall(r"https://docs.google.com/document/d/[a-zA-Z0-9-_]+", text)

def download_docx(doc_id: str, dest_path: str):
    """Download a Google Doc as .docx via export URL."""
    url = f"https://docs.google.com/document/d/{doc_id}/export?format=docx"
    print(f"Downloading {doc_id} → {dest_path}")
    resp = requests.get(url)
    resp.raise_for_status()
    with open(dest_path, "wb") as f:
        f.write(resp.content)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <HUB_DOC_URL> [OUTPUT_NAME]")
        sys.exit(1)

    HUB_DOC_URL = sys.argv[1]
    OUTPUT_NAME = sys.argv[2] if len(sys.argv) > 2 else "combined.epub"

    hub_doc_id = extract_doc_id(HUB_DOC_URL)
    if not hub_doc_id:
        raise ValueError("Could not extract hub doc ID")

    os.makedirs(TEMP_DIR, exist_ok=True)

    # 1. Download hub text
    hub_text = download_hub_doc(hub_doc_id)

    # 2. Extract linked doc URLs
    links = extract_links(hub_text)
    links.insert(0, HUB_DOC_URL)
    print(f"Found {len(links)} linked docs")

    # 3. Download each docx
    docx_files = []
    for i, link in enumerate(links, start=1):
        doc_id = extract_doc_id(link)
        if not doc_id:
            continue
        out_file = os.path.join(TEMP_DIR, f"doc_{i}.docx")
        download_docx(doc_id, out_file)
        docx_files.append(out_file)

    # 4. Run pandoc to merge into EPUB
    pandoc_cmd = ["pandoc", "-o", OUTPUT_NAME] + docx_files
    print("Running:", " ".join(pandoc_cmd))
    subprocess.run(pandoc_cmd, check=True)

    print(f"\n✅ All done! EPUB saved as {OUTPUT_NAME}")

