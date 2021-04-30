# CaipiraGames

Project is structured in the following way:

Abstract class Scene: abstract class for scripting game scenes, such as menus, loading screens, gameover, credits and the game itself. Contains a bool self.running for controlling the execution of the main while loop at the runningLoop method. Child Scene classes can inherit a fixed FPS value for the scene, implemented through pygame.time.Clock().

The class contains four main methods: 

(1) @abstractmethod eventHandler: receives an event from the queue and processes it according to the scene logic. [must be implemented]

(2) @abstractmethod updateLogic: updates the scene state, encapsulating the scene logic. [must be implemented]

(3) @abstractmethod updateDisplay: updates the display for the given scene. [must be implemented]

(4) runningLoop: main while loop for the Scene.