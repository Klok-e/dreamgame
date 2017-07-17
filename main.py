from classMap import *
from classes_for_entityes import *


def load_all_the_images():
    Entity.TEXTURES = [load_image('actor.bmp')]
    Entity.DEAD_TEXTURES = [load_image('actor_dead.bmp')]
    Entity.GET_DAMAGE_ANIMATION = [load_image('actor.bmp'), load_image('actor_damaged.bmp')]

    Wall.TEXTURES = [load_image('wall.bmp')]
    img = pygame.transform.scale(load_image('attack.gif'),
                                 (round(Entity.radius_of_AOE * 1.4),
                                  round(Entity.radius_of_AOE * 1.4)))
    Attack.IMAGES = [img, pygame.transform.flip(img, 1, 1)]


def main():
    # initialization
    pygame.init()
    display_surf = pygame.display.set_mode(SCREENRECT.size)

    # images
    load_all_the_images()

    # clock
    timer = pygame.time.Clock()

    # camera
    camera = Camera()

    # font for displaying text
    textobj = pygame.font.Font(None, 50)

    # the map
    map1 = Mapg()

    def physics_step():
        # move the camera
        camera.move()

        # update
        map1.update_everything()

        # deal damage by attacks
        map1.attacks_do_damage()

    def drawing_step():

        # draw things
        map1.draw_everything()

        # attacks
        map1.animate_attacks()

        # draw an arena
        display_surf.fill(DARKGREEN)
        display_surf.blit(map1.get_arena(), camera.get_plgrsurf_pos())

        # mouse at the current block
        blockmouse_at = map1.pix_to_block_coords(mouse_pos, camera)
        display_surf.blit(textobj.render(str(blockmouse_at), True, ORANGE), (10, 10))

        # update the screen
        pygame.display.update(SCREENRECT)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return

            camera.handle_input(event)

            map1.actors.sprite.h.save_event(event)
            # playergrp.sprite.do_action(event)

        mouse_pos = pygame.mouse.get_pos()
        drawing_step()
        physics_step()

        timer.tick(FPS)


if __name__ == '__main__':
    main()
