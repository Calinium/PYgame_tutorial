from os import walk
import pygame
from csv import reader
from settings import tile_size

def import_folder(path):
    surface_list = []

    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image

            scale = 1
            image_surf = pygame.image.load(full_path)
            if 'bang_mark' in full_path:
                scale = 0.05
            elif 'fireball' in full_path:
                scale = 0.3
            elif 'dust_particles' not in full_path:
                scale = 2

            image_surf = pygame.transform.scale(image_surf, (image_surf.get_size()[0]*scale, image_surf.get_size()[1]*scale)).convert_alpha()
            surface_list.append(image_surf)

    return surface_list

def import_csv_layout(path):
    terrain_map = []
    with open(path) as map_:
        level = reader(map_, delimiter=',')
        for row in level:
            terrain_map.append(list(row))
        return terrain_map
    
def import_cut_graphics(path):
    surface = pygame.image.load(path).convert_alpha()
    surface = pygame.transform.scale(surface, (surface.get_size()[0]*2.66666666667, surface.get_size()[1]*2.66666666667)).convert_alpha()
    tile_num_x = int(surface.get_size()[0] / tile_size)
    tile_num_y = int(surface.get_size()[1] / tile_size)

    cut_tiles = []
    for row in range(tile_num_y):
        for col in range(tile_num_x):
            x = col * tile_size
            y = row * tile_size
            new_surf = pygame.Surface((tile_size, tile_size),flags=pygame.SRCALPHA)
            new_surf.blit(surface, (0, 0), pygame.Rect(x, y, tile_size, tile_size))
            cut_tiles.append(new_surf)

    return cut_tiles
    