import sys
import pygame as pg
import numpy as np
import imageio
from pygame.locals import *
from PIL import Image

PHONE_RESOLUTION = (1440,2960)
HD1080_RESOLUTION = (1920,1080)
HD720_RESOLUTION = (1280,720)
WINXP_RESOLUTION = (800, 600)
HD1080_SMALL_RESOLUTION = (480, 270)
ATARI_RESOLUTION = (192, 160)

pg.init()
pg.display.set_caption("Test Images")
pg.display.set_icon(pg.image.load("./images/caipiragames.png"))

s = 48
tilemap = Image.open('tilemap.png')
tilemap_array = np.asarray(tilemap)
imageio.imsave('tile.png', tilemap_array[0:s,0:s,:])

tile = pg.image.load("tile.png")
tile_img = Image.open('tile.png')

screen = pg.display.set_mode(HD720_RESOLUTION)
# image = pg.image.load('player.png')

def convert_image(square_tile, r, angle):
    '''
    Converts image
    '''
    tile_array = np.asarray(square_tile)

    s = tile_array.shape[0]
    if s != tile_array.shape[1]:
        raise Exception("Tile must be square.")

    # scale = 10
    # new_tile_array = np.zeros([scale*s, scale*s, 4])
    # for i in range(s-1):
    #     for j in range(s-1):
    #         for k in range(4):
    #             new_tile_array[scale*i:scale*(i+1),scale*j:scale*(j+1),k] = tile_array[i,j,k]*np.ones([scale,scale])

    # s = new_tile_array.shape[0]
    w = int(2*(r+s)*np.sin(angle/2))
    h = int(r*(1-np.cos(angle/2)) + s)

    converted_tile_array = np.zeros([h,w,4])
    for i in range(s):
        for j in range(s):
            i_transf = int(round( (r+s) - (r+s-j)*np.cos(-angle/2 + i*(angle/s)) ))
            j_transf = int(round( w/2 + (r+s-j)*np.sin(-angle/2 + i*(angle/s)) ))
            converted_tile_array[i_transf, j_transf,:] = tile_array[i,j,:]

    return converted_tile_array.tolist()

if __name__ == '__main__':
    # while True:
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()

        screen.fill(Color("BLACK"))
        screen.blit(tile, (0,0))
        
        Rmax = 400
        angle = np.pi/20
        round_tile = convert_image(tile_img, Rmax, angle)
        imageio.imsave('round_tile.png', round_tile)

        pg.display.update()

pg.quit()