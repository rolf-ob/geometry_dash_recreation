WIDTH = 1440
HEIGHT = 720
PLAYER_X = 360
FONT_SIZE = 24
FIXED_STEP = 1 / 240

gamemode_colors = {
    "wave": (0, 255, 255),
    "cube": (0, 255, 0),
    "ship": (255, 0, 255),
    "ball": (255, 0, 0),
    "ufo": (255, 128, 0),
    "robot": (255, 255, 255),
    "spider": (128, 0, 255)
}

gravity_colors = {
    1: (0, 255, 0),
    2: (255, 0, 255),
    -1: (255, 255, 0),
    -2: (0, 0, 255)
}

orb_pad_colors = {
    "small": (255, 0, 255),
    "normal": (255, 255, 0),
    "big": (255, 0, 0),
    "gravity": (0, 255, 255),
    "heavy/spider": (0, 0, 0),
    "dash": (0, 255, 0)
}

controls_tutorial = [
    "HOW TO WIN",
    "Collecting coins and completing levels gives points",
    "Level points are displayed in the title",
    "",
    "NAVIGATION",
    "Go Up - Spacebar, W, Return/Enter, Left Mouse",
    "Restart Level - R",
    "Switch Level - Q, E",
    "Pan/Scroll/Zoom - Scroll + Ctrl/Shift/None",
    "",
    "PRACTICE CHEATS",
    "Cheats disables points earning and the end switches color",
    "Switch Checkpoint - 1, 3",
    "Toggle Speed Changer - Z",
    "Toggle Hitboxes - X",
    "Toggle Collision - C",
    "Move One Frame Forward - V",
    "Toggle Player Visibility - N",
    "",
    "OTHER",
    "Debug Menu - F3",
    "Save To File - F"
]
operator_tutorial = [
    "OPERATOR CONTROLS",
    "Create Level - H",
    "Build Mode - B"
]
settings_tutorial = [
    "CHANGE SETTINGS",
    "Pause Level/Open Settings - Escape, S",
    "Select Setting - Up/Down Arrow",
    "Apply Setting - Return/Enter",
    "Deselect Setting - Tab",
    "",
    "SETTING DESCRIPTION",
    "Name - Your leaderboard name",
    "Speedhack - Speed multiplier for the speed changer",
    "FPS - Frames per second",
    "Respawn Time - How quickly you respawn"
]
building_tutorial = [
    "BUILDING CONTROLS",
    "Place Object - Left Mouse + Shift/None",
    "Select Object - Right Mouse + Shift/None",
    "Move Objects - W, A, S, D + Shift/Ctrl/None",
    "Rotate Objects - Z, C",
    "Flip Objects - I, O",
    "Deselect Objects - U",
    "Duplicate Objects - Y",
    "Delete Objects - Backspace",
    "Snap Objects To Grid - G",
    "Switch Building Layer - Q, E",
    "Reset Camera Position - R",
    "Edit Level Settings - T",
    "",
    "LEVEL SETTINGS",
    "Background- Sets the background color of the enire level",
    "Title - The title of the level",
    "Points - How many points you should get from completing the level",
    "Level Number - Which order in the levels this level is",
    "Reset stats - Type reset to clear all attempts and completions",
    "Delete - Type delete to delete the entire level permanently",
    "",
    "SHAPES",
    "Building shapes - square, end, triangle, slope, circle",
    "Functional shapes - coin, orb, pad, gamemode, speed, gravity",
    "",
    "SHAPE MODIFIERS",
    "Coin - Set the number of points it should give",
    "Orb - Small, normal, big, gravity, heavy or dash",
    "Pad - Small, normal, big, gravity or spider",
    "Speed - Default speed is 2",
    "Gravity - Default gravity is 1, can also be negative",
    "",
    "GAMEMODES",
    "Wave - Hold to instantly move up, release to move down",
    "Cube - Click to do a jump when on the ground",
    "Ship - Hold to accelerate upwards, release to accelerate downwards", #!
    "",
    "CHECKPOINTS",
    "Checkpoints have to be duplicated from the start position marked with an S",
    "Have only checkpoints selected to change their modifiers"
    "",
    "CHECKPOINT MODIFIERS",
    "Gamemode - Changes what action clicking performs",
    "Speed - Changes how fast the player moves in both directions",
    "Gravity - Changes how fast the player moves up and down",
]