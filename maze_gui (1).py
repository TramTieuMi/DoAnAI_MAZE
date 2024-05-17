import math
from simpleai.search import SearchProblem, astar
import numpy as np
import cv2
import tkinter as tk
from PIL import Image, ImageTk
import time
import streamlit as st
import streamlit.components.v1 as components

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from search import *

# Define cost of moving around the map
cost_regular = 1.0
cost_diagonal = 1.7

# Create the cost dictionary
COSTS = {
    "up": cost_regular,
    "down": cost_regular,
    "left": cost_regular,
    "right": cost_regular,
    "up left": cost_diagonal,
    "up right": cost_diagonal,
    "down left": cost_diagonal,
    "down right": cost_diagonal,
}

# Define the map
MAP = """
##############################
#         #              #   #
# ####    ########       #   #
#    #    #              #   #
#    ###     #####  ######   #
#      #   ###   #           #
#      #     #   #  #  #   ###
#     #####    #    #  #     #
#              #       #     #
##############################
"""

# Convert map to a list
MAP = [list(x) for x in MAP.split("\n") if x]
M = 10
N = 30
W = 21
mau_xanh = np.zeros((W, W, 3), np.uint8) + (np.uint8(255), np.uint8(0), np.uint8(0))
mau_trang = np.zeros((W, W, 3), np.uint8) + (np.uint8(255), np.uint8(255), np.uint8(255))
image = np.ones((M * W, N * W, 3), np.uint8) * 255

# Calculate the starting position for drawing the maze in the middle of the canvas
start_x = ((N * W - len(MAP[0]) * W) // 2)
start_y = (M * W - len(MAP) * W) // 2

for y in range(0, M):
    for x in range(0, N):
        if MAP[y][x] == '#':
            image[start_y + y * W:(start_y + y + 1) * W, start_x + x * W:(start_x + x + 1) * W] = mau_xanh
        elif MAP[y][x] == ' ':
            image[start_y + y * W:(start_y + y + 1) * W, start_x + x * W:(start_x + x + 1) * W] = mau_trang

color_coverted = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
pil_image = Image.fromarray(color_coverted)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.dem = 0
        self.title('Tìm đường trong mê cung')

        # Adjust the size of the canvas to make it larger
        canvas_width = N * W + 50
        canvas_height = M * W + 100

        # Create a canvas for the maze
        self.cvs_me_cung = tk.Canvas(self, width=canvas_width, height=canvas_height,
                                     relief=tk.SUNKEN, border=1)
        self.image_tk = ImageTk.PhotoImage(pil_image)
        self.cvs_me_cung.create_image(0, 0, anchor=tk.NW, image=self.image_tk)
        self.cvs_me_cung.create_text(N * W // 2, 15, text="Tìm Công Chúa", font=("Helvetica", 16), fill="black")
        self.cvs_me_cung.bind("<Button-1>", self.xu_ly_mouse)
        self.cvs_me_cung.pack()

        lbl_frm_menu = tk.LabelFrame(self)
        btn_start = tk.Button(lbl_frm_menu, text='Start', width=7,
                              command=self.btn_start_click)
        btn_reset = tk.Button(lbl_frm_menu, text='Reset', width=7,
                              command=self.btn_reset_click)
        btn_start.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N)
        btn_reset.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N)

        lbl_frm_menu.pack(side=tk.RIGHT, padx=10, pady=10)

    def xu_ly_mouse(self, event):
        if self.dem == 0:
            px = event.x
            py = event.y
            x = (px - start_x) // W
            y = (py - start_y) // W
            if y >= 0 and y < M and x >= 0 and x < N and MAP[y][x] == ' ':
                MAP[y][x] = 'o'
                self.cvs_me_cung.create_oval(start_x + x * W + 2, start_y + y * W + 2, start_x + (x + 1) * W - 2,
                                             start_y + (y + 1) * W - 2, outline='#FF0000', fill='#FF0000')
                self.dem = self.dem + 1
        elif self.dem == 1:
            px = event.x
            py = event.y
            x = (px - start_x) // W
            y = (py - start_y) // W
            if y >= 0 and y < M and x >= 0 and x < N and MAP[y][x] == ' ':
                MAP[y][x] = 'x'
                self.cvs_me_cung.create_rectangle(start_x + x * W + 2, start_y + y * W + 2, start_x + (x + 1) * W - 2,
                                                  start_y + (y + 1) * W - 2, outline='#FF0000', fill='#FF0000')
                self.dem = self.dem + 1

    def btn_start_click(self):
        problem = MazeSolver(MAP)
        # Run the solver
        result = astar(problem, graph_search=True)

        # Extract the path
        path = [x[1] for x in result.path()]

        # Print the result
        '''
        print()
        for y in range(len(MAP)):
            for x in range(len(MAP[y])):
                if (x, y) == problem.initial:
                    print('o', end='')
                elif (x, y) == problem.goal:
                    print('x', end='')
                elif (x, y) in path:
                    print('·', end='')
                else:
                    print(MAP[y][x], end='')
            print()
        print(path)
        '''
        L = len(path)
        for i in range(1, L):
            x = path[i][0]
            y = path[i][1]
            self.cvs_me_cung.create_rectangle(x*W+2, y*W+2, (x+1)*W-2, (y+1)*W-2, 
                                         outline = '#FF0000', fill = '#FF0000')
            time.sleep(0.5)
            self.cvs_me_cung.update()

    def btn_reset_click(self):
        self.cvs_me_cung.delete(tk.ALL)
        self.cvs_me_cung.create_image(0, 0, anchor = tk.NW, image = self.image_tk)
        self.dem = 0
        for x in range(0, M):
            for y in range(0, N):
                if MAP[x][y] == 'o' or MAP[x][y] == 'x':
                    MAP[x][y] = ' '

if	__name__ ==	"__main__":
    app	=	App()
    app.mainloop()
