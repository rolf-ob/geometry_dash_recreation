from pathlib import Path
import json, os

from entities.object import Object

def level_to_dict(level):
    return {
        "meta": level["meta"],
        "background": [obj.to_dict() for obj in level["background"]],
        "objects": [obj.to_dict() for obj in level["objects"]],
        "decoration": [obj.to_dict() for obj in level["decoration"]],
        "checkpoints": [obj.to_dict() for obj in level["checkpoints"]],
        "victors": level["victors"]
    }

def dict_to_level(level):
    return {
        "meta": level["meta"],
        "background": [Object.from_dict(obj) for obj in level["background"]],
        "objects": [Object.from_dict(obj) for obj in level["objects"]],
        "decoration": [Object.from_dict(obj) for obj in level["decoration"]],
        "checkpoints": [Object.from_dict(obj) for obj in level["checkpoints"]],
        "victors": level["victors"]
    }

def save_json(path, data):
    path = Path(path)
    temp_path = path.with_suffix(path.suffix + ".tmp")

    with open(temp_path, "w") as f:
        json.dump(data, f, indent=2)
        f.flush()
        os.fsync(f.fileno())

    os.replace(temp_path, path)