import pygame
from pygame.locals import *
from pygame.math import *
from math import *
import ctypes
import random

import numpy as np

user32 = ctypes.windll.user32
SCREEN_SIZE = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

pygame.init()

screen = pygame.display.set_mode(SCREEN_SIZE)

font = pygame.font.SysFont(None, 36)

class Board():
    def __init__(self, dimensions):
        self.dimensions = dimensions
        self.board = np.full((int(dimensions.x), int(dimensions.y)), 0, dtype=int)
        self.start_offset = BOARD_OFFSET * TILE_SIZE

    def check_valid(self, shape, pos):
        for x in range(0, len(shape[0])):
            for y in range(0, len(shape)):
                if (shape[x, y] == True):
                    try:
                        print(f'checking pos {x + int(pos.x)} {y + int(pos.y)}')
                        if (self.board[x + int(pos.x), y + int(pos.y)] != 0):
                            print('block already occupied - new position not valid')
                            return False
                        if (x + int(pos.x) < 0 or y + int(pos.y) < 0):
                            return False
                    except IndexError:
                        print('block out of bound - new position not valid')
                        return False
        return True
    
    def try_clear_line(self):
        for y in range(0, int(self.dimensions.y)):
            line_clearable = True
            for x in range(0, int(self.dimensions.x)):
                if self.board[x, y] == 0:
                    line_clearable = False
            if line_clearable:
                board_updated = True
                # Allocate every line that is at the same level or above the clearing line values of the line directly above it
                for y_prime in range(y, 0, -1):
                    for x in range(0, int(self.dimensions.x)):
                        self.board[x, y_prime] = self.board[x, y_prime - 1]
                
                # Empty uppermost line
                for x in range(0, int(self.dimensions.x)):
                    self.board[x, 0] = 0

    def draw(self):
        pygame.draw.rect(
            screen,
            Color(64, 64, 64), 
            Rect(self.start_offset.x, self.start_offset.y,
                    TILE_SIZE * BOARD_SIZE.x, TILE_SIZE * BOARD_SIZE.y))
        
        for x in range(0, int(self.dimensions.x)):
            for y in range(0, int(self.dimensions.y)):
                if self.board[x, y] != 0:
                    pygame.draw.rect(
                        screen,
                        COLORS[self.board[x, y]],
                        Rect(self.start_offset.x + x * TILE_SIZE,
                            self.start_offset.y + y * TILE_SIZE,
                            TILE_SIZE, TILE_SIZE)
                    )

class Block():    
    def __init__(self, block_preset, board):
        self.shape = block_preset.shape
        self.center = block_preset.center
        self.color_index = block_preset.color_index
        self.position = Vector2(int(BOARD_SIZE.x/2 - self.center/2), 0)
        self.board = board
        self.moved_prev = False

    def try_rotate(self, direction):
        assert direction == 0 or direction == 1

        if (direction == 1):
            self.shape = np.rot90(self.shape)
        elif (direction == 0):
            self.shape = np.rot90(np.rot90(np.rot90(self.shape)))

        if not self.board.check_valid(self.shape, self.position):
            for delta_p in [Vector2(0, 1), Vector2(0, -1), Vector2(-1, 0), Vector2(1, 0), Vector2(0, 2), Vector2(0, -2), Vector2(-2, 0), Vector2(2, 0)]:
                if self.board.check_valid(self.shape, self.position + delta_p):
                    self.position += delta_p
                    break
        
        self.moved_prev = True
        global board_updated
        board_updated = True

    def pin_block(self):
        for x in range(0, len(self.shape[0])):
            for y in range(0, len(self.shape)):
                if (self.shape[x, y] == True):
                    self.board.board[x + int(self.position.x), y + int(self.position.y)] = self.color_index

        initialize_new_block(choose_random_block())
        global board_updated
        board_updated = True

    def try_move(self, delta_p):
        if delta_p != None:
            if not self.moved_prev:
                if delta_p.y == 1:
                    if not board.check_valid(self.shape, self.position + delta_p):
                        self.pin_block()

            if board.check_valid(self.shape, self.position + delta_p):
                self.position += delta_p
                self.moved_prev = True
                global board_updated
                board_updated = True
    
    def fall(self):
        self.try_move(Vector2(0, 1))
        self.moved_prev = False

    def draw(self):
        for x in range(0, int(len(self.shape))):
            for y in range(0, int(len(self.shape[0]))):
                if (self.shape[x, y] != 0):
                    pygame.draw.rect(screen,
                        COLORS[self.color_index],
                        Rect(TILE_SIZE * (BOARD_OFFSET.x + self.position.x + x),
                            TILE_SIZE * (BOARD_OFFSET.y + self.position.y + y),
                            TILE_SIZE, TILE_SIZE
                    ))

class Block_Preset():
    def __init__(self, shape, color_index):
        self.shape = shape
        self.center = len(shape)
        self.color_index = color_index

BOARD_SIZE = Vector2(16, 28)
BOARD_OFFSET = Vector2(1, 1)
TILE_SIZE = 32
FALL_DELAY = 500
MOVE_DELAY = 50

COLOR_RED = (255, 0, 0)
COLOR_PURPLE = (255, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_YELLOW = (255, 255, 0)
COLOR_ORANGE = (255, 128, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_AQUA = (0, 255, 255)
COLORS = [(0, 0, 0), COLOR_RED, COLOR_ORANGE, COLOR_YELLOW, COLOR_GREEN, COLOR_AQUA, COLOR_BLUE, COLOR_PURPLE]

i_block = Block_Preset(np.array([[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]]), 5)
j_block = Block_Preset(np.array([[1, 0, 0], [1, 1, 1], [0, 0, 0]]), 6)
l_block = Block_Preset(np.array([[0, 0, 1], [1, 1, 1], [0, 0, 0]]), 2)
o_block = Block_Preset(np.array([[1, 1], [1, 1]]), 3)
s_block = Block_Preset(np.array([[1, 1, 0], [0, 1, 1], [0, 0, 0]]), 4)
t_block = Block_Preset(np.array([[1, 1, 1], [0, 1, 0], [0, 0, 0]]), 7)
z_block = Block_Preset(np.array([[0, 1, 1], [1, 1, 0], [0, 0, 0]]), 1)

block_presets = [i_block, j_block, l_block, o_block, s_block, t_block, z_block]

board = Board(BOARD_SIZE)

def initialize_new_block(block_preset):
    global current_block
    current_block = Block(block_preset, board)

def choose_random_block():
    return block_presets[random.randint(0, len(block_presets) - 1)]

initialize_new_block(choose_random_block())
previous_fall_t = pygame.time.get_ticks()
press_move_t = pygame.time.get_ticks()
rotate_available = [True, True]
board_updated = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.display.quit()
            pygame.quit()
            break
    else:
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_z]:
            if rotate_available[0]:
                current_block.try_rotate(1)
                rotate_available[0] = False
        else:
            rotate_available[0] = True
        
        
        if pressed_keys[K_x]:
            if rotate_available[1]:
                current_block.try_rotate(0)
                rotate_available[1] = False
        else:
            rotate_available[1] = True

        if pygame.time.get_ticks() - press_move_t >= MOVE_DELAY:
            press_move_t = pygame.time.get_ticks()
            if pressed_keys[K_UP]:
                current_block.try_move(Vector2(0, -1))
            if pressed_keys[K_DOWN]:
                current_block.try_move(Vector2(0, 1))
            if pressed_keys[K_RIGHT]:
                current_block.try_move(Vector2(1, 0))
            if pressed_keys[K_LEFT]:
                current_block.try_move(Vector2(-1, 0))
            if pressed_keys[K_SPACE]:
                pass
            if pressed_keys[K_SPACE]:
                pass
        
        if board_updated:
            board.try_clear_line()

            screen.fill((0, 0, 0))
            board.draw()
            current_block.draw()
            pygame.display.update()

        if pygame.time.get_ticks() - previous_fall_t >= FALL_DELAY:
            previous_fall_t = pygame.time.get_ticks()
            current_block.fall()

def pass_state():
    tuple = board
    for y in range(current_block.shape[x]):
        for x in range(current_block.shape[y]):
            tuple[current_block.position.x + x, current_block.posution.y + y] = current_block[x, y]

    return tuple

def receive_action():
    pass