import json

from entities.serialization import data_to_levels, levels_to_data

with open("entities/levels.json", "r") as f:
    levels = data_to_levels(json.load(f))

for level in levels:
    level["victors"].clear()

with open("entities/levels.json", "w") as f:
    json.dump(levels_to_data(levels), f, indent=2)