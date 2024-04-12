import pygame
from random import randint, random, uniform
import math
from time import sleep
from player import Player
from ball import Ball
from constants import *


def main():
    game_clock = pygame.time.Clock()
    pygame.init()
    pygame.font.init()
    default_font = pygame.font.SysFont("Calibri", 16)
    big_font = pygame.font.SysFont("Calibri", 56)
    is_running = True
    debug_drawing_list = {}

    # init screen
    screen = pygame.display.set_mode((INITIAL_SCREEN_WIDTH, INITIAL_SCREEN_HEIGHT))
    screen.fill(BACKGROUD_COLOR)
    pygame.display.set_caption("PyPong")

    # init sprites
    sprite_group = pygame.sprite.Group()
    player_length = INITIAL_SCREEN_HEIGHT * PLAYER_SCREEN_RATIO
    player = Player(
        x_starting_pos=10,
        y_starting_pos=10,
        width=PLAYER_WIDTH,
        length=player_length,
    )
    sprite_group.add(player)
    player_list = [player]

    default_ball = Ball(
        radius=BALL_RADIUS,
        x=INITIAL_SCREEN_WIDTH /2,
        y=INITIAL_SCREEN_HEIGHT /2,
        x_speed=BALL_X_INITIAL_SPEED* random_sign(),
        y_speed=BALL_Y_INITIAL_SPEED*random_sign(),
        ball_color=BALL_COLOR,
    )
    ball_list = [default_ball]

    # random balls
    for i in range(0):
        ball = Ball(
            randint(15, 35),
            player.rect.centerx + 10,
            player.rect.centery,
            randint(3, 6) / 5,
            randint(3, 6) / 5,
            (randint(0, 255), randint(0, 255), randint(0, 255)),
        )
        ball_list.append(ball)

    # create borders
    borders_to_create = [
        # top border
        (TOP_LEFT, (INITIAL_SCREEN_WIDTH, BORDER_HEIGTH)),
        # bottom border
        (
            (0, INITIAL_SCREEN_HEIGHT - BORDER_HEIGTH),
            (INITIAL_SCREEN_WIDTH, BORDER_HEIGTH),
        ),
    ]

    # goal hitboxes
    left_goal = pygame.Rect(
        (-50, 0),
        (50, INITIAL_SCREEN_HEIGHT),
    )
    right_goal = pygame.Rect(
        (INITIAL_SCREEN_WIDTH, 0),
        (50, INITIAL_SCREEN_HEIGHT),
    )

    borders_to_create += [
        # right border
        (
            (INITIAL_SCREEN_WIDTH - BORDER_HEIGTH, 0),
            (BORDER_HEIGTH, INITIAL_SCREEN_HEIGHT),
        ),
    ]

    # TESTING
    # borders_to_create += [
    #     # left boder
    #     (TOP_LEFT, (BORDER_HEIGTH, INITIAL_SCREEN_HEIGHT)),
    #     # right border
    #     (
    #         (INITIAL_SCREEN_WIDTH - BORDER_HEIGTH, 0),
    #         (BORDER_HEIGTH, INITIAL_SCREEN_HEIGHT),
    #     ),
    #     # obstacles for testing
    #     ((150, 125), (300, 50)),
    #     ((300, 300), (50, 300)),
    #     ((750, 500), (300, 50)),
    #     ((875, 100), (50, 300)),
    # ]
    border_list: list[pygame.Rect] = []

    for border in borders_to_create:
        border_list.append(pygame.Rect(*border))

    left_score, right_score = 0, 0

    # ---------
    # MAIN LOOP
    # ---------
    while is_running:
        dt = game_clock.tick(FPS)
        time_update_start = pygame.time.get_ticks()

        # ---- EVENTS
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                is_running = False

        # cursor_position = pygame.mouse.get_pos()

        # ---- KEY PRESSES
        keys = pygame.key.get_pressed()
        if keys[pygame.K_z]:
            player.set_acceleration(-PLAYER_ACCELERATION)
        elif keys[pygame.K_s]:
            player.set_acceleration(PLAYER_ACCELERATION)
        else:
            player.set_acceleration(0)
        if keys[pygame.K_ESCAPE]:
            is_running = False

        # if keys[pygame.K_p]:
        #     ball.accel += 0.0001
        # elif keys[pygame.K_m]:
        #     ball.accel += 0.0001
            

        # ---- UPDATES
        # move player
        player.update(dt)

        # check for out of bound bugs
        if player.rect.centery > INITIAL_SCREEN_HEIGHT or player.rect.centery < 0:
            player.rect.centery = INITIAL_SCREEN_HEIGHT // 2

        # check for collisions
        # player
        player_collision_with_border = player.rect.collideobjects(border_list)
        if player_collision_with_border:
            y_distance_with_border = (
                # player_collision_with_border.centery - player.rect.centery
                player.rect.centery
                - player_collision_with_border.centery
            )
            if y_distance_with_border > 0:
                sign_direction = 1
            else:
                sign_direction = -1
            y_distance_to_move = sign_direction * (
                ((BORDER_HEIGTH / 2) + (player_length / 2))
                - abs(y_distance_with_border)
            )
            player.move_y(y_distance_to_move)
        else:
            y_distance_to_move = 0

        # ball
        for i, ball in enumerate(ball_list):

            ball.update(dt)

            # goals
            if ball.rect.centerx < 0:
                right_score += 1
                if len(ball_list) > 1:
                    ball_list.pop(i).kill()
                    continue
                else:
                    ball.set_position(
                        INITIAL_SCREEN_WIDTH / 2, INITIAL_SCREEN_HEIGHT / 2
                    )
                    ball.set_velocity(
                        x_speed=BALL_X_INITIAL_SPEED
                        * uniform(0.75, 1.25)
                        * random_sign(),
                        y_speed=BALL_Y_INITIAL_SPEED
                        * uniform(0.75, 1.25)
                        * random_sign(),
                    )
            if ball.rect.centerx > INITIAL_SCREEN_WIDTH:
                left_score += 1
                if len(ball_list) > 1:
                    ball_list.pop(i).kill()
                    continue
                else:
                    ball.set_position(
                        INITIAL_SCREEN_WIDTH / 2, INITIAL_SCREEN_HEIGHT / 2
                    )
                    ball.set_velocity(
                        x_speed=BALL_X_INITIAL_SPEED
                        * uniform(0.75, 1.25)
                        * random_sign(),
                        y_speed=BALL_Y_INITIAL_SPEED
                        * uniform(0.75, 1.25)
                        * random_sign(),
                    )

            # out of bound
            if ball.rect.centery > INITIAL_SCREEN_HEIGHT or ball.rect.centery < 0:
                ball_list.pop(i).kill()
                continue

            # borders
            ball_collision_with_border = ball.rect.collideobjects(border_list)
            if ball_collision_with_border:
                ball_collision_calculation = ball.calculate_collision_with_rect(
                    ball_collision_with_border
                )

            # player
            ball_collision_with_player = ball.rect.collideobjects(player_list)
            if ball_collision_with_player:
                ball_collision_calculation = ball.calculate_collision_with_rect(
                    ball_collision_with_player.rect
                )
                y_offset = ball.rect.centery - player.rect.centery
                ball.y_speed += ((y_offset/500) + (player.speed/3))
                # make ball go brrrr
                ball.increase_speed()

        # ---- RENDER
        time_update_stop = pygame.time.get_ticks()
        time_render_start = pygame.time.get_ticks()
        # redraw background
        screen.fill(BACKGROUD_COLOR)

        # sprites
        for border in border_list:
            pygame.draw.rect(screen, WHITE, border)
        sprite_group.draw(screen)

        for ball in ball_list:
            ball.draw(screen)

        BIG_DEBUG_TEXT = f"{ball.speed_increase_counter}"

        time_render_stop = pygame.time.get_ticks()
        if DEBUG:

            for debug_name, debug_drawing in debug_drawing_list.items():
                debug_drawing[0](*debug_drawing[1])

            update_time = time_update_stop - time_update_start
            render_time = time_render_stop - time_render_start

            debug_lines = [
                f"FPS: {round(game_clock.get_fps())}",
                f"update: {update_time} ms",
                f"update: {render_time} ms",
                f"dt: {dt} ms",
                f"player speed: {player.speed:.4f}",
                f"ball X speed: {ball.x_speed:.4f}",
                f"ball Y speed: {ball.y_speed:.4f}"
            ]

            for i, debug_line_txt in enumerate(debug_lines):
                line_x_position = DEBUG_BOTTOM_LEFT[0]
                line_y_position = DEBUG_BOTTOM_LEFT[1] - DEBUG_LINE_SPACING * i
                line_position = (line_x_position, line_y_position)

                text_object = default_font.render(str(debug_line_txt), False, WHITE)
                screen.blit(text_object, line_position)

            # DEBUG text in the middle of screen
            debug_text_in_center = big_font.render(BIG_DEBUG_TEXT, True, WHITE)
            screen.blit(
                debug_text_in_center,
                (INITIAL_SCREEN_WIDTH // 2, INITIAL_SCREEN_HEIGHT // 2),
            )

        pygame.display.update()


def random_sign():
    return 1 if random() < 0.5 else -1


if __name__ == "__main__":
    main()
