WIDTH = 1440
HEIGHT = 720
PLAYER_X = 360
FONT_SIZE = 24
FIXED_STEP = 1 / 240
AUTOSAVE_INTERVAL = 120
BUCKET_WIDTH = 400
CAMERA_MARGIN = 100
MAX_EDIT_HISTORY = 100

gamemode_colors = {
    "wave": (0, 255, 255),
    "cube": (0, 255, 0),
    "ship": (255, 0, 255),
    "ball": (255, 0, 0),
    "ufo": (255, 128, 0),
    "robot": (128, 128, 128),
    "spider": (128, 0, 255)
}

speed_color = (128, 128, 128)

gravity_colors = {
    1: (0, 255, 0),
    2: (255, 0, 255),
    -1: (255, 255, 0),
    -2: (0, 0, 255)
}

size_colors = {
    1: (0, 255, 0),
    0.5: (255, 0, 255)
}

teleport_color = (255, 128, 0)

orb_pad_colors = {
    "small": (255, 0, 255),
    "normal": (255, 255, 0),
    "big": (255, 0, 0),
    "gravity": (0, 255, 255),
    "heavy": (0, 0, 0),
    "spider": (0, 0, 0),
    "dash": (0, 255, 0)
}

coin_color = (255, 255, 0)

controls_tutorial = [
    "HOW TO WIN",
    "Collecting coins and completing levels gives points",
    "Level points are displayed in the title",
    "",
    "NAVIGATION",
    "Go Up - Spacebar, W, Return/Enter, Left Mouse",
    "Restart Level - R",
    "Switch Level - Q, E",
    "Pan/Scroll/Zoom (Paused) - Scroll + Ctrl/Shift/None",
    "",
    "PRACTICE CHEATS",
    "Cheats disables points earning and switches end color",
    "Switch Checkpoint - A, D",
    "Toggle Speed Changer - Z",
    "Toggle Hitboxes - X",
    "Scroll Through Hitboxes - Scroll + Alt",
    "Toggle Collision (Only a cheat if you actually collide) - C",
    "Move One Frame Forward - V",
    "Toggle Player Visibility - N",
    "",
    "OTHER",
    "Dark Mode - M",
    "Debug Overlay - F3",
    "Show Spacial Buckets - F4",
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
    "Select Object - Right Mouse + Shift/Ctrl/None",
    "Switch Between Move and Scale - V",
    "Move/Scale Objects - W, A, S, D + Shift/Ctrl/Alt/None",
    "Rotate Objects - Q, E + Shift/Ctrl/Alt/None",
    "Flip Objects - I, O",
    "Deselect Objects - U",
    "Duplicate Objects - Y",
    "Delete Objects - Backspace",
    "Snap Objects To Grid - G",
    "Group Objects Together - J",
    "Ungroup Objects - K",
    "Layer Objects Last/Back/Forward/First - 1, 2, 3, 4",
    "Move Objects To Background/Objects/Decoration - 5, 6, 7",
    "Switch Building Layer - C + Shift/None",
    "Reset Camera Y/Full Camera Position Reset - R + Ctrl/None",
    "Undo/Redo Edit - Z + Ctrl/None",
    "Edit Level Settings - T",
    "",
    "LEVEL SETTINGS",
    "Length - What x value the level ends at for the percentage display",
    "Roof/Floor - What y value the levels roof/floor that stops the player is at",
    "Background- Sets the background color of the enire level",
    "Title - The title of the level",
    "Points - How many points you should get from completing the level",
    "Level Number - Which order in the levels this level is",
    "Song - Name of the song to use in the level, add as ogg filetype to songs folder",
    "Reset stats - Type reset to clear all attempts and completions",
    "Delete - Type delete to delete the entire level permanently",
    "",
    "SHAPES",
    "Building shapes - square, triangle, slope, circle",
    "Functional shapes - end, checkpoint, gamemode, speed, gravity, size, teleport, orb, pad, coin",
    "Set color or outline to 0 to make them transparent",
    "",
    "CHECKPOINTS",
    "Checkpoints are marked with a C, the first checkpoint is marked S and cannot be deleted",
    "Have only checkpoints selected to change their modifiers"
    "",
    "SHAPE MODIFIERS",
    "Gamemode - Cube, ship, ball, wave, ufo, robot, spider",
    "Speed - Default speed is 2",
    "Gravity - Default gravity is 1, can also be negative",
    "Size - Default size is 1 which is 40 pixels",
    "Teleport - Teleports the player to a specific height",
    "Orb - Small, normal, big, gravity, heavy or dash",
    "Pad - Small, normal, big, gravity or spider",
    "Coin - Set the number of points it should give",
    "",
    "AVAILABLE SONGS",
    "climax",
]