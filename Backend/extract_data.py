import requests
from bs4 import BeautifulSoup
import json
import os

def extract_paragraphs(url, min_words=30):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    raw_text = soup.get_text(separator='\n')

    paragraphs = []
    for para in raw_text.split('\n'):
        clean = para.strip()
        if len(clean.split()) >= min_words:
            paragraphs.append(clean)
    return paragraphs

sebi_urls = []

all_chunks = []

for topic, url in sebi_urls.items():
    print(f"Fetching from: {url}")
    paragraphs = extract_paragraphs(url)
    for i, text in enumerate(paragraphs):
        all_chunks.append({
            "id": f"{topic}-{i}",
            "topic": topic,
            "text": text
        })

os.makedirs("data", exist_ok=True)
with open("data/sebi_chunks.json", "w", encoding="utf-8") as f:
    json.dump(all_chunks, f, ensure_ascii=False, indent=2)

print(f"Saved {len(all_chunks)} cleaned paragraphs to data/sebi_chunks.json")
