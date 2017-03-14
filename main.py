import numpy as np
from utils import *
from PIL import Image
from PIL import ImageGrab
from cell_decoder import CellRecognizer
import win32api
import win32con
import time
import move_maker

board_box = (100, 136, 681, 653)
img_size = (board_box[2] - board_box[0], board_box[3] - board_box[1])
cell_size = (img_size[0] / 9, img_size[1] / 9)
game_board = np.zeros((board_size, board_size), dtype=np.int32)
recognizer = CellRecognizer()


# It takes the screenshot of the board and then crops each cell using a nested loop
def grab_board():
    global game_board
    img = ImageGrab.grab()

    img = img.crop(board_box)
    for y in range(0, 9):
        for x in range(0, 9):
            cell_box = (x * cell_size[0], y * cell_size[1], (x + 1) * cell_size[0], (y + 1) * cell_size[1])
            cell = img.crop(cell_box)
            game_board[y][x] = recognizer.predict(cell)

    print_board(game_board)
    return img


ref_img = None


# checks if the board is in moving state (It is in moving state after the candies have been exploded)
def board_is_moving():
    global ref_img
    img = ImageGrab.grab()
    img = img.crop(board_box)
    img = img.resize((img.size[0] / 4, img.size[1] / 4), Image.NEAREST)

    has_movement = True
    if ref_img:
        has_movement = compare_images(img, ref_img, threshold=100) > 100

    ref_img = img
    return has_movement


# for comparing the pixels of the cell board
def are_pixels_equal(p1, p2, threshold):
    diff = 0
    for i in range(3):
        diff += abs(p1[i] - p2[i])
    return diff < threshold


def compare_images(current, reference, threshold):
    current_data = np.array(current.getdata())
    ref_data = np.array(reference.getdata())

    diff_pixels = 0
    total_size = current.size[0] * current.size[1]
    for i in range(0, total_size - 3, 3):
        if not are_pixels_equal(current_data[i], ref_data[i], threshold):
            diff_pixels += 1

    print diff_pixels
    return diff_pixels


background_img = Image.open('background.bmp')
background_img = background_img.resize((background_img.size[0] / 4, background_img.size[1] / 4), Image.NEAREST)


#  for imitating the clicks on the board
def win32_click(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)


# it gets the coords of the central part of the cell
def get_desktop_coords(cell):
    x = board_box[0] + cell[1] * cell_size[0] + cell_size[0] / 2
    y = board_box[1] + cell[0] * cell_size[1] + cell_size[1] / 2
    return x, y


# sort of main function for win32 api
def do_move(move):
    start = move[0]
    end = move[1]

    start_w = get_desktop_coords(start)
    end_w = get_desktop_coords(end)

    win32api.SetCursorPos(start_w)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, start_w[0], start_w[1], 0, 0)
    time.sleep(0.3)  # for waiting the board to settle down after explosions
    win32api.SetCursorPos(end_w)
    time.sleep(0.3)  # for waiting the board to settle down after explosions
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, end_w[0], end_w[1], 0, 0)

    win32api.SetCursorPos((1100, 1100))


# the main function for the entire program also responsible for the training of the classifier
def main():
    recognizer.train()
    maker = move_maker.MoveMaker()
    img_end_game = Image.open('end_screen.bmp')
    img_end_game = img_end_game.resize((img_end_game.size[0] / 4, img_end_game.size[1] / 4), Image.NEAREST)
    total_moves = 0
    while True:
        if not board_is_moving():
            board_img = grab_board()
            board_img = board_img.resize((board_img.size[0] / 4, board_img.size[1] / 4), Image.NEAREST)
            if compare_images(board_img, img_end_game, 10) < 3000:
                break
            score, move = maker.solve_board(game_board)
            print '\nBest move found. Score = {0}, Move = {1}'.format(score, move)
            do_move(move)
            total_moves += 1
        time.sleep(0.4)
    print 'Total moves done: ' + str(total_moves)
