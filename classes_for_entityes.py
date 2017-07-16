from locals import *

import pygame
import math
import random
#import ai_geneticNN as aig
import numpy as np
from classMap import *


def collide_circleNrect(spriteCircle, spriteRect):
    '''
    {COPYPASTE EDITION}
    callback function for intersection detection of Wall's and Entity's
    '''
    r = spriteCircle.radius
    center = spriteCircle.rect.center

    rect = spriteRect.rect

    circle_distance_x = abs(center[0] - rect.centerx)
    circle_distance_y = abs(center[1] - rect.centery)
    if circle_distance_x > rect.w / 2.0 + r or circle_distance_y > rect.h / 2.0 + r:
        return False
    if circle_distance_x <= rect.w / 2.0 or circle_distance_y <= rect.h / 2.0:
        return True
    corner_x = circle_distance_x - rect.w / 2.0
    corner_y = circle_distance_y - rect.h / 2.0
    corner_distance_sq = corner_x ** 2.0 + corner_y ** 2.0
    return corner_distance_sq <= r ** 2.0


class Vector2(object):
    def __init__(self, xy: tuple, angle=None):
        self.xy = xy

        self.angle_rad = math.atan2(self.xy[1], self.xy[0])

        self.length = self.get_length()

        self.normalize()

    def __str__(self):
        return str(math.degrees(self.angle_rad)) + ' |||| ' + str(self.xy)

    def __add__(self, other):
        return self.__thisVectorPlusAnotherVector(other)
    def __mul__(self,other):
        x1,y1=self.get_componenXY()
        x2,y2=other.get_componenXY()
        scalar=x1*x2+y1*y2
        return scalar

    def get_componenXY(self):
        return (self.xy[0], self.xy[1])

    def get_length(self):
        x, y = self.get_componenXY()
        length = math.sqrt(x ** 2 + y ** 2)
        return length

    def get_angle(self):
        return math.degrees(self.angle_rad)

    def change_components_to(self, xy):
        self.xy = xy

        self.angle_rad = math.atan2(xy[1], xy[0])
        self.length = self.get_length()

    def change_angle_by(self, angle_indeg):
        angle = math.radians(angle_indeg)
        self.angle_rad += angle

        self.change_components_to((math.cos(self.angle_rad), math.sin(self.angle_rad)))

    def normalize(self):
        x, y = self.xy
        length = self.length
        if length != 0:
            normx, normy = x / length, y / length
            self.change_components_to((normx, normy))

    def __thisVectorPlusAnotherVector(self, vect):
        # convert to radians
        selfAngle = math.radians(self.angle_rad)
        vectAngle = math.radians(vect.angle)
        # first vector's components
        x = math.cos(selfAngle) * self.length
        y = math.sin(selfAngle) * self.length
        # second vector's components
        x1 = math.cos(vectAngle) * vect.value
        y1 = math.sin(vectAngle) * vect.value
        # sum
        xx = x + x1
        yy = y + y1
        '''
        # calculate angle and value
        angle = math.atan2(yy, xx)
        value = math.hypot(xx, yy)
        # convert to degrees
        angle = math.degrees(angle)'''
        return Vector2((xx, yy))


class Attack(pygame.sprite.Sprite):
    IMAGES = []
    FRAMES_LIVES_DEFAULT = 6

    def __init__(self, pos, radius, mapp, dmg):
        super().__init__()
        self.image = self.IMAGES[0]
        self.rect = self.image.get_rect(center=pos)
        self.radius = radius
        self.frames_left = self.FRAMES_LIVES_DEFAULT
        self.damage_dealed = 0
        self.dmg = dmg

        self.mapp = mapp
        self.add(self.mapp.attacks)

    def animate(self):
        self.frames_left -= 1

        self.image = self.IMAGES[self.frames_left % 2]
        if self.frames_left <= 0:
            self.kill()

    def deal_damage(self):
        self.damage_dealed = 1
        collided = pygame.sprite.spritecollide(self, self.mapp.actors, False, pygame.sprite.collide_circle)
        for actor in collided:
            actor.get_damage(self.dmg)


class Entity(pygame.sprite.Sprite):
    TEXTURES = []
    GET_DAMAGE_ANIMATION = []
    DEAD_TEXTURES = []
    SPEED_BOOST = 6
    SPEED_DECAY = 0.8
    length_of_hands = TILESIZE[0] + 16
    radius_of_AOE = 4
    dmg_anim_counter_default = 6

    CHANGE_ANGLE_STEP = 15

    FOOD_EATEN_EVERY_TICK = 1

    length_of_sight=100

    def __init__(self, pos, mapp, nn_parameters=None):
        super().__init__()
        self.original_img: pygame.Surface = pygame.transform.scale(random.choice(self.TEXTURES),
                                                                   (TILESIZE[0] * 2, TILESIZE[1] * 2))

        self.image = self.original_img.copy()

        self.for_movement_struct = {'vector': Vector2((1, 0)),  # used for movement
                                    'speed': 0,  # used for movement
                                    'pos': list(pos),  # used for positing
                                    }

        self.survival_struct = {'hp': 100,
                                'damage': 10,
                                'attack_speed_modif': 1,
                                'armour_penetration_modif': 1,
                                'enemy_dmg_modif(selfarmour)': 0.9,
                                }
        self.rect: pygame.Rect = self.original_img.get_rect(center=pos)  # used for blitting only
        self.radius = TILESIZE[0]  # used for collision detection

        self.add(mapp.actors, mapp.collideblesgrp)

        self.collidebles_group_without_self = mapp.collideblesgrp.copy()
        self.collidebles_group_without_self.remove(self)

        self.mapp = mapp

        self.dmg_anim_counter = self.dmg_anim_counter_default

        self.ai = aig.Nn_ai(nn_parameters)
        # self.h = aig.Human(self)

        self.got_damage = 0

    def attack(self):

        def cassettes_of_trgl(angle, hypotenuse):
            angle = angle  # WTf?

            cass_nearest = math.cos(math.radians(angle)) * hypotenuse
            cass_farest = math.sin(math.radians(angle)) * hypotenuse
            return cass_nearest, cass_farest

        a, b = cassettes_of_trgl(self.for_movement_struct['vector'].get_angle(), self.length_of_hands)

        pos_of_AOE = self.for_movement_struct['pos'][0] + a, self.for_movement_struct['pos'][1] + b

        Attack(pos_of_AOE, self.radius_of_AOE, self.mapp, self.survival_struct['damage'])

    def get_damage(self, damage):
        self.got_damage = 1

        self.survival_struct['hp'] -= damage * self.survival_struct['enemy_dmg_modif(selfarmour)']

        if self.survival_struct['hp'] <= 0:
            self.original_img = self.DEAD_TEXTURES[0]
            self.rotate_to_selfangle()

    def get_damage_animation(self):
        # TODO: make it work
        if self.got_damage:
            self.original_img = self.GET_DAMAGE_ANIMATION[self.dmg_anim_counter % 2]
            self.dmg_anim_counter -= 1
            if self.dmg_anim_counter <= 0:
                self.dmg_anim_counter = self.dmg_anim_counter_default

    def die(self):
        # TODO: does not work
        self.original_img = pygame.transform.scale(random.choice(self.TEXTURES), (TILESIZE[0] * 2, TILESIZE[1] * 2))

    def rotate_to_selfangle(self):
        pos = self.for_movement_struct['pos']

        img = pygame.transform.rotate(self.original_img, -self.for_movement_struct['vector'].get_angle() - 90)
        self.image = img
        # self.image = pygame.transform.scale(img, (TILESIZE[0] * 2, TILESIZE[1] * 2))

        self.rect = img.get_rect()
        self.rect.center = pos

        # print('1',self.rect.topleft, self.rect.center, self.rect.bottomright)

    def eat(self):
        grass = self.mapp.get_grassgrp()
        collides = pygame.sprite.spritecollide(self, grass, False,
                                               collide_circleNrect)
        for grass_tile in collides:
            grass_tile.get_eaten(self.FOOD_EATEN_EVERY_TICK)

    def collect_environment_state(self):
        data = np.empty((1, 5))

        # amount of food available
        data_food = 0
        grass = self.mapp.get_grassgrp()
        collides = pygame.sprite.spritecollide(self, grass, False,
                                               pygame.sprite.collide_circle)
        for grass_tile in collides:
            data_food += grass_tile.food_amount

        # angle of self
        data_angle = self.for_movement_struct['vector'].get_angle()

        # obstacles
        l=self.length_of_sight# straightforward
        end=(math.cos(math.radians(data_angle))*l,math.sin(math.radians(data_angle))*l)
        points=get_points_on_line(self.for_movement_struct['pos'],end,l)

        for point in points:
            c=self.collidebles_group_without_self


        '''
        sight_line_eq=str(math.tan(math.radians(data_angle)))+'*x'+str(self.for_movement_struct['pos'][1])
        for coll in self.mapp.collideblesgrp:
            find_intersection_line_coll(sight_line_eq,coll)
            1/0'''#math


    def update(self):
        # print(self.survival_struct['hp'])
        # self.get_damage_animation()

        action = self.ai.decide(action_choices)
        self.do_action(action)

        self.collide()

        self.rotate_to_selfangle()

    def do_action(self, action):
        # print(self.for_movement_struct['speed'])
        # print(action)
        if action == ATTACK:
            self.attack()
        elif action == K_UP:
            self.for_movement_struct['speed'] = self.SPEED_BOOST

        elif action == K_LEFT:
            self.for_movement_struct['vector'].change_angle_by(-self.CHANGE_ANGLE_STEP)
        elif action == K_RIGHT:
            self.for_movement_struct['vector'].change_angle_by(self.CHANGE_ANGLE_STEP)
        elif action == EAT:
            self.eat()
        else:
            pass

    def collide(self):
        self.for_movement_struct['speed'] *= self.SPEED_DECAY

        currposrect = self.rect.copy()
        newpos = self.calc_next_pos()

        # check x axis
        self.rect.centerx = newpos[0]

        collided = pygame.sprite.spritecollide(self, self.collidebles_group_without_self, False,
                                               collide_circleNrect)
        # print(collided,'x')

        if collided:
            self.rect = currposrect
        else:
            # self.rect = rect
            self.for_movement_struct['pos'][0] = newpos[0]

        currposrect = self.rect.copy()

        # check y axis
        self.rect.centery = newpos[1]

        collided = pygame.sprite.spritecollide(self, self.collidebles_group_without_self, False,
                                               collide_circleNrect)
        # print(collided,'y')
        if collided:
            self.rect = currposrect
        else:
            # self.rect = rect
            self.for_movement_struct['pos'][1] = newpos[1]

    def calc_next_pos(self):
        dx, dy = self.for_movement_struct['vector'].get_componenXY()

        sp = self.for_movement_struct['speed']
        dx *= sp
        dy *= sp

        pos = self.for_movement_struct['pos']
        newposx, newposy = pos[0] + dx, pos[1] + dy

        newrectx = pygame.Rect(0, 0, TILESIZE[0] * 2, TILESIZE[1] * 2)
        newrecty = pygame.Rect(0, 0, TILESIZE[0] * 2, TILESIZE[1] * 2)

        newrectx.center = newposx, pos[1]
        newrecty.center = newposy, pos[1]

        return (newposx, newposy)

    @staticmethod
    def breed(mom, dad):
        # TODO: breed
        pass
