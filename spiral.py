import pygame, sys, random, math
from pygame.locals import *

class Dot():
    def __init__(self, x, y, addAngle=5, increase=0):
        self.x, self.y = x, y
        self.dist = y-450
        self.angle = 0

        self.addAngle = addAngle
        self.increase = increase

    def move(self):
        self.angle+=self.dist/self.addAngle
        self.x=800+math.cos(math.radians(self.angle))*self.dist
        self.y=450+math.sin(math.radians(self.angle))*self.dist
        self.dist+=self.increase

class Spiral():
    def __init__(self, screen, numberDots=500, thickness=4, size=400, color=pygame.Color("BLACK")):
        self.numberDots = numberDots
        self.thickness = thickness
        self.screen = screen
        self.size = size
        self.color = color

        self.dots = [] 
        for i in range(self.numberDots):
            self.dots.append(Dot(450,450+i*self.size/self.numberDots))

    def draw(self,number):
        if number != 0:
            pygame.draw.line(self.screen,self.color,(self.dots[number].x,self.dots[number].y),(self.dots[number-1].x,self.dots[number-1].y),self.thickness)

    def drawDots(self):
        number=0
        for dot in self.dots:
            self.draw(number)
            dot.move()
            number+=1