import numpy as np
import os, sys, csv

filename_open = '4243423'

try:
    grid = []
    with open(os.path.join(filename_open+str('.csv'))) as data:
        data = csv.reader(data, delimiter=',')
        for row in data:
            grid.append(list(row))
    tilegrid = np.array(grid,dtype=int)
except IOError:
    print("Couldn't locate "+filename_open+str('.csv'))

num_cols = tilegrid.shape[1]

flipped_tilegrid = np.flip(tilegrid, axis=1)

rolled_tilegrid = np.roll(flipped_tilegrid, shift=int(num_cols/4)+1, axis=1)

filename_save = 'map2'

with open(filename_save+str('.csv'), mode='w', newline='') as file:
    file_writer = csv.writer(file, delimiter=',')
    for row in range(rolled_tilegrid.shape[0]):
        file_writer.writerow(rolled_tilegrid[row].tolist())
print("Tile map saved.")