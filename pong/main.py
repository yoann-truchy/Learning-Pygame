import math
from random import randint, random, uniform
from time import sleep
import time

import pygame
from Ball import Ball
from Constants import *
from Game_types import Game_config, Screen_config
from Player import Player


class Pong_pygame:
    def __init__(self) -> None:
        """Init the game variables"""
        self.init_config()
        self.game_clock = pygame.time.Clock()
        pygame.init()
        self.is_running = True


        # usefull lists and dicts
        self.player_list: list[Player] = list()
        self.ball_list: list[Ball] = list()
        self.border_list: list[pygame.Rect] = list()
        # key: shape (pygame object)
        self.debug_drawing_list: dict[str, any] = dict()

        # create fonts
        pygame.font.init()
        self.fonts = {}
        self.fonts["default"] = pygame.font.SysFont("Calibri", 16)
        self.fonts["big_debug"] = pygame.font.SysFont("Calibri", 56)

        # init screen
        self.screen = pygame.display.set_mode(
            (self.config.screen.width, self.config.screen.height)
        )
        self.screen.fill(self.config.backgroud_color)
        pygame.display.set_caption("PyPong")
        pygame.display.flip()

        # create players, borders, balls
        self.create_arena()
        self.create_players()

        default_ball = Ball(
            radius=BALL_RADIUS,
            x_speed=BALL_X_INITIAL_SPEED * random_sign(),
            y_speed=BALL_Y_INITIAL_SPEED * random_sign(),
            ball_color=self.config.ball_color,
        )
        default_ball.set_position(
            self.config.screen.width / 2, self.config.screen.height / 2
        )
        self.ball_list.append(default_ball)

        self.score = {"left": 0, "right": 0}

    def init_config(self):
        """Load the game configuration"""
        # TODO: implement a config file
        self.config = Game_config(
            debug=True,
            screen=Screen_config(max_refresh_rate=120)
        )

    def create_players(self):
        # init sprites
        # player is roughtly 14% of the screen
        player_length = self.config.screen.height * PLAYER_SCREEN_RATIO

        # left player
        self.player_l = Player(
            width=PLAYER_WIDTH,
            length=player_length,
            color=self.config.player_color,
        )

        # right player
        self.player_r = Player(
            width=PLAYER_WIDTH,
            # TESTING
            # length=player_length,
            length=self.config.screen.height - 60,
            color=self.config.player_color,
        )

        # place player
        self.player_l.set_center_position(
            postion_x=25, position_y=self.config.screen.height / 2
        )
        self.player_r.set_center_position(
            postion_x=self.config.screen.width - 25,
            position_y=self.config.screen.height / 2,
        )

        # add player to sprite group and list
        self.player_list.append(self.player_l)
        self.player_list.append(self.player_r)

    def create_arena(self):
        # calculate borders based on screen resolution
        borders_to_be_created = [
            # top border
            (TOP_LEFT, (self.config.screen.width, BORDER_HEIGTH)),
            # bottom border
            (
                (0, self.config.screen.height - BORDER_HEIGTH),
                (self.config.screen.width, BORDER_HEIGTH),
            ),
        ]

        # goal hitboxes
        self.left_goal = pygame.Rect(
            (-50, 0),
            (50, self.config.screen.height),
        )
        self.right_goal = pygame.Rect(
            (self.config.screen.width, 0),
            (50, self.config.screen.height),
        )

        for border in borders_to_be_created:
            self.border_list.append(pygame.Rect(*border))

    def handle_event(self):
        """Run code based on events"""
        # All events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

        # KEY PRESSES
        keys = pygame.key.get_pressed()

        if keys[getattr(pygame, f"K_{self.config.mapping.player1_up_key}")]:
            self.player_l.set_acceleration(-PLAYER_ACCELERATION)
        elif keys[getattr(pygame, f"K_{self.config.mapping.player1_down_key}")]:
            self.player_l.set_acceleration(PLAYER_ACCELERATION)
        else:
            self.player_l.set_acceleration(0)
        if keys[pygame.K_ESCAPE]:
            self.is_running = False
            
        self.mouse_pos = pygame.mouse.get_pos()

    def update(self):
        """Game logic such as collisions and different calculations"""
        # get delta time
        self.dt = self.game_clock.tick(self.config.screen.max_refresh_rate)
        time_update_start = pygame.time.get_ticks()

        # logic for players
        for player in self.player_list:
            player.update(self.dt)
            # check that players are not out of bound
            if (
                player.rect.centery > self.config.screen.height
                or player.rect.centery < 0
            ):
                # put player at their orignal place
                player.rect.centery = self.config.screen.height // 2

            # check collision with borders
            player_collision_with_border = player.rect.collideobjects(self.border_list)

            if player_collision_with_border:
                y_distance_with_border = (
                    player.rect.centery - player_collision_with_border.centery
                )
                sign_direction = 1 if y_distance_with_border > 0 else -1
                # if y is positive, move down, else move up
                y_distance_to_move = sign_direction * (
                    ((BORDER_HEIGTH / 2) + (player.length / 2))
                    - abs(y_distance_with_border)
                )
                player.move_y(y_distance_to_move)

        # ball
        for i, ball in enumerate(self.ball_list):

            ball.update(self.dt)

            # goals
            if ball.rect.centerx < 0 or ball.rect.centerx > self.config.screen.width:
                if ball.rect.centerx < 0:
                    self.score["right"] += 1
                else:
                    self.score["left"] += 1

                # if more than 1 ball, remove it when scoring
                if len(self.ball_list) > 1:
                    self.ball_list.pop(i).kill()
                    continue
                else:
                    # TODO: logic when goal scored
                    # For now, ball is set to middle of screen
                    ball.set_position(
                        self.config.screen.width / 2, self.config.screen.height / 2
                    )
                    ball.set_velocity(
                        x_speed=BALL_X_INITIAL_SPEED
                        * uniform(0.75, 1.25)
                        * random_sign(),
                        y_speed=BALL_Y_INITIAL_SPEED
                        * uniform(0.75, 1.25)
                        * random_sign(),
                    )
                    ball.speed_increase_counter = 0
                    continue

            # ball is out of bound
            # TODO: handle out of bound better, for now the ball is just deleted
            if ball.rect.centery > self.config.screen.height or ball.rect.centery < 0:
                self.ball_list.pop(i).kill()
                continue

            # collision with borders
            ball_collision_with_border = ball.rect.collideobjects(self.border_list)
            if ball_collision_with_border:
                ball.calculate_collision_with_rect(ball_collision_with_border)

            # collision with players
            # TODO: make collision more forgiving
            ball_collision_with_player = ball.rect.collideobjects(self.player_list)
            if ball_collision_with_player:
                ball.calculate_collision_with_rect(ball_collision_with_player.rect)
                # add speed X speed and change Y speed based on player's speed
                y_offset = ball.rect.centery - player.rect.centery
                ball.y_speed += (y_offset / 500) + (player.speed / 3)
                ball.increase_speed()

        time_update_stop = pygame.time.get_ticks()
        self.update_time = time_update_stop - time_update_start

    def render(self):
        """Draw sprites and other element on the screen"""
        time_render_start = pygame.time.get_ticks()
        # redraw background
        self.screen.fill(self.config.backgroud_color)

        # draw borders, players, balls
        for border in self.border_list:
            pygame.draw.rect(self.screen, WHITE, border)
        for player in self.player_list:
            player.draw(self.screen)
        for ball in self.ball_list:
            ball.draw(self.screen)

        time_render_stop = pygame.time.get_ticks()
        self.render_time = time_render_stop - time_render_start

        if self.config.debug:
            self.render_debug()
        
        pygame.display.update()

    def render_debug(self):
        debug_position = (
            self.config.screen.width - 250,
            self.config.screen.height - 45,
        )

        for debug_name, debug_drawing in self.debug_drawing_list.items():
            debug_drawing[0](*debug_drawing[1])


        debug_lines = [
            f"FPS: {round(self.game_clock.get_fps())}",
            f"update: {self.update_time} ms",
            f"update: {self.render_time} ms",
            f"dt: {self.dt} ms",
            f"player speed: {self.player_l.speed:.4f}",
            f"ball X speed: {self.ball_list[0].x_speed:.4f}",
            f"ball Y speed: {self.ball_list[0].y_speed:.4f}",
        ]

        for i, debug_line_txt in enumerate(debug_lines):
            line_x_position = debug_position[0]
            line_y_position = debug_position[1] - DEBUG_LINE_SPACING * i
            line_position = (line_x_position, line_y_position)

            text_object = self.fonts["default"].render(
                str(debug_line_txt), False, WHITE
            )
            self.screen.blit(text_object, line_position)

    def run(self):
        """game loop"""
        while self.is_running:
            self.handle_event()
            self.update()
            self.render()


def random_sign():
    return 1 if random() < 0.5 else -1


if __name__ == "__main__":
    game = Pong_pygame()
    game.run()
