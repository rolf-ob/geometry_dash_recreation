Bugs:
- Missing wave trail on teleport
- Slope velocity gets heavier with higher value gravity
- Wave trail bug upside down slope 0 gravity
- Undo redo doesn't update objects until new object placed? (Restore state doesnt call rebuild_buckets?)
- When changing object color it renders the old one until obj.recompute gets called due to real_color (same issue as undo redo?)
- Rotation drifts (use rounding?)
- Object menu doesn't work correctly with multi select, check also when deleting objects while start pos is selected

Update v1.1.0
- Trigger transition speed
- Main levels
- Pyinstaller exe file

Optimization
- Rebuild buckets for individual objects while keeping z-order
- Too much dependency on Game class, experiment with multiple classes

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