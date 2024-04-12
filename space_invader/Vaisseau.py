#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import pygame


class vaisseau(pygame.sprite.Sprite):
    def __init__(self):
        self.image = pygame.image.load(
            os.path.join(os.path.dirname(__file__), "Images/ship1.png")
        )
        pygame.sprite.Sprite.__init__(self)
        self.rect = self.image.get_rect()
        self.rect.center = (400, 500)
        self.pv = 100
        self.ulti = 50
        self.tir = False

    def aller_a_droite(self, pas):
        if self.rect.right < 800:
            self.rect.center = (self.rect.center[0] + pas, 500)

    def take_damage(self):
        self.pv -= 5
        if self.pv <= 0:
            sys.exit()

    def aller_a_gauche(self, pas):
        if self.rect.left > 0:
            self.rect.center = (self.rect.center[0] - pas, 500)
