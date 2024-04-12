import pygame
from constants import *


class Player(pygame.sprite.Sprite):
    def __init__(
        self,
        x_starting_pos,
        y_starting_pos,
        width,
        length,
    ) -> None:
        super().__init__()
        # player rectangle
        self.image = pygame.Surface((width, length))
        self.rect = self.image.fill(PLAYER_COLOR)
        # place player
        self.rect.topleft = (x_starting_pos, y_starting_pos)
        self.acceleration = 0
        self.drag = PLAYER_DRAG
        self.speed = 0

    def set_acceleration(self, accel):
        self.acceleration = accel

    def set_drag(self, drag):
        self.acceleration = drag
    
    def set_speed(self, speed):
        self.speed = speed

    def update(self, dt=1):
        self.speed += self.acceleration
        self.speed_sign = 1 if self.speed > 0 else -1

        if self.speed > 0:
            self.speed -= self.drag
            if self.speed < 0:
                self.speed = 0
        else:
            self.speed += self.drag
            if self.speed > 0:
                self.speed = 0
            

        if abs(self.speed) > PLAYER_MAX_SPEED:
            self.speed = PLAYER_MAX_SPEED * self.speed_sign

        self.move_y(self.speed * dt)

    def move_y(self, y_distance):
        current_x, current_y = self.rect.center
        self.rect.center = (current_x, current_y + y_distance)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
