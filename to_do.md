recomputing width and height has to redo rotation computing
moving same object's x and y at the same time lags

Bugs:
- Text objects get rendered based on original square width
- Frame stepping desyncs music

Optimization/structuring
- Rebuild buckets for individual objects while keeping z-order
- Undo redo history list memory optimization
- Add more tests
- Linux/Mac file name compatability
- Too much dependency on Game class, experiment with multiple classes

Features
- User music delay
- Level music volume
- Ctrl+alt+scroll to change hitboxes faster
- Triggers display trigger id while in build mode
- Display next unused trigger id
- All objects show their attributes if all selected have the same
- Show dash orb pointing
- Multi-select bounding box
- Default level sizes
- Rotation trigger rotates around collective objects center
- Camera x, y and zoom trigger
- Checkpoints store level settings
- Music affected by speedhack
- Multi-point shape
- Combining shapes and transparent shapes into a single multi-point shape
- CBF

User
- Making private levels
- Public levels
- Public level stats like unique visitors, likes, dislikes, comments etc
- Changing controls and tutorial with it

UI
- Images/sprites
- Clickable UI menu and build mode