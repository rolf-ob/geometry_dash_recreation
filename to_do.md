- Checkpoints as shapes

- Enforce x, y, width and height to be integers and rotation to be floats at max 1 decimal
- Set maximum speed value so player cant move through thin objects
- When changing level number have minimum 1 so main menu is always 0 and maximum the length of however many levels there are

- sorted() function for leaderboard/checkpoint sorting

- Only select top object if multiple are overlapping
- Keybind to change the Z-axis of an object

- Precompute and store obj.axes, obj.points and obj.AABB using obj.recompute rather than _points arrays
- Square hitboxes that get checked before SAT runs for optimization stored as obj.AABB
- Render and check for things in cells that are for example 400 wide

- Display from which percentage you started a run
- Dark mode
- Better x, y alignment for width and height
- Scale mode for WASD
- Camera going up and down with player
- Changing controls in menu and changing tutorial with it
- Sliding on slopes or rotated squares
- CBF
- Images/sprites
- Each level as its own json file
- UI menu and build mode