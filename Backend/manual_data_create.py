import json
import uuid
import os

DATA_FILE = "manual_data.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = []

print("Type paras,enter q to exit\n")

while True:
    para = input("Enter paragraph:\n").strip()

    if para.lower()=='q':
        break

    if len(para.split()) < 10:
        continue

    item = {
        "id": str(uuid.uuid4()),
        "text": para
    }
    data.append(item)
    print("Added.\n")

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f,indent = 2, ensure_ascii=False)

