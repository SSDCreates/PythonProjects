import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join

pygame.init()

pygame.display.set_caption('Platformer')  # sets cation at top of window

# global variables
WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5  # player velociy ( how fast player moves around screen)

window = pygame.display.set_mode((WIDTH, HEIGHT))

# sprites


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False)for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    #  load every file inside of the directory
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}  # key will be animation style, value is images in animation

    for image in images:
        # allows loading of transparent background iamge
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            # passes width of image
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            # create rectangle to tell us where we want to take an image from and blit it onto surface
            rect = pygame.Rect(i * width, 0, width, height)
            # draws sprite sheet at 0,0, according to diameter of rect
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        # sprite directions
        if direction:
            # replaces the sprite .png to _right to name
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites
    return all_sprites


def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    # creates image at size dimensioned to the block
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    # 96 denotes the start of the sprite to use on the x and 0 is the y axis of the sprite start at top-left corner
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)  # Draws image on surface
    return pygame.transform.scale2x(surface)  # returns scaled image

# player


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets('MainCharacters', 'VirtualGuy', 32, 32, True)
    ANIMATION_DELAY = 3

    # pygame sprite makes it easier to detect collision

    def __init__(self, x, y, width, height):
        super().__init__()
        # define rectange to surroudn player
        self.rect = pygame.Rect(x, y, width, height)

        # velocity denotes how fast the player moves in every frame in both directions
        self.x_vel = 0
        self.y_vel = 0
        # set mask
        self.mask = None
        # set default direction for character to face
        self.direction = 'left'
        # resets animation count
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
    
    def make_hit(self):
        self.hit = True
        self.hit_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 8  # multiply by speed of jump
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0  # resets gravity on jump for first jump

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != 'left':
            self.direction = 'left'
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != 'right':
            self.direction = 'right'
            self.animation_count = 0

    def loop(self, fps):
        # calls once every frame (1 iteration of while loop)
        # update gravity
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        # updates animation
        self.move(self.x_vel, self.y_vel)
        # update mask

        self.fall_count += 1
        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0
        self.update_sprite()

    def landed(self):
        # reset fall count
        self.fall_count = 0
        self.y_vel = 0  # reset y movement
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"  # default sprite sheet
        if self.hit:
            sprite_sheet = "hit"
        if self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"

        if self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        # every five frames use a different sprite for the appropriate animation
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    # update rect on sprite to match sprite
    def update(self):
        # constantly adjust width and height of rectange to match the sprite
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        # mask is a mapping of the pixels that exist in the sprite
        # tells us where there's actual pixels and matches pixel perfect collision ex: collision occurs at pixels and not rectangle
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        # every five frames use a different sprite for the appropriate animation
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.update()
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            # ensures animation count is not too large
            # will mess up double jump on player
            self.animation_count = 0


def get_background(name):
    # create grid of background tiles
    image = pygame.image.load(join('assets', 'Background', name))
    _, _, width, height = image.get_rect()  # gets width and height for image
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            # tells us how many tiles we need
            # denotes position of top left corner of current tile pygames draws from topleft corner
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    # draw blocks
    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            # handle collision by direction
            if dy > 0:
                # if falling down, you move to the top of the collision item
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom  # if moving up, make top = bottom
                player.hit_head()
            collided_objects.append(obj)
    return collided_objects

# check if horizontal collision


def collide(player, objects, dx):
    # checks if player were to move in a direction if they would hit a block (l or r)
    player.move(dx, 0)
    player.update()  # updates mask to check for collision

    collided_object = None

    for obj in objects:
        # if a collision would occur
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj  # logging object
            break
    player.move(-dx, 0)  # move player back
    player.update()  # update location
    return collided_object


def handle_move(player, objects):
    keys = pygame.key.get_pressed()  # read key input
    player.x_vel = 0  # reset movement velocity

    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)
    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()



def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background('Blue.png')

    block_size = 96
    blocks = [Block(0, HEIGHT - block_size, block_size)]

    player = Player(100, 100, 50, 50)

    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)

    fire.on()

    # create blocks that go to the left and right of screen first range is blocks to left of screen, second is to right
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, WIDTH * 2 // block_size)]

    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size),
               Block(block_size * 3, block_size * 4, block_size), fire]

    offset_x = 0
    scroll_area_width = 200

    run = True
    while run:
        clock.tick(FPS)  # ensures while loop runs at 60FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)
        fire.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        # if moving to the right and character is right on the screen offset the screen by velocity
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or ((player.rect.left - offset_x <= WIDTH - scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)  # only runs game if the file itself is ran
