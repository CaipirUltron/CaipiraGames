from classes.character import Character

class Player(Character):
    """ 
    Class for the player character. The implementation of player controls can be found here.
    """
    def followMouse(self, mouse_x, mouse_y):
        error_x = mouse_x - self.x
        error_y = mouse_y - self.y
        norm_error = ( error_x**2 + error_y**2 )**0.5
        if norm_error > 100:
            self.k = 2.0
        else:
            self.k = 20.0
        self.speed_x = self.k*error_x
        self.speed_y = self.k*error_y

    def startMovement(self, pressed_key):
        if pressed_key == pygame.K_LEFT:
            self.speed_x += -1
        if pressed_key == pygame.K_RIGHT:
            self.speed_x += +1
        if pressed_key == pygame.K_UP:
            self.speed_y += -1
        if pressed_key == pygame.K_DOWN:
            self.speed_y += +1

    def endMovement(self, released_key):
        if released_key == pygame.K_LEFT:
            self.speed_x -= -1
        if released_key == pygame.K_RIGHT:
            self.speed_x -= +1
        if released_key == pygame.K_UP:
            self.speed_y -= -1
        if released_key == pygame.K_DOWN:
            self.speed_y -= +1
