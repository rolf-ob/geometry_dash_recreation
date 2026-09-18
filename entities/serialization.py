#! Understand
from entities.object import Object

def level_to_dict(level):
    meta, background, objects, decoration, checkpoints, end, victors = level.values()
    return {
        "meta": {
            "gamemode": meta["gamemode"], "speed": meta["speed"], "gravity": meta["gravity"], "background color": list(meta["background color"]), "title": meta["title"], "points": meta["points"]
        },
        "background": [obj.to_dict() for obj in background],
        "objects": [obj.to_dict() for obj in objects],
        "decoration": [obj.to_dict() for obj in decoration],
        "checkpoints": [obj.to_dict() for obj in checkpoints],
        "end": end.to_dict(),
        "victors": victors
    }

def dict_to_level(d):
    m = d["meta"]
    meta = {"gamemode": m["gamemode"], "speed": m["speed"], "gravity": m["gravity"], "background color": tuple(m["background color"]), "title": m["title"], "points": m["points"]}
    return {
        "meta": meta,
        "background": [Object.from_dict(o) for o in d["background"]],
        "objects": [Object.from_dict(o) for o in d["objects"]],
        "decoration": [Object.from_dict(o) for o in d["decoration"]],
        "checkpoints": [Object.from_dict(o) for o in d["checkpoints"]],
        "end": Object.from_dict(d["end"]),
        "victors": d["victors"]
    }

def levels_to_data(levels):
    return [level_to_dict(level) for level in levels]

def data_to_levels(data):
    return [dict_to_level(d) for d in data]