import pygame as pg
import pygame.event
from main import *

class Play(pg.sprite.Sprite):
    def __init__(self, image):
        pg.sprite.Sprite.__init__(self)

        self.rect = self.image.get_rect()
        self.org = pg.image.load("files/sprites/play.png")
        self.hov = pg.image.load("files/sprites/play_hover.png")
        self.image = image
    def update(self, events):
        pos = pygame.mouse.get_pos()
        hover = self.rect.collidepoint(pos)

        self.image = self.hov if hover else self.org

class Stop(pg.sprite.Sprite):
    def __init__(self, image):
        pg.sprite.Sprite.__init__(self)

        self.rect = self.image.get_rect()
        self.org = pg.image.load("files/sprites/stop.png")
        self.hov = pg.image.load("files/sprites/stop_hover.png")
        self.image = image
    def update(self, events):
        pos = pygame.mouse.get_pos()
        hover = self.rect.collidepoint(pos)

        self.image = self.hov if hover else self.org

