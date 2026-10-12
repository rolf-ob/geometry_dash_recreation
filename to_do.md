Update v1.1.0
- Trigger transition speed
- Main levels
- Pyinstaller exe file

Bugs:
- Object menu doesn't work correctly with multi select, check also when deleting objects while start pos is selected

Optimization/structuring
- Add more tests
- Clean up apply_edit()
- Selected objects list
- Object groups dict similar to trigger dict and rework all obj.selected checking
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