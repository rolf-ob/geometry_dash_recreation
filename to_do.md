Update v1.1.0
- Trigger transition speed
- Main levels
- Pyinstaller exe file

Bugs:
- When rotating 0.1 or 1 degrees, rouding makes position slighly inaccurate, fix by implementing true_x and true_y
- Shift to multiselect objects, release mouse while hovering over selected object, object gets deselected
- Object menu doesn't work correctly with multi select, check also when deleting objects while start pos is selected

Optimization/structuring
- Add more tests
- Clean up apply_edit()
- Selected objects list
- Object groups dict similar to trigger dict and rework all obj.selected checking
- When recomputing object, only recompute rotation if it's changed, if not just add x and y to the existing points
- Rebuild buckets for individual objects while keeping z-order
- Linux/Mac file name compatability
- Too much dependency on Game class, experiment with multiple classes
- Undo redo history list memory optimization

Features
- Multi-select bounding box
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