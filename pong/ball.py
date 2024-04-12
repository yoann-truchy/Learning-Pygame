from token import NUMBER
import pygame
import math
from constants import *


class Ball(pygame.sprite.Sprite):
    def __init__(
        self,
        radius,
        x,
        y,
        x_speed,
        y_speed,
        ball_color=WHITE,
    ) -> None:
        super().__init__()
        # ball rectangle
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            self.image,
            ball_color,
            (radius, radius),
            radius,
        )
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        # place ball
        self.radius = radius
        self.rect.topleft = (x, y)
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.max_speed = 1.2
        self.accel = 0
        self.speed_increase_counter = 0

    def move(self, x_distance, y_distance):
        current_x, current_y = self.rect.center
        self.rect.center = (current_x + x_distance, current_y + y_distance)

    def increase_speed(self):
        x_speed_sign = 1 if self.x_speed > 0 else -1
        # linear
        # new_speed = BALL_X_INITIAL_SPEED + number * 0.1
        # sigmoid
        new_speed = 0.12 + (1.2 / (1 + (6 * math.exp(-0.2 * self.speed_increase_counter))))
        self.speed_increase_counter += 2

        self.x_speed = new_speed * x_speed_sign

    def update(self, dt):
        current_x, current_y = self.rect.center
        x_speed_sign = 1 if self.x_speed > 0 else -1
        y_speed_sign = 1 if self.y_speed > 0 else -1

        self.x_speed += self.accel * x_speed_sign
        self.y_speed += self.accel * y_speed_sign

        if self.x_speed > self.max_speed:
            self.x_speed = self.max_speed * x_speed_sign
        if self.y_speed > self.max_speed:
            self.Y_speed = self.max_speed * y_speed_sign

        self.move(self.x_speed * dt, self.y_speed * dt)

    def calculate_collision_with_rect(self, collission_rect: pygame.Rect):
        top_point = (self.rect.centerx, self.rect.top)
        bot_point = (self.rect.centerx, self.rect.bottom)
        left_point = (self.rect.left, self.rect.centery)
        right_point = (self.rect.right, self.rect.centery)

        # check which side of the rect the ball collided with
        return_flag = False
        if collission_rect.collidepoint(bot_point):
            # top side
            self.y_speed = -abs(self.y_speed)
            return_flag = True
        if collission_rect.collidepoint(top_point):
            # bottom side
            self.y_speed = abs(self.y_speed)
            return_flag = True
        if collission_rect.collidepoint(right_point):
            # left side
            self.x_speed = -abs(self.x_speed)
            return_flag = True
        if collission_rect.collidepoint(left_point):
            # right side
            self.x_speed = abs(self.x_speed)
            return_flag = True

        if return_flag:
            return
        else:
            # collision with corner
            x_distance_from_rect = self.rect.centerx - collission_rect.centerx
            y_distance_from_rect = self.rect.centery - collission_rect.centery

            # center of ball regardering corner
            if y_distance_from_rect > 0 and x_distance_from_rect > 0:
                # bottom right collision
                corner_position = collission_rect.bottomright
            elif y_distance_from_rect < 0 and x_distance_from_rect > 0:
                # top right
                corner_position = collission_rect.topright
            elif y_distance_from_rect < 0 and x_distance_from_rect < 0:
                # top left
                corner_position = collission_rect.topleft
            elif y_distance_from_rect > 0 and x_distance_from_rect < 0:
                # bottom left
                corner_position = collission_rect.bottomleft

            corner_x_distance = corner_position[0] - self.rect.centerx
            corner_y_distance = corner_position[1] - self.rect.centery
            distance_from_corner = math.sqrt(
                (corner_x_distance**2) + (corner_y_distance**2)
            )

            if distance_from_corner > self.radius:
                # no collision
                return

            x_bigger = abs(corner_x_distance) > abs(corner_y_distance)
            y_bigger = abs(corner_x_distance) < abs(corner_y_distance)

            if corner_y_distance > 0 and y_bigger:
                # more top
                self.y_speed = -abs(self.y_speed)
            elif corner_y_distance < 0 and y_bigger:
                # more bot
                self.y_speed = abs(self.y_speed)
            elif corner_x_distance > 0 and x_bigger:
                # more left
                self.x_speed = -abs(self.x_speed)
            elif corner_x_distance < 0 and x_bigger:
                # more right
                self.x_speed = abs(self.x_speed)
            else:
                # ????
                txt = "fuck"

    def set_position(self, x, y):
        self.rect.topleft = (x, y)

    def set_velocity(self, x_speed, y_speed):
        self.x_speed = x_speed
        self.y_speed = y_speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)
