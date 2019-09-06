#如何将特定游戏绑定到AI框架:
#1.创建游戏对象类,继承自gameai_frame.GameRole
#   必须提供的方法: 'calculate_fitness', 'look'(获取神经网络输入), 'show', 'think'(获取神经网络输出)
#   需要重载的方法(其实只是改一下名称): 'clone', 'crossover'
#   可以重载的方法: 'user_init'(可能没没什么用), 'user_update'(在循环中除了look, think之外需要更新的部分)
#2.定制神经网络和遗传算法的参数
#3.花时间训练
#4.当训练好之后，就可以移除遗传算法的部分了，运用神经网络控制AI, e.g. 如下流程:
#in one frame:
#   Snake.look()
#   Snake.think()
#   Snake.user_update()
#   Snake.show()
from gameai_frame import global_vars as fg
from gameai_frame import *
from MyGameRole import Snake, Mario
from PIL import Image
import game_globaldata as gg
import pygame as pg
import numpy as np
import os
#定制神经网络和遗传算法的参数
def set_aiframe_global_vars():
    fg.NN_INPUT_SIZE = 24 #3 * 8
    fg.NN_OUTPUT_SIZE = 4
    fg.NN_HIDDENLAYER_NUM = 2
    fg.NN_HIDDEN_SIZE = 16
    return
def load_map(file = 'map.png'):
    #define block colors-------------------------------------
    clr_wall = (0, 0, 0)
    #--------------------------------------------------------
    gg.MAP = np.zeros((gg.SCN_BLOCKNUM_Y, gg.SCN_BLOCKNUM_X))
    img = Image.open(file)
    #assert img size
    for i in range(gg.SCN_BLOCKNUM_Y):
        for j in range(gg.SCN_BLOCKNUM_X):
            color = img.getpixel((j, i))
            if color == clr_wall:
                gg.MAP[i][j] = gg.MAP_ENUM_WALL
    return
def show_map():
    interval = gg.BLOCK_SIZE / 16
    square_size = gg.BLOCK_SIZE - interval
    for i in range(gg.SCN_BLOCKNUM_Y):
        for j in range(gg.SCN_BLOCKNUM_X):
            if gg.MAP[i][j] == gg.MAP_ENUM_WALL:
                pg.draw.rect(gg.SCN_Surface, (100, 100, 100),\
                    pg.Rect(j * gg.BLOCK_SIZE, i * gg.BLOCK_SIZE,\
                            square_size, square_size))
def setup():
    set_aiframe_global_vars()
    load_map()
    gg.Pop = Population.Population(fg.AG_POP_SIZE, fg.AG_POP_PM, fg.AG_POP_PC, Snake)
    pg.init()
    os.environ['SDL_VIDEO_WINDOW_POS'] = '%d, %d'%(0, 32)
    gg.SCN_Surface = pg.display.set_mode((gg.SCN_WIDTH, gg.SCN_HEIGHT),\
       pg.DOUBLEBUF)
    pg.display.set_caption('AIFrame Sample')
    return
def run():
    #set up vars only used in loop
    Font_Small = pg.font.Font('Minecraft.ttf', 16)
    Font_Big = pg.font.Font('Minecraft.ttf', 32)
    t_save = Font_Small.render("Save", True, (0, 0, 0))
    t_save_as = Font_Small.render("Save As", True, (0, 0, 0))
    t_load = Font_Small.render("Load", True, (0, 0, 0))
    button_width = 100
    button_height = 22
    button_save_x = gg.SCN_WIDTH - button_width - 12
    button_save_y = 2
    button_save_as_y = button_save_y + 24
    button_load_y = button_save_as_y + 24
    #--------------------------------------------------------------------------------------------
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return
            elif event.type == pg.MOUSEBUTTONDOWN:
                pg.event.clear(pg.MOUSEBUTTONDOWN)
                if button_save_x <= event.pos[0] <= button_save_x + button_width:
                    if button_save_y <= event.pos[1] <= button_save_y + button_height:#save
                            gg.Pop.bestIndv.brain.save()
                    elif button_save_as_y <= event.pos[1] <= button_save_as_y + button_height:#save as
                            gg.Pop.bestIndv.brain.save_as()
                    elif button_load_y <= event.pos[1] <= button_load_y + button_height:#load
                            gg.Pop.bestIndv.brain.load()
        gg.SCN_Surface.fill((255, 255, 255))
        #CORE**************************************
        gg.Pop.update()
        gg.Pop.show()
        #******************************************
        show_map()
        #draw text---------------------------------
        pg.draw.rect(gg.SCN_Surface, (0, 0, 0), pg.Rect(button_save_x, button_save_y, button_width, button_height), 1)
        pg.draw.rect(gg.SCN_Surface, (0, 0, 0), pg.Rect(button_save_x, button_save_as_y, button_width, button_height), 1)
        pg.draw.rect(gg.SCN_Surface, (0, 0, 0), pg.Rect(button_save_x, button_load_y, button_width, button_height), 1)
        if gg.Pop.bestIndv.dead:
            dead = Font_Big.render(gg.Pop.bestIndv.illus_dead_reason, True, (255, 0, 0))
            gg.SCN_Surface.blit(dead, (0.5 * (gg.SCN_WIDTH - dead.get_rect().width), gg.SCN_HEIGHT * 0.5))
        gg.SCN_Surface.blit(t_save, (button_save_x + 8, button_save_y))
        gg.SCN_Surface.blit(t_save_as, (button_save_x + 8, button_save_as_y))
        gg.SCN_Surface.blit(t_load, (button_save_x + 8, button_load_y))
        #------------------------------------------
        pg.display.flip()
    return
if __name__ == '__main__':
    setup()
    run()