# CaipiraGames
My first big game project, with pygame and pymunk. 

**Installation instructions:**

$ *pip3 install pygame*

$ *pip3 install pymunk*

**Running instructions:** 

$ *python3 main.py*


Project is structured in the following way:

    ./classes

    ./images

    .main.py


**./classes/game.py:** Game() class. Contains high-level parameters and configurations for the game, such as max. running FPS, screen resolution, etc.
Initializes pygame and the main game screen. Contains methods for adding/removing/reseting/editing scenes, as well as transitioning between different scenes.

**./classes/scene.py:** (abstract) Scene() class for scripting game scenes, such as menus, loading screens, gameover, credits and the game itself. 
Contains the three abstract methods that must be implemented by the child classes:

*(i) eventHandler()*: handles events from the queue, processing them according to the scene logic.

*(ii) updateLogic()*: updates the scene state. All the scene logic must be implemented here in the child classes.

*(iii) updateDisplay()*: updates the game screen with the graphical elements of the scene (blits, surfaces and rect updates must go here).

Every scene has the fixed method *runningLoop()* that executes the scene while loop, checking events with *eventHandler()*, getting the mouse position, updating the scene logic with *updateLogic()* and updating the game screen with *updateDisplay()*.


Other classes:

**./classes/characters/player.py:** Player(Character) class for the player, handling the player movement, physics, and player state (life, counters, abilities, etc).

**./classes/enemy.py:** Enemy(Character) class an enemy. Contains basic logic to handle enemy movement, physics and state.


Other files contain classes for the game scenes. For now, a simple menu and the game itself are implemented in **./classes/scenes/menus/main_menu.py** and **./classes/scenes/ingame/level.py**.


Finally, **main.py** simply loops the *runningLoop()* method of the current active scene.
