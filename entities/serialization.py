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

def levels_to_data(levels):
    return [level_to_dict(level) for level in levels]

def data_to_levels(data):
    return [dict_to_level(level) for level in data]