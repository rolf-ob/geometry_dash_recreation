import json
from pathlib import Path

from entities.serialization import dict_to_level, level_to_dict, save_json

levels = []
for file in Path("levels").glob("*.json"):
    with open(file, "r") as f:
        level = dict_to_level(json.load(f))
        level["victors"].clear()
        save_json(Path("levels") / f"{level["meta"]["title"]}.json", level_to_dict(level))