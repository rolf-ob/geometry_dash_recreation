- remaining = frame_duration - (time.perf_counter() - self.last_frame_time)
if remaining > 0.001:
    time.sleep(remaining - 0.0005)

- Enforce x, y, width and height to be integers and rotation to be floats at max 1 decimal
- Keep rotations between 0 and 359
- Set maximum speed value so player cant move through thin objects
- When changing level number have minimum 1 so main menu is always 0 and maximum the length of however many levels there are

- sorted() function for leaderboard/checkpoint sorting

- Only select top object if multiple are overlapping
- Keybind to change the Z-axis of an object

- Precompute and store obj.axes, obj.points and obj.AABB using obj.recompute rather than _points arrays
- Square hitboxes that get checked before SAT runs for optimization stored as obj.AABB
- Render and check for things in cells that are for example 400 wide

- Display from which percentage you started a run
- Camera going up and down with player
- Changing controls in menu and changing tutorial with it
- Sliding on slopes or rotated squares
- CBF