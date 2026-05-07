"""Fix notebook widget metadata so nbconvert can export to HTML (KeyError: 'state')."""
import json
import sys

path = "IS467_Embeddings_and_Chunking_with_LlamaIndex_and_Gemini__HT.ipynb"
if len(sys.argv) > 1:
    path = sys.argv[1]

with open(path, encoding="utf-8") as f:
    nb = json.load(f)

widgets = nb.get("metadata", {}).get("widgets", {})
mime = "application/vnd.jupyter.widget-state+json"
ws = widgets.get(mime, {})

if ws and "state" not in ws:
    # nbconvert expects metadata.widgets[mime]["state"] = { id: ... }
    widgets[mime] = {"state": ws}
    nb["metadata"]["widgets"] = widgets
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print("Fixed widget metadata. Run nbconvert again.")
else:
    print("No change needed (already has 'state' or no widget data).")
