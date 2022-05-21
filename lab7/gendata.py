################################################################################
# This code was written for lab 7 of CST 475,    Based on https://bit.ly/3sO1iT6
# taught at Oregon Tech by Prof. Cecily Heiner
################################################################################

# Automatic training data generation for Slither.io bot.
# This code works on my laptop, and more than likely only my laptop.
# The data generated is a .csv file in the format of:   

# COLS      DATA                    TYPE
# 0 - 17346 [screenshot of game]    (147 x 118) values are 0 or 255
# 17347     direction               radians
# 17348     previous score          int
# 17349     current score           int
# 17350     diff of scores          int

# Imports ######################################################################

from cv2 import FileNode_NAMED
import pyautogui
import time
import pytesseract
import math
import random
import numpy as np
import cv2
import re
from PIL import Image
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract"
)

# Functions ####################################################################

# starts the webdriver (opens the game in the browser)
# sizes and posisions the browser
def start_slither():
    chromeopts = Options()
    chromeopts.add_argument(f"--window-size={600},{600}")
    chromeopts.add_experimental_option("excludeSwitches", ["enable-logging"])
    browser = webdriver.Chrome(
        service=Service(ChromeDriverManager(log_level=0).install()), options=chromeopts
    )
    browser.set_window_position(-8, 0)
    browser.get("http://www.slither.io")

    return browser

# clicks on the start/replay buttom
# clicks twice more to make the game listen to future mouse movements
def start_game():
    time.sleep(1)
    pyautogui.click(start_button_position_x, start_button_position_y)
    time.sleep(1)
    pyautogui.click(start_button_position_x, start_button_position_y)
    time.sleep(0.5)
    pyautogui.click(start_button_position_x, start_button_position_y)

# checks if the word 'Skin' is where the score normally is
# if so the player is dead and this function returns true
def is_dead():
    img = screenshot(98, 701, 45, 20, threshold=100)
    read = pytesseract.image_to_string(img, lang="eng", config="--psm 6")
    if "skin" in read.lower():
        return True
    else:
        return False

# takes a screenshot, filters, and compresses
def screenshot(x, y, width, height, threshold=-1, reduction_factor=1):
    raw = pyautogui.screenshot(region=(x, y, width, height))
    data = np.array(raw)

    img = cv2.cvtColor(data, cv2.COLOR_BGR2GRAY)

    if threshold != -1:
        ret, img = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY_INV)

    img = img[::reduction_factor, ::reduction_factor]

    return img

# reads the score of the game, will not return until reads a valid score
def get_score(old_score):
    got = False
    while not got:

        if is_dead():
            return -1

        img = screenshot(106, 695, 50, 20, threshold=190)

        score = pytesseract.image_to_string(img, lang="eng", config="--psm 6")

        score = re.sub("[^0-9]", "", score)

        if score != "" and int(score) >= old_score:
            score = int(score)
            return score

# point the snake a direction given in radians
def move_to_radians(radians, radius=50):
    pyautogui.moveTo(
        window_center_x + radius * math.cos(radians),
        window_center_y + radius * math.sin(radians),
    )

    return radians

# main data collection loop
def collect_data(data_points, output_file, time_gap=1, verbose=True, delete_file=False):
    score = 10

    writing_mode = "a"
    if delete_file:
        writing_mode = "w"

    with open(output_file, writing_mode, newline="") as _f:
        for i in range(data_points):
            if is_dead():
                print("Restarting game.")
                start_game()
                score = 10
            """ 
            data = screenshot(
                100,
                height / 2,
                width - 200,
                height / 2,
                threshold=85,
                reduction_factor=5,
            )
            """
            direction = move_to_radians(random.uniform(0, math.pi * 2))

            data = screenshot(
                0,
                tool_bar_height,
                width,
                height - tool_bar_height,
                threshold=85,
                reduction_factor=5,
            )

            #Image.fromarray(data).save("data.png")

            values = data.shape[0] * data.shape[1]
            data = data.reshape(values)

            old_score = score

            time.sleep(time_gap)
            score = get_score(old_score)

            data = np.append(data, [direction, old_score, score, score - old_score])
            np.savetxt(_f, [data], fmt="%5d", delimiter=",")

            if verbose:
                print(
                    f"({round(((i+1)/data_points)*100, 2)}%) Data point "
                    + f"{i+1}/{data_points} collected. "
                    + f"Direction: {round(direction,2)}, "
                    + f"Score changed by: {score-old_score}"
                )

        _f.close()


################################################################################

tool_bar_height = 156

width = 735
height = 745

window_center_x = width / 2
window_center_y = tool_bar_height + ((height - tool_bar_height) / 2)

start_button_position_x = width / 2
start_button_position_y = 575

data_points = int(input("Job size: "))
csv_name = input("csv file: ")
delete_file = input("overwrite file? y/n: ").lower() == "y"
verbose = input("verbose? y/n: ").lower() == "y"

print("\nStarting Slither.io...")
browser = start_slither()

# low graphics
pyautogui.click(660, 228)

print("Starting Data generation loop...")
collect_data(data_points, csv_name, verbose=verbose, delete_file=delete_file)
print("Done!")