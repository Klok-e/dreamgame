from locals import *
from  classes_for_entityes import Entity

import random
import pygame
import math


class Camera():
    CAMERA_STEP = 20

    def __init__(self, startpos=(0, 0)):
        self.pos = (startpos[0], startpos[1])
        self.movingx = 0
        self.movingy = 0

    def move(self):
        self.pos = (self.pos[0] - self.movingx, self.pos[1] - self.movingy)

    def get_plgrsurf_pos(self):
        return (self.pos[0], self.pos[1])

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.movingy = -self.CAMERA_STEP
            if event.key == pygame.K_DOWN:
                self.movingy = self.CAMERA_STEP
            if event.key == pygame.K_LEFT:
                self.movingx = -self.CAMERA_STEP
            if event.key == pygame.K_RIGHT:
                self.movingx = self.CAMERA_STEP
        if event.type == pygame.KEYUP:
            self.movingy, self.movingx = 0, 0


class Wall(pygame.sprite.Sprite):
    TEXTURES = []

    def __init__(self, pos):
        super().__init__()

        self.image = pygame.transform.scale(random.choice(self.TEXTURES), TILESIZE)
        self.rect: pygame.Rect = self.image.get_rect(topleft=pos)
        # self.radius = TILESIZE[0] // 2



        self.line_equations = []

        # bottom line
        point1 = self.rect.bottomleft[0] + 1, self.rect.bottomleft[0] - 1
        point2 = self.rect.bottomright[0] - 1, self.rect.bottomright[1] - 1

        e = line_eq(point1, point2)
        # print(e)
        self.line_equations.append(e)

        # top line
        point1 = self.rect.topleft[0] + 1, self.rect.topleft[1] + 1
        point2 = self.rect.topright[0] - 1, self.rect.topright[1] + 1

        e = line_eq(point1, point2)
        self.line_equations.append(e)

        # left line
        e = self.rect.left + 1
        self.line_equations.append(e)

        # right line
        e = self.rect.right - 1
        self.line_equations.append(e)

        assert isinstance(e, int), 'wtf r u doin'

    def get_lines(self):
        return self.line_equations


class Grass(pygame.sprite.Sprite):
    COLORS = [(214, 225, 34), (124, 252, 0), (0, 255, 0), (50, 205, 50), (0, 128, 0), (0, 100, 0)]
    FOOD_RECOVERY = 1
    FOOD_MAX = 180

    def __init__(self, pos, mapp):
        super().__init__()
        self.color = None
        self.image = pygame.Surface(TILESIZE)

        self.rect = self.image.get_rect(topleft=pos)
        # self.radius = TILESIZE[0] // 2
        self.add(mapp.grass_tiles)

        self.food_amount = 31

    def set_colour(self):
        f = self.food_amount
        if f <= 5:
            self.image.fill(BLACK)
        else:
            for i in range(1, len(self.COLORS) + 1):
                if f <= (self.FOOD_MAX // len(self.COLORS)) * i:
                    self.image.fill(self.COLORS[i - 1])
                    break

    def get_eaten(self, amount):
        self.food_amount -= amount
        if self.food_amount < 0:
            self.food_amount = 0
            amount = 0
        self.set_colour()
        return amount

    def update(self):
        self.food_amount += self.FOOD_RECOVERY
        self.set_colour()

    def get_food(self):
        return self.food_amount


class Mapg():
    MAPCOLOUR = GREEN
    UPDATE_GRASS_EVERYframes = 1000

    def __init__(self):
        self.arena = None
        self.unwalkabletilesgrp = pygame.sprite.Group()
        self.actors = pygame.sprite.Group()
        # self.actors = pygame.sprite.GroupSingle()
        self.collideblesgrp = pygame.sprite.Group()
        self.attacks = pygame.sprite.Group()
        self.grass_tiles = pygame.sprite.Group()

        self.__set_map()
        self.set_actors()

        self.mpgr = self.get_mapofgrass()
        self.mpagnt = self.get_mapofagents()

        self.count = self.UPDATE_GRASS_EVERYframes

    def get_mapofgrass(self):  # input to NN
        mp = np.zeros((MAPSIZE[1], MAPSIZE[0]))
        for grs in self.grass_tiles:
            x, y = grs.rect.center
            blx, bly = x // TILESIZE[0], y // TILESIZE[1]
            mp[bly][blx] = 1 if grs.get_food() > 30 else 0
        # print(mp,'\n',mp.shape)
        return mp

    def get_mapofagents(self):  # input to NN
        mp = np.zeros((MAPSIZE[1], MAPSIZE[0]))
        for actor in self.actors:
            x, y = actor.for_movement_struct['pos']
            blx, bly = int(x // TILESIZE[0]), int(y // TILESIZE[1])
            # print(blx,bly)
            mp[bly][blx] = 1.
        # print(mp,'\n',mp.shape)
        return mp

    def set_actors(self):
        self.actors.add(Entity((100, 100), self))

    def __set_map(self):
        self.arena: pygame.Surface = pygame.Surface((MAPSIZE[0] * TILESIZE[0], MAPSIZE[1] * TILESIZE[1]))
        self.__set_unwalkable_onthe_edges()
        self._set_grass()

    def draw_everything(self):
        self.arena.fill(self.MAPCOLOUR)
        self.grass_tiles.draw(self.arena)
        self.unwalkabletilesgrp.draw(self.arena)

        self.actors.draw(self.arena)

        self.attacks.draw(self.arena)

    def update_everything(self):
        self.mpgr = self.get_mapofgrass()
        self.mpagnt = self.get_mapofagents()

        self.actors.update()

        # grass grows every ... frames
        self.count += 1
        if self.count >= self.UPDATE_GRASS_EVERYframes:
            self.grass_tiles.update()
            self.count = 0

    def animate_attacks(self):
        for attack in self.attacks:
            attack.animate()

    def attacks_do_damage(self):
        for attack in self.attacks:
            if attack.damage_dealed == False:
                attack.deal_damage()

    def __set_unwalkable_onthe_edges(self):
        for i in range(MAPSIZE[0]):
            pixpos = self.block_to_pix_coords((i, 0))
            a = Wall(pixpos)

            pixpos = self.block_to_pix_coords((i, MAPSIZE[1] - 1))
            b = Wall(pixpos)

            a.add(self.unwalkabletilesgrp, self.collideblesgrp)
            b.add(self.unwalkabletilesgrp, self.collideblesgrp)

        for i in range(1, MAPSIZE[1] - 1):
            pixpos = self.block_to_pix_coords((0, i))
            a = Wall(pixpos)

            pixpos = self.block_to_pix_coords((MAPSIZE[0] - 1, i))
            b = Wall(pixpos)

            a.add(self.unwalkabletilesgrp, self.collideblesgrp)
            b.add(self.unwalkabletilesgrp, self.collideblesgrp)

    def _set_grass(self):
        for y in range(1, MAPSIZE[1]):
            for x in range(1, MAPSIZE[0]):
                pixpos = self.block_to_pix_coords((x, y))
                Grass(pixpos, self)

    def __draw_tile_lines_toself(self):
        for i in range(1, MAPSIZE[0]):
            pygame.draw.line(self.arena, BLACK, (i * TILESIZE[0] - 1, 0),
                             (i * TILESIZE[0] - 1, TILESIZE[1] * MAPSIZE[1] - 1))

        for i in range(1, MAPSIZE[1]):
            pygame.draw.line(self.arena, BLACK, (0, i * TILESIZE[1] - 1),
                             (TILESIZE[0] * MAPSIZE[0] - 1, i * TILESIZE[1] - 1))

    def get_arena(self):
        return self.arena

    def get_collidebles(self):
        return self.collideblesgrp

    def get_grassgrp(self):
        return self.grass_tiles

    def block_to_pix_coords(self, xy: tuple):
        x = xy[0] * TILESIZE[0]
        y = xy[1] * TILESIZE[1]
        return (x, y)

    def pix_to_block_coords(self, xy: tuple, camera: Camera):
        arenaxy = camera.get_plgrsurf_pos()

        relxy = (xy[0] - arenaxy[0], xy[1] - arenaxy[1])

        mapmax = (TILESIZE[0] * MAPSIZE[0], TILESIZE[1] * MAPSIZE[1])

        if (relxy[0] < 0 or relxy[1] < 0) or (relxy[0] > mapmax[0] or relxy[1] > mapmax[1]):
            return None
        else:
            x = relxy[0] // TILESIZE[0]
            y = relxy[1] // TILESIZE[1]
            return (x, y)
