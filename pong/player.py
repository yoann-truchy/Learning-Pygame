import pygame
from constants import *


class Player():
    def __init__(
        self,
        width,
        length,
        color,
    ) -> None:
        super().__init__()
        # player rectangle
        self.image = pygame.Surface((width, length))
        self.rect = self.image.fill(color)
        # place player
        self.acceleration = 0
        self.drag = PLAYER_DRAG
        self.speed = 0
        self.length = length

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

    def set_position(self, postion_x, position_y):
        self.rect.topleft = (postion_x, position_y)

    def set_center_position(self, postion_x, position_y):
        self.rect.center = (postion_x, position_y)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
