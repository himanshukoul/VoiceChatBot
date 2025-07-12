import json
from pinecone_client import upsert_chunk  

DATA_FILE = "manual_data.json"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Loaded {len(data)} items")

for item in data:
    doc_id = item["id"]
    text = item["text"]
    upsert_chunk(doc_id, text)
    print(f"Upserted: {doc_id}")
