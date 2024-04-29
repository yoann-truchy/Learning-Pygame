from token import NUMBER
import pygame
import math
from Constants import *


class Ball:
    def __init__(
        self,
        radius,
        x_speed,
        y_speed,
        ball_color=WHITE,
    ) -> None:
        # ball rectangle
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            self.image,
            ball_color,
            (radius, radius),
            radius,
        )
        self.rect = self.image.get_rect()
        self.prediction = self.rect.copy()
        self.pos = pygame.math.Vector2()
        self.radius = radius
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.speed_increase_counter = 0

    def move(self, x_distance, y_distance):
        current_x, current_y = self.rect.center
        self.rect.center = (current_x + x_distance, current_y + y_distance)

    def increase_speed(self):
        """increase the X speed based on the number of time the ball has been hit"""
        x_speed_sign = 1 if self.x_speed > 0 else -1
        # linear
        # new_speed = BALL_X_INITIAL_SPEED + number * 0.1
        # sigmoid
        new_speed = BALL_X_INITIAL_SPEED + (
            BALL_MAX_SPEED / (1 + (20 * math.exp(-0.32 * self.speed_increase_counter)))
        )
        self.speed_increase_counter += 1

        self.x_speed = new_speed * x_speed_sign

    def update(self, dt):
        current_x, current_y = self.rect.center
        x_speed_sign = 1 if self.x_speed > 0 else -1
        y_speed_sign = 1 if self.y_speed > 0 else -1

        # cap speed at max speed
        if abs(self.x_speed) > BALL_MAX_SPEED:
            self.x_speed = BALL_MAX_SPEED * x_speed_sign
        if abs(self.y_speed) > BALL_MAX_SPEED:
            self.y_speed = BALL_MAX_SPEED * y_speed_sign

        # calculate the next position
        x_distance = self.x_speed * dt
        y_distance = self.y_speed * dt
        current_x, current_y = self.pos
        self.pos = (current_x + x_distance, current_y + y_distance)
        # set center of rect to rounded pixel
        self.rect.center = (round(self.pos[0]), round(self.pos[1]))

        # self.move(self.x_speed * dt, self.y_speed * dt)

    def calculate_collision_with_rect(self, collission_rect: pygame.Rect):
        """Handles collision between the ball and the passed rect
        The main rule is that the ball will change it's X and Y speed based
        on what side of the rectangle it hits.
        Note: this makes hitting the ball with the player side NOT go to the opponent
        Maybe the collision with borders and players should be handle by different functions
        """
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
                raise NotImplementedError()

    def set_position(self, x, y):
        self.pos = (x, y)
        self.rect.topleft = (x, y)

    def set_velocity(self, x_speed, y_speed):
        self.x_speed = x_speed
        self.y_speed = y_speed

    def draw_on(self, surface):
        surface.blit(self.image, self.rect)
