import json
from pathlib import Path

path = Path("questions_labeled.json")
data = json.loads(path.read_text(encoding="utf-8"))

ids = sorted(q["id"] for q in data)
expected = list(range(ids[0], ids[-1] + 1))
missing = sorted(set(expected) - set(ids))
dupes   = sorted(i for i in ids if ids.count(i) > 1)

seen_text = {}
dupe_text = []
for q in data:
    text = q["question"].strip().lower()
    if text in seen_text:
        dupe_text.append((seen_text[text], q["id"]))
    else:
        seen_text[text] = q["id"]

print(f"Total questions : {len(data)}")
print(f"ID range        : {ids[0]} → {ids[-1]}")
print(f"Missing IDs     : {missing if missing else 'None'}")
print(f"Duplicate IDs   : {sorted(set(dupes)) if dupes else 'None'}")
print(f"Duplicate text  : {dupe_text if dupe_text else 'None'}")
