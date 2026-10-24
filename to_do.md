Bugs:
- Spawning inside an object doesn't activate it
- Text objects get rendered based on original square width
- Frame stepping desyncs music
- Shift to multiselect objects, release mouse while hovering over selected object, object gets deselected
- Object menu doesn't work correctly with multi select, check also when deleting objects while start pos is selected
- Object menu resets if pressing enter in a field belonging to checkpoint or trigger

Optimization/structuring
- Selected objects list, rework all obj.selected checking
- When recomputing object, only recompute rotation if it's changed, if not just add x and y to the existing points
- Rebuild buckets for individual objects while keeping z-order
- Undo redo history list memory optimization
- Add more tests
- Linux/Mac file name compatability
- Too much dependency on Game class, experiment with multiple classes

Features
- User music delay
- Level music volume
- Triggers display trigger id while in build mode
- All objects show their attributes if all selected have the same
- Ctrl+alt+scroll to change hitboxes faster
- Show dash orb pointing
- Multi-select bounding box
- Default level sizes
- Multi-point shape
- Combining shapes and transparent shapes into a single multi-point shape
- Checkpoints store level settings
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