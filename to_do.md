- Checkpoints as shapes
- Rotate objects around x+20 y+20, obj center if holding alt
- Hide mouse
- Obj scale mode for WASD

- sorted() function for leaderboard/checkpoint sorting

- Only select top object if multiple are overlapping
- Keybind to change the Z-axis of an object

- Precompute and store obj.axes, obj.points and obj.AABB using obj.recompute rather than points arrays
- Square hitboxes that get checked before SAT runs for optimization stored as obj.AABB
- Render and check for things in cells that are for example 400 wide

- Display from which percentage you started a run
- Dark mode
- Better x, y alignment compared to width and height
- Camera going up and down with player
- Changing controls in menu and changing tutorial with it
- Sliding on slopes or rotated squares
- CBF
- Images/sprites
- Each level as its own json file
- UI menu and build mode

positions never float, rotations max 1 decimal, clamped speed, clamped level number, visually collect coins