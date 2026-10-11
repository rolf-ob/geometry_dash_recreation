Bugs:
- Slope velocity gets heavier with higher value gravity, try to make slope_vel independent of gravity
- Wave trail breaks on slopes when in 0 gravity
- Rotation drifts for 0.1, 1 and 45 degrees (use rounding?)
- Object menu doesn't work correctly with multi select, check also when deleting objects while start pos is selected

Update v1.1.0
- Trigger transition speed
- Main levels
- Pyinstaller exe file

Optimization/structuring
- Clean up apply_edit()
- Rebuild buckets for individual objects while keeping z-order
- Too much dependency on Game class, experiment with multiple classes
- Add more tests

Features
- Default level sizes
- Multi-point shape
- Music affected by speedhack
- CBF

User
- Making private levels
- Public levels
- Public level stats like unique visitors, likes, dislikes, comments etc
- Changing controls and tutorial with it

UI
- Images/sprites
- Clickable UI menu and build mode