import pygame
from support import import_folder

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        self.image = pygame.Surface((size, size))
        # self.image.fill('grey')
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, x_shift):
        self.rect.x += x_shift

class StaticTile(Tile):
    def __init__(self, pos, size, surface):
        super().__init__(pos, size)
        self.image = surface

class AnimatedTile(Tile):
    def __init__(self, pos, size, surface, path):
        super().__init__(pos, size)
        self.frames = import_folder(path)
        self.frame_index = 0
        # self.image = self.frames[self.frame_index]
        self.image = pygame.Surface((32, 64))
        self.image.fill('red')
        self.motion_image = self.image
        # self.image.set_alpha(0)
        self.rect = self.image.get_rect(topleft=pos)
        self.surface = surface

    def animate(self):
        self.frame_index += 0.15
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        self.motion_image = self.frames[int(self.frame_index)]
        self.surface.blit(self.motion_image, (self.rect.topleft[0]-25, self.rect.topleft[1]-22))

    def update(self, x_shift):
        self.animate()
        self.rect.x += x_shift