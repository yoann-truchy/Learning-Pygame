import math
from typing import Literal
from random import randint, random, uniform
from time import sleep
import time

import pygame
from Ball import Ball
from Constants import *
from Game_types import Game_config, Screen_config
from Player import Player, AI_player
from Debug import Debug_window


class Pong_pygame:
    def __init__(self) -> None:
        """Init the game variables"""
        self.init_config()
        self.game_clock = pygame.time.Clock()
        pygame.init()
        self.running = True
        self.paused = False
        self.debug_window = None

        # variables
        self.ai_prediction_event = pygame.event.custom_type()
        self.ball_reset_event = pygame.event.custom_type()
        self.court_size = self.config.screen.height - (2 * BORDER_HEIGTH)

        # usefull lists and dicts
        self.player_list: list[Player] = list()
        self.ai_player_list: list[AI_player] = list()
        self.ball_list: list[Ball] = list()
        self.border_list: list[pygame.Rect] = list()
        self.debug_lines: dict[str, str] = dict()
        # key: shape (pygame object)
        self.debug_drawing_list: dict[str, any] = dict()

        # create fonts
        pygame.font.init()
        self.font_default = pygame.font.SysFont("Calibri", 16)
        self.font_score = pygame.font.SysFont("Calibri", 56)

        # init screen
        self.screen = pygame.display.set_mode(
            (self.config.screen.width, self.config.screen.height)
        )
        self.screen.fill(self.config.backgroud_color)
        pygame.display.set_caption("PyPong")
        pygame.display.flip()

        # create players, borders, balls
        self.create_arena()
        self.create_ball()
        self.create_players()

        self.score = {"left": 0, "right": 0}

    def init_config(self):
        """Load the game configuration"""
        # TODO: implement a config file
        self.config = Game_config(
            debug=True,
            screen=Screen_config(max_refresh_rate=120),
            backgroud_color=(30, 30, 75),
        )

    def create_ball(self, initial_direction: Literal[-1, 1] = None):
        if initial_direction is None:
            ball_direction = random_sign()
        else:
            ball_direction = initial_direction

        ball = Ball(
            radius=BALL_RADIUS,
            x_speed=BALL_X_INITIAL_SPEED * ball_direction,
            y_speed=BALL_Y_INITIAL_SPEED * ball_direction,
            ball_color=self.config.ball_color,
        )
        ball.set_position(self.config.screen.width / 2, self.config.screen.height / 2)
        self.ball_list.append(ball)

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
        self.player_r = AI_player(
            width=PLAYER_WIDTH,
            length=player_length,
            color=self.config.player_color,
        )

        # create event for AI player on a timer
        pygame.time.set_timer(
            pygame.event.Event(
                self.ai_prediction_event,
            ),
            500,
        )

        # place player
        self.player_l.set_center_position(
            postion_x=PLAYER_POSITION_PADDING, position_y=self.config.screen.height / 2
        )
        self.player_r.set_center_position(
            postion_x=self.config.screen.width - PLAYER_POSITION_PADDING,
            position_y=self.config.screen.height / 2,
        )

        # add player to sprite group and list
        self.player_list.append(self.player_l)
        self.player_list.append(self.player_r)

        for p in self.player_list:
            if isinstance(p, AI_player):
                self.ai_player_list.append(p)

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
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused

                # update and render once
                if event.key == pygame.K_f:
                    self.update_and_render()

            # MOUSE
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if (
                        self.debug_window is not None
                        and self.debug_window.rect.collidepoint(event.pos)
                    ):
                        self.debug_window.drag_start(event.pos)

            elif event.type == pygame.MOUSEMOTION:
                if self.debug_window is not None and self.debug_window.is_dragged:
                    self.debug_window.drag_at(event.pos)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.debug_window is not None:
                        self.debug_window.drag_stop()

            # CUSTOM EVENTS
            # reset ball after goal
            elif event.type == self.ball_reset_event:
                ball_x_direction = event.x_direction
                self.create_ball(ball_x_direction)

            elif event.type == self.ai_prediction_event:
                ball_point_prediction = self.ball_prediction()
                if ball_point_prediction is None:
                    break
                ball_rect_prediction = pygame.Rect((0, 0), (20, 20))
                ball_rect_prediction.center = ball_point_prediction
                self.debug_drawing_list["prediction_rect"] = [
                    pygame.draw.rect,
                    (self.screen, RED, ball_rect_prediction),
                ]
                for ai in self.ai_player_list:
                    # distance from player to ball
                    try:
                        dist_from_ball = ai.rect.centerx - self.ball_list[0].pos[0]
                    except IndexError:
                        dist_from_ball = 0
                    # add random error to prediction
                    # the closer to the player, the more accurate it is
                    prediction_offset = randint(-ai.error_offset, ai.error_offset)
                    prediction_ratio = 2 * (
                        abs(dist_from_ball) / self.config.screen.width
                    )
                    error_offset = prediction_offset * prediction_ratio
                    self.debug_lines["prediction offset"] = str(prediction_offset)
                    self.debug_lines["prediction ratio"] = str(prediction_ratio)
                    self.debug_lines["error offset"] = str(error_offset)

                    ball_rect_prediction_with_error = pygame.Rect((0, 0), (100, 20))
                    ball_rect_prediction_with_error.center = (
                        ball_point_prediction[0],
                        ball_point_prediction[1] + error_offset,
                    )
                    self.debug_drawing_list["prediction_rect_err"] = [
                        pygame.draw.rect,
                        (self.screen, GREEN, ball_rect_prediction_with_error),
                    ]

                    y_distance_from_prediction = (
                        ball_rect_prediction_with_error.centery - ai.rect.centery
                    )
                    self.debug_lines["y_distance from prediction"] = str(
                        y_distance_from_prediction
                    )

                    y_distance_sign = 1 if y_distance_from_prediction > 0 else -1
                    ai.set_acceleration(y_distance_sign * PLAYER_ACCELERATION)

        # KEY PRESSES
        keys = pygame.key.get_pressed()

        if keys[getattr(pygame, f"K_{self.config.mapping.player1_up_key}")]:
            self.player_l.set_acceleration(-PLAYER_ACCELERATION)
        elif keys[getattr(pygame, f"K_{self.config.mapping.player1_down_key}")]:
            self.player_l.set_acceleration(PLAYER_ACCELERATION)
        else:
            self.player_l.set_acceleration(0)
        if keys[pygame.K_ESCAPE]:
            self.running = False

        self.mouse_pos = pygame.mouse.get_pos()

    def update(self):
        """Game logic such as collisions and different calculations"""
        time_update_start = pygame.time.get_ticks()

        # logic for players
        for player in self.player_list:
            # update movement
            player.update(self.dt)

            # let ai move
            if player.ai_controlled:
                # move to prediction
                pass

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

        try:
            self.debug_lines.update(
                {
                    "ball X speed": f"{self.ball_list[0].x_speed:.0f} pixel/s",
                    "ball X speed": f"{self.ball_list[0].x_speed * self.dt:.4f} pixel/update",
                    "ball Y speed": f"{self.ball_list[0].y_speed:.0f} pixel/s",
                    "ball Y speed": f"{self.ball_list[0].y_speed * self.dt:.4f} pixel/update",
                    "ball speed counter": f"{self.ball_list[0].speed_increase_counter}",
                }
            )
        except IndexError:
            pass

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
                    # in the event of multiple balls being present (powerups or gamemodes)
                    self.ball_list.pop(i)
                    continue
                else:
                    # create an event to reset the ball afet N ms
                    # the goal is going in the direction on the last scored goal
                    pygame.time.set_timer(
                        pygame.event.Event(
                            self.ball_reset_event,
                            x_direction=-1 if ball.x_speed < 0 else 1,
                        ),
                        1500,
                        1,
                    )
                    self.ball_list.pop(i)

            # ball is out of bound
            # TODO: handle out of bound better, for now the ball is just deleted
            if ball.rect.centery > self.config.screen.height or ball.rect.centery < 0:
                self.ball_list.pop(i)
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
                ball.y_speed = 450 * random_sign()
                ball.increase_speed()
                self.ball_prediction()

        time_update_stop = pygame.time.get_ticks()
        self.update_time = time_update_stop - time_update_start

    def ball_prediction(self):
        try:
            ball = self.ball_list[0]
        except IndexError:
            return None

        # get the x posistions where the ball can intersect with player
        player_displacement = PLAYER_POSITION_PADDING + (PLAYER_WIDTH // 2)
        min_x = player_displacement + ball.radius
        max_x = self.config.screen.width - player_displacement - ball.radius
        self.debug_lines["court size"] = f"court size : {self.court_size}"

        # get the direction of the ball
        x_intersection = min_x if ball.x_speed < 0 else max_x
        self.debug_drawing_list["x_intersection"] = [
            pygame.draw.line,
            (
                self.screen,
                BLUE,
                (x_intersection, 0),
                (x_intersection, self.config.screen.height),
                4,
            ),
        ]

        # calculate the time where x = minX or x = maxX
        t_until_collision = (x_intersection - ball.pos[0]) / ball.x_speed
        self.debug_lines["collision in"] = f"collision in: {t_until_collision:.4f} s"

        # get Y for t calculated before
        y_distance_traveled = ball.y_speed * t_until_collision
        y_intersection = ball.pos[1] + (y_distance_traveled)

        # get y position factoring in bounces
        topmost = BORDER_HEIGTH + ball.radius
        botmost = self.config.screen.height - BORDER_HEIGTH - ball.radius
        n_bounce = 0
        while y_intersection < topmost or y_intersection > botmost:
            if y_intersection < topmost:
                y_intersection = topmost + (topmost - y_intersection)
            elif y_intersection > botmost:
                y_intersection = botmost - (y_intersection - botmost)
            n_bounce += 1

        self.debug_drawing_list["y_intersection"] = [
            pygame.draw.line,
            (
                self.screen,
                BLUE,
                (0, y_intersection),
                (self.config.screen.width, y_intersection),
                4,
            ),
        ]

        return (x_intersection, y_intersection)

    def render(self):
        """Draw sprites and other element on the screen"""
        # redraw background
        self.screen.fill(self.config.backgroud_color)
        time_render_start = pygame.time.get_ticks()

        # draw borders, players, balls
        for border in self.border_list:
            pygame.draw.rect(self.screen, WHITE, border)
        for player in self.player_list:
            player.draw_on(self.screen)
        for ball in self.ball_list:
            ball.draw_on(self.screen)

        # draw score
        l_score_txt = self.font_score.render(str(self.score["left"]), True, WHITE)
        r_score_txt = self.font_score.render(str(self.score["right"]), True, WHITE)
        self.screen.blits(
            blit_sequence=[
                ((l_score_txt), (self.config.screen.width / 3, SCORE_Y)),
                (r_score_txt, (2 * self.config.screen.width / 3, SCORE_Y)),
            ]
        )

        time_render_stop = pygame.time.get_ticks()
        self.render_time = time_render_stop - time_render_start

        if self.config.debug:
            self.render_debug()

        pygame.display.update()

    def render_debug(self):
        if self.debug_window == None:
            # debug surface which debug text will be drawn on
            self.debug_window = Debug_window((0, 0))

        try:
            for pos in self.ball_list[0].position_list:
                pygame.draw.rect(self.screen, RED, (pos, (2, 2)))

        except:
            pass

        # debug drawings
        for debug_name, debug_drawing in self.debug_drawing_list.items():
            debug_drawing[0](*debug_drawing[1])

        # draw lines
        debug_lines_to_render = [
            f"FPS: {self.fps:.0f}",
            f"update: {self.update_time} ms",
            f"render: {self.render_time} ms",
            f"dt: {self.dt} s",
        ]

        for name, value in self.debug_lines.items():
            debug_lines_to_render.append(f"{name}: {value}")

        self.debug_window.render_lines(debug_lines_to_render, self.screen)

    def pause(self, state: bool = None):
        if state is None:
            pause_desired = not self.pause
        else:
            pause_desired = state

        if pause_desired:
            black_tint_surface = pygame.Surface(
                (
                    self.config.screen.width,
                    self.config.screen.height,
                ),
                flags=pygame.SRCALPHA,
            )

            self.screen.blit(
                pygame.draw.rect(black_tint_surface, black_tint_surface.get_rect()),
                (0, 0),
            )
            pygame.display.update()

    def tick(self):
        self.dt = self.game_clock.tick(self.config.screen.max_refresh_rate) / 1000
        self.fps = self.game_clock.get_fps()

    def update_and_render(self):
        self.update()
        self.render()

    def run(self):
        """game loop"""
        while self.running:
            self.tick()
            self.handle_event()
            if not self.paused:
                self.update_and_render()


def random_sign():
    return 1 if random() < 0.5 else -1


if __name__ == "__main__":
    game = Pong_pygame()
    game.run()
