from support import import_folder
import pygame
import math

class Fireball(pygame.sprite.Sprite):
    def __init__(self, surface, x, y, target, targetx, targety):
        super().__init__()
        self.import_fireball_assets()
        self.display_surface = surface
        self.target = target
        self.speed = 6

        self.angle = math.atan2(targety-y, targetx-x)
        self.dx = math.cos(self.angle)*self.speed
        self.dy = math.sin(self.angle)*self.speed
        self.x = x
        self.y = y

        self.fireball_index = 0
        self.duration_index = 0

        self.size = 32
        self.rect = pygame.Rect(x-self.size/2, y-self.size/2, self.size, self.size)

    def import_fireball_assets(self):
        fireball_path = r'assets\enemies\fireball'
        self.fireball_animations = import_folder(fireball_path)

    def target_collision(self):
        if self.rect.colliderect(self.target.rect):
            isFireballOnRight = self.rect.x > self.target.rect.x
            self.target.hurt(isFireballOnRight)
            self.kill()

    def shoot(self):
        self.fireball_index += 0.1
        self.duration_index += 0.1

        # when animation ended
        if self.fireball_index >= len(self.fireball_animations):
            self.fireball_index = 0
        if self.duration_index > 20:
            self.kill()

        #act
        self.x += self.dx
        self.y += self.dy
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

 
        image = self.fireball_animations[int(self.fireball_index)]
        rotate_image = pygame.transform.rotate(image, -math.degrees(self.angle))
        self.display_surface.blit(rotate_image, (self.rect.x, self.rect.y))
        self.rect.center = rotate_image.get_rect(center=self.rect.center).center
        # pygame.draw.rect(self.display_surface, (0, 255, 0), self.rect)

    def update(self, x_shift):
        self.x += x_shift
        self.shoot()
        self.target_collision()
