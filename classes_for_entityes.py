from locals import *

import pygame
import math
import random
import ai_geneticNN as aig
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

    def __mul__(self, other):
        x1, y1 = self.get_componenXY()
        x2, y2 = other.get_componenXY()
        scalar = x1 * x2 + y1 * y2
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
    max_energy = 300

    # length_of_sight = 100

    # numb_of_sight_lines = 3
    diff_sight_lines_degrees = 10

    flag2 = 1
    count = 0
    amount_of_entities = 0

    def __init__(self, pos, mapp, ancestor=None):
        super().__init__()
        self.original_img: pygame.Surface = pygame.transform.scale(random.choice(self.TEXTURES),
                                                                   (TILESIZE[0] * 2, TILESIZE[1] * 2))

        self.image = self.original_img.copy()

        self.for_movement_struct = {'vector': Vector2((1, 0)),  # used for movement
                                    'speed': 0,  # used for movement
                                    'pos': list(pos),  # used for positing
                                    }

        self.survival_struct = {'energy': 100,
                                'damage': 10,
                                'attack_speed_modif': 1,
                                'armour_penetration_modif': 1,
                                'enemy_dmg_modif(selfarmour)': 0.9,
                                }
        self.rect: pygame.Rect = self.original_img.get_rect(center=pos)  # used for blitting only
        self.radius = TILESIZE[0]  # used for collision detection

        self.add(mapp.actors, mapp.collideblesgrp)

        self.collidebles_group = mapp.collideblesgrp
        #self.collidebles_group_without_self.remove(self)

        self.mapp = mapp

        self.dmg_anim_counter = self.dmg_anim_counter_default

        # self.ai = aig.Agent()


        self.got_damage = 0

        # print(self.s.shape[1])

        # self.count1 = 0  # for energy difference

        self.flag = 0  # for newborn

        self.is_dead = 0  # dead or not

        if ancestor != None:
            self.agent = ancestor.agent

        Entity.amount_of_entities += 1

        # assert self.numb_of_sight_lines % 2 == 1, 'not even'

    def attack(self):

        a, b = cassettes_of_trgl(self.for_movement_struct['vector'].get_angle(), self.length_of_hands)

        pos_of_AOE = self.for_movement_struct['pos'][0] + a, self.for_movement_struct['pos'][1] + b

        Attack(pos_of_AOE, self.radius_of_AOE, self.mapp, self.survival_struct['damage'])

    def get_damage(self, damage):
        self.got_damage = 1

        self.survival_struct['energy'] -= damage * self.survival_struct['enemy_dmg_modif(selfarmour)']

        if self.survival_struct['energy'] <= 0:
            self.original_img = self.DEAD_TEXTURES[0]
            self.rotate_to_selfangle()
            if self.survival_struct['energy'] < 0:

                self.is_dead = 1

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
        eaten = 0
        for grass_tile in collides:
            eaten += grass_tile.get_eaten(self.FOOD_EATEN_EVERY_TICK)
        self.survival_struct['energy'] += eaten
        if self.survival_struct['energy'] > self.max_energy:
            self.survival_struct['energy'] = self.max_energy

    def collect_environment_state(self):
        data = []

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
        # n = self.numb_of_sight_lines
        grsmp = self.mapp.mpgr
        agntmp = self.mapp.mpagnt

        x, y = self.for_movement_struct['pos']
        blx, bly = int(x // TILESIZE[0]), int(y // TILESIZE[1])
        agntmp[blx][bly] = 2  # pos of self = 2 on map

        # print(grsmp, '\n\n\n\n\n', agntmp)

        '''
        data_dist_to_obstacles = []

        for wall in self.mapp.unwalkabletilesgrp:
            c = wall.rect.center
            # dist = dist_between_points(self.for_movement_struct['pos'], c)
            data_dist_to_obstacles.extend(c)'''  # screw it

        '''
        degrees = degrees_for_sight_lines(data_angle, self.diff_sight_lines_degrees, n)
        #print(degrees)
        for i, deg in enumerate(degrees):  # straightforward
            l = self.length_of_sight
            end = (self.for_movement_struct['pos'][0] + math.cos(math.radians(data_angle)) * l,
                   self.for_movement_struct['pos'][1] + math.sin(math.radians(deg)) * l)
            # print(self.for_movement_struct['pos'], end)
            points = points_on_line(self.for_movement_struct['pos'], end, l // 2)
            # print(points)
            for x, y in points:
                if data_dist_to_obstacles[i]:
                    break
                for coll in self.collidebles_group_without_self:
                    if is_point_in_collideble((x, y), coll):
                        data_dist_to_obstacles[i] = dist_between_points(self.for_movement_struct['pos'], (x, y))
                        break'''  # angles

        '''
        sight_line_eq=str(math.tan(math.radians(data_angle)))+'*x'+str(self.for_movement_struct['pos'][1])
        for coll in self.mapp.collideblesgrp:
            find_intersection_line_coll(sight_line_eq,coll)
            1/0'''  # math

        # finish
        data.extend(self.for_movement_struct['pos'])
        #data.append(data_food)
        data.append(data_angle)

        data = np.array(data)
        # print(data,'data')

        data.resize(grsmp.shape)
        # print(data,'data2')

        stacked = np.stack((grsmp, agntmp, data), axis=2)

        # stacked=stacked.reshape(1, *stacked.shape)

        stacked = stacked.flatten()
        stacked = stacked.reshape(1, stacked.shape[0])

        return stacked

    def replay_agent(self):

        v=Entity.amount_of_entities if Entity.amount_of_entities!=0 else 1

        if Entity.count / v > 500:
            self.agent.replay(32)
            Entity.count = 0
        Entity.count += 1

    def update(self):
        # print(self.survival_struct['hp'])
        # self.get_damage_animation()
        if self.flag == 0:
            self.s = self.collect_environment_state()
            # print(self.s.shape)
            if not hasattr(self, 'agent'):
                self.agent = aig.Agent(self.s.shape)
            self.flag = 1

        a = self.agent.act(self.s)
        next_s, r = self.do_action(a)
        self.agent.memorize(self.s, a, r, next_s)
        self.s = next_s

        self.collide()

        self.rotate_to_selfangle()

        self.get_damage(0.1)

        self.replay_agent()

    def do_action(self, action):
        # print(self.for_movement_struct['speed'])
        # print(action)
        reward = 0.1
        action = action_choices[action]
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
        elif action == STAY:
            pass
        elif action == BREED:
            reward = self.breed()
        else:
            pass

        if self.is_dead:
            self.kill()
            Entity.amount_of_entities -= 1
            reward = -1

        next_state = self.collect_environment_state()

        return next_state, reward

    def collide(self):
        self.for_movement_struct['speed'] *= self.SPEED_DECAY

        currposrect = self.rect.copy()
        newpos = self.calc_next_pos()

        # check x axis
        self.rect.centerx = newpos[0]


        collidebles_group_without_self:pygame.sprite.Group=self.collidebles_group.copy()
        collidebles_group_without_self.remove(self)

        collided = pygame.sprite.spritecollide(self, collidebles_group_without_self, False,
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

        collided = pygame.sprite.spritecollide(self, collidebles_group_without_self, False,
                                               collide_circleNrect)

        collidebles_group_without_self.empty()
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

    def breed(self):
        if self.survival_struct['energy'] > self.max_energy * 0.9:
            a, b = cassettes_of_trgl(self.for_movement_struct['vector'].get_angle(), self.radius * 2.3)

            pos = self.for_movement_struct['pos'][0] + a, self.for_movement_struct['pos'][1] + b
            test_if_fits = pygame.sprite.Sprite
            test_if_fits.radius, test_if_fits.rect = self.radius, self.original_img.get_rect(center=pos)
            collided = pygame.sprite.spritecollide(test_if_fits, self.mapp.get_collidebles(), False,
                                                   pygame.sprite.collide_circle)
            if not collided:
                Entity(pos, self.mapp, self)

                self.survival_struct['energy'] = self.max_energy * 0.3
                return 1  # reward
            else:
                # print('NO')
                pass
        return 0.1  # bcos alive
