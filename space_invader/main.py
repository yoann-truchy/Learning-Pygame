#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from random import choice, random

import pygame

from Envahisseurs import *
from Tirs import *
from Vaisseau import *

# listes des collisions
list_alien = list()
list_tirs_alien = list()
list_tirs_allie = list()
borders = list()


def main():
    # Initialisation de la librairie et de quelques paramètres
    pygame.init()
    size = width, height = 850, 600
    black = 0, 0, 0
    pygame.key.set_repeat(1, 100)
    screen = pygame.display.set_mode(size)
    debug = False
    hitboxes = False
    score = 0
    # elements de texte
    print(pygame.font.get_default_font())
    font = pygame.font.SysFont("freesansbold", 25)
    sh_debug = font.render("d = Debug mode", False, (75, 75, 75))
    sh_special = font.render("haut = spécial", False, (75, 75, 75))
    sh_hitbox = font.render("h = show hitbox", False, (75, 75, 75))

    # Titre
    pygame.display.set_caption(" Game Invaders ")

    # Chargement et collage du fond
    fond = pygame.image.load(
        os.path.join(os.path.dirname(__file__), "Images/fond.jpg")
    ).convert()
    fond = pygame.transform.scale(fond, size)
    screen.blit(fond, (0, 0))
    groupe_vaisseau = pygame.sprite.Group()
    groupe_missile = pygame.sprite.Group()
    groupe_aliens = pygame.sprite.Group()

    # création hitbox pour la création aliens et leurs déplacements
    hitbox = pygame.draw.rect(fond, (0, 0, 0), [-1, -1, 802, 40], 1)
    border1 = pygame.draw.line(fond, (0, 0, 0), (-1, 0), (-1, 432), 2)
    border2 = pygame.draw.line(fond, (0, 0, 0), (800, 0), (800, 432), 4)
    borders.append(border1)
    borders.append(border2)

    # Creation et mise en place d'un vaisseau : a vous de completer...
    ship = vaisseau()
    groupe_vaisseau.add(ship)

    # fonction de creation d'alien
    def spawn_alien():
        for i in range(2, 13):
            list_alien.append(alien(0, i))
        for y in list_alien:
            groupe_aliens.add(y)

    spawn_alien()

    # alien hors ecran pour eviter d'avoir une liste vide
    trash = alien(-20, -100)
    list_alien.append(trash)
    groupe_aliens.add(trash)

    # Boucle principale : action !
    clock = pygame.time.Clock()
    while 1:
        clock.tick(20)

        t_score = font.render("score: " + str(score), False, (75, 75, 75))

        # debug
        print(len(list_tirs_allie))

        # tir d'alien
        choix_alien = choice(list_alien)
        if random() <= 0.1:
            ma = missile(2, choix_alien.rect.centerx, choix_alien.rect.top, 20)
            groupe_missile.add(ma)
            list_tirs_alien.append(ma)

        # création alien
        if hitbox.collidelist(list_alien) == -1:
            spawn_alien()

        # deplacement aliens
        for ali in list_alien:
            # print (ali.vitesse_x)
            # print (ali.rect.collidelist(borders))
            if ali.rect.collidelist(borders) != -1:
                ali.vitesse_x = -ali.vitesse_x

        # detection des tirn enemy
        if ship.rect.collidelist(list_tirs_alien) >= 0:
            pygame.sprite.Sprite.kill(
                list_tirs_alien[ship.rect.collidelist(list_tirs_alien)]
            )
            list_tirs_alien[ship.rect.collidelist(list_tirs_alien)].rect.center = (0, 0)
            ship.take_damage()

        # detection tir allier sur alien
        for tir_allie in list_tirs_allie:

            if tir_allie.rect.collidelist(list_alien) >= 0:

                ali = list_alien[tir_allie.rect.collidelist(list_alien)]
                ali.take_damage(50)
                if ali.PV <= 50:  # pv de l'alien a 50 ou en dessous
                    ali.image = pygame.image.load(os.path.join(os.path.dirname(__file__),"Images/alien2_degat.png"))
                    score += 6
                if ali.PV <= 0:  # mort de l'alien
                    pygame.sprite.Sprite.kill(ali)
                    ali.rect.center = (100000, -1000000)
                    list_alien.remove(ali)
                    score += 13

                tir_allie.rect.center = (10000, 10000)
                list_tirs_allie.remove(tir_allie)
                pygame.sprite.Sprite.kill(tir_allie)
                if ship.ulti < 100:
                    ship.ulti += 10

        # Détection d'un événement (clic souris ou appui touche clavier) :
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:  # c'est un clic souris
                print("Clic souris detecte ...")

            elif event.type == pygame.KEYDOWN:  # C'est une touche clavier
                if event.key == pygame.K_ESCAPE:
                    sys.exit()  # Sortie du jeu
                if event.key == pygame.K_d:  # Permet de passer en mode debug
                    if debug:
                        debug = False
                    else:
                        debug = True
                if event.key == pygame.K_h:  # Permet d'afficher les hitbox
                    if hitboxes:
                        hitboxes = False
                    else:
                        hitboxes = True
                if event.key == pygame.K_UP:
                    if ship.tir:
                        ship.tir = False
                    else:
                        ship.tir = True
                if event.key == pygame.K_SPACE:
                    tir = missile(1, ship.rect.centerx, ship.rect.top, -20)
                    list_tirs_allie.append(tir)
                    groupe_missile.add(tir)

        # deplacement du vaisseau en continu
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            ship.aller_a_gauche(10)
        if keys[pygame.K_RIGHT]:
            ship.aller_a_droite(10)

        # capacité spéciale
        if ship.ulti > 0 and ship.tir:
            tir = missile(1, ship.rect.centerx, ship.rect.top, -20)
            list_tirs_allie.append(tir)
            groupe_missile.add(tir)
            ship.ulti -= 20
            if ship.ulti <= 0:
                ship.ulti = 0
                ship.tir = False

        # Effacement de l'ancienne image
        screen.blit(fond, (0, 0))

        # Mise à jour des éléments du jeu : à vous de compléter

        groupe_vaisseau.update()
        groupe_vaisseau.draw(screen)
        groupe_missile.update()
        groupe_missile.draw(screen)
        groupe_aliens.update()
        groupe_aliens.draw(screen)

        # barre de vie du joueur
        # rouge
        pygame.draw.line(screen, (255, 0, 0), (825, 550), (825, 50), 20)
        pygame.draw.polygon(screen, (255, 0, 0), [(816, 50), (825, 40), (835, 50)])

        # vert
        pygame.draw.line(
            screen, (0, 255, 0), (825, 550), (825, (-5 * ship.pv + 550)), 20
        )
        pygame.draw.polygon(screen, (0, 255, 0), [(816, 550), (825, 560), (835, 550)])
        if ship.pv == 100:
            pygame.draw.polygon(screen, (0, 255, 0), [(816, 50), (825, 40), (835, 50)])

        # bare de super
        # vide
        pygame.draw.line(
            screen,
            (30, 30, 30),
            (ship.rect.bottomleft[0], ship.rect.bottomleft[1] + 10),
            (ship.rect.bottomright[0], ship.rect.bottomright[1] + 10),
            3,
        )
        # remplie
        pygame.draw.line(
            screen,
            (30, 30, 255),
            (ship.rect.bottomleft[0], ship.rect.bottomleft[1] + 10),
            (
                ship.rect.bottomleft[0] + ship.ulti,
                ship.rect.bottomright[1] + 10,
            ),
            3,
        )

        # Show hitboxes
        if hitboxes:
            for ali in list_alien:
                pygame.draw.rect(screen, (150, 0, 0), (ali.rect), 2)
                pygame.draw.line(
                    screen,
                    (150, 0, 0),
                    ali.rect.topleft,
                    ali.rect.bottomright,
                    2,
                )
                pygame.draw.line(
                    screen,
                    (150, 0, 0),
                    ali.rect.topright,
                    ali.rect.bottomleft,
                    2,
                )
                pygame.draw.line(
                    screen,
                    (150, 0, 0),
                    ali.rect.topright,
                    ali.rect.bottomleft,
                    2,
                )

            for tir in groupe_missile:
                pygame.draw.rect(screen, (255, 0, 0), (tir.rect), 2)
                pygame.draw.line(
                    screen,
                    (150, 0, 0),
                    tir.rect.topleft,
                    tir.rect.bottomright,
                    2,
                )
                pygame.draw.line(
                    screen,
                    (150, 0, 0),
                    tir.rect.topright,
                    tir.rect.bottomleft,
                    2,
                )

            pygame.draw.rect(screen, (255, 0, 0), (ship.rect), 2)
            pygame.draw.line(
                screen,
                (150, 0, 0),
                ship.rect.topleft,
                ship.rect.bottomright,
                2,
            )
            pygame.draw.line(
                screen,
                (150, 0, 0),
                ship.rect.topright,
                ship.rect.bottomleft,
                2,
            )

        # Debug mode:
        if debug:
            for ali in list_alien:
                pygame.draw.line(
                    screen,
                    (255, 0, 0),
                    (ali.rect.topleft[0], ali.rect.topleft[1] - 10),
                    (ali.rect.topright[0], ali.rect.topright[1] - 10),
                    3,
                )
                pygame.draw.line(
                    screen,
                    (0, 255, 0),
                    (ali.rect.topleft[0], ali.rect.topleft[1] - 10),
                    (ali.rect.topleft[0] + ali.PV, ali.rect.topright[1] - 10),
                    3,
                )

            # pv et super infinis
            ship.pv = 100
            ship.ulti = 100
            pygame.draw.line(screen, (0, 0, 150), (825, 550), (825, 50), 20)
            pygame.draw.polygon(screen, (0, 0, 150), [(816, 50), (825, 40), (835, 50)])
            pygame.draw.polygon(
                screen, (0, 0, 150), [(816, 550), (825, 560), (835, 550)]
            )

        # elements de texte
        screen.blit(sh_debug, (15, 500))
        screen.blit(sh_hitbox, (15, 520))
        screen.blit(sh_special, (15, 540))
        screen.blit(t_score, (700, 575))

        # Actualisation de l'écran
        pygame.display.flip()

    print(score)


if __name__ == "__main__":
    main()
