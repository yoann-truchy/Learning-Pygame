#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import pygame


class missile(pygame.sprite.Sprite):
    def __init__(self, e, x, y, v):
        pygame.sprite.Sprite.__init__(self)

        if e == 1:
            self.image = pygame.image.load(
                os.path.join(os.path.dirname(__file__), "Images/tir.png")
            )
            self.rect = self.image.get_rect()
            self.rect.midbottom = (x, y)
        else:
            self.image = pygame.image.load(
                os.path.join(os.path.dirname(__file__), "Images/tir_enemy.png")
            )
            self.rect = self.image.get_rect()
            self.rect.midtop = (x, y)

        self.vitesse = v

    def update(self):
        pygame.sprite.Sprite.update(self)
        self.rect.move_ip(0, self.vitesse)
        if self.rect.bottom < 0 or self.rect.top > 800:
            pygame.sprite.Sprite.kill(self)
            self.rect.center = (1000, -25)
