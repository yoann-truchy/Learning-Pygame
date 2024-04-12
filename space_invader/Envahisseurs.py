#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import pygame
from random import choice, random
from Tirs import *


class alien(pygame.sprite.Sprite):
    def __init__(self, lig, col):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(
            os.path.join(os.path.dirname(__file__), "Images/alien2.png")
        )
        self.rect = self.image.get_rect()
        self.PV = 100
        self.rect.center = (col * 55, lig * 55)
        if random() < 0.5:
            self.vitesse_x = 5
        else:
            self.vitesse_x = -5
        self.vitesse_y = 1

    def descendre(self):
        self.rect.center = (self.rect.center[0], self.rect.center[1] + 55)

    def take_damage(self, dmg):
        self.PV -= dmg
        if self.PV <= 50:  # pv de l'alien a 50 ou en dessous
            self.image = pygame.image.load(
                os.path.join(os.path.dirname(__file__), "Images/alien2_degat.png")
            )
        if self.PV <= 0:
            pygame.sprite.Sprite.kill(self)
            self.rect.center = (100000, -1000000)

    def update(self):
        pygame.sprite.Sprite.update(self)
        self.rect.move_ip(self.vitesse_x, self.vitesse_y)
        if self.rect.bottom > 432:
            pygame.sprite.Sprite.kill(self)
            self.rect.center = (100000, -1000000)
            sys.exit()
