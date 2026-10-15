import json
from pathlib import Path

from entities.serialization import dict_to_level, level_to_dict, save_json

levels = []
for file in Path("levels").glob("*.json"):
    with open(file, "r", encoding="utf-8") as f:
        level = dict_to_level(json.load(f))
        level["victors"].clear()
        level["meta"]["title"] = file.stem
        levels.append(level)

for level in levels:
    save_json(f"levels/{level["meta"]["title"]}.json", level_to_dict(level))