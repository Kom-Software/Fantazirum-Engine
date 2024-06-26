import pygame as pg
import pygame.event

class Play(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)

        self.org = pg.image.load("files/sprites/play.png")
        self.hov = pg.image.load("files/sprites/play_hover.png")
        self.image = self.org
        self.rect = self.image.get_rect()
    def update(self):
        pos = pygame.mouse.get_pos()
        hover = self.rect.collidepoint(pos)

        self.image = self.hov if hover else self.org

class Stop(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)

        self.org = pg.image.load("files/sprites/stop.png")
        self.hov = pg.image.load("files/sprites/stop_hover.png")
        self.image = self.org
        self.rect = self.image.get_rect()
    def update(self):
        pos = pygame.mouse.get_pos()
        hover = self.rect.collidepoint(pos)

        self.image = self.hov if hover else self.org
