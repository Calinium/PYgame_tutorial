import pygame
from tiles import Tile, StaticTile
from settings import tile_size, screen_width
from player import Player
from particles import ParticleEffect
from support import import_csv_layout, import_cut_graphics
from enemy import Enemy
from background import BackGround

class Level:
    def __init__(self, level_data, surface):
        # general setup
        self.display_surface = surface
        self.world_shift = 0
        self.change_shift = 0

        #player
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.player_setup(player_layout)
        
        self.world_width = len(player_layout) * tile_size
        self.world_height = len(player_layout[0]) * tile_size

        #terrain setup
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_sprites = self.create_tile_group(terrain_layout, 'terrain')

        #decoration setup
        decorations_layout = import_csv_layout(level_data['decorations'])
        self.decorations_sprites = self.create_tile_group(decorations_layout, 'decorations')

        #enemies setup
        enemies_layout = import_csv_layout(level_data['enemies'])
        self.enemies_sprites = self.create_tile_group(enemies_layout, 'enemies')

        #enemie_border setup
        border_layout = import_csv_layout(level_data['border'])
        self.border_sprites = self.create_tile_group(border_layout, 'border')

        self.background = BackGround()

        self.current_x = 0

        # dust
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False

    def create_tile_group(self, layout, type_):
        sprite_group = pygame.sprite.Group()
        
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size
                    
                    if type_ == 'terrain':
                        terrain_tile_list = import_cut_graphics('./assets/map/terrain/oak_woods_tileset.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile((x, y), tile_size, tile_surface)

                    if type_ == 'decorations':
                        decorations_tile_list = import_cut_graphics('./assets/map/terrain/decorations/decorations.png')
                        tile_surface = decorations_tile_list[int(val)]
                        sprite = StaticTile((x, y), tile_size, tile_surface)

                    if type_ == 'enemies':
                        if int(val) == 0:
                            sprite = Enemy((x,y), tile_size, self.display_surface, self.player,'mage')
                        else:
                            sprite = Enemy((x,y), tile_size, self.display_surface, self.player, 'worrior')

                    if type_ == 'border':
                        sprite = Tile((x, y), tile_size)

                    sprite_group.add(sprite)

        return sprite_group

    def player_setup(self, layout):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val == '0':
                    x = col_index * tile_size
                    y = row_index * tile_size
                    sprite = Player((x,y), self.display_surface, self.create_jump_particles)
                    self.player.add(sprite)

    def enemy_collision_reverse(self):
        for enemy in self.enemies_sprites.sprites():
            for border in self.border_sprites.sprites():
                if border.rect.colliderect(enemy.rect):
                    condition = (enemy.speed < 0 and abs(enemy.rect.left - border.rect.right) < tile_size) or (enemy.speed > 0 and abs(enemy.rect.right - border.rect.left) < tile_size)
                    if condition:
                        if enemy.detect_level == 2 and enemy.type == 'worrior':
                            if enemy.speed < 0 and abs(enemy.rect.left - border.rect.right) < tile_size:
                                enemy.rect.left = border.rect.right
                            elif enemy.speed > 0 and abs(enemy.rect.right - border.rect.left) < tile_size:
                                enemy.rect.right = border.rect.left
                        else:
                            enemy.reverse()

    def create_jump_particles(self, pos):
        if self.player.sprite.facing_right:
            pos -= pygame.math.Vector2(10, 5)
        else:
            pos += pygame.math.Vector2(10, -5)
        jump_particle_sprite = ParticleEffect(pos, 'jump')
        self.dust_sprite.add(jump_particle_sprite)

    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False

    def create_landing_dust(self):
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(10, 15)
            else:
                offset = pygame.math.Vector2(-10, 15)
            fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset, 'land')
            self.dust_sprite.add(fall_dust_particle)

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx

        if player_x < screen_width/2-tile_size*3.5:
            self.change_shift += 0.3
        elif player_x > screen_width/2+tile_size*3.5:
            self.change_shift -= 0.3
        else: 
            if self.change_shift > 0:
                self.change_shift -= 0.3
            elif self.change_shift < 0: 
                self.change_shift += 0.3

        limit = player.speed - 0.5
        if self.change_shift > limit:
            self.change_shift = limit
        elif self.change_shift < -limit:
            self.change_shift = -limit

        self.world_shift = int(self.change_shift)

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()

        for sprite in self.terrain_sprites.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0 and abs(player.rect.bottom - sprite.rect.top) < tile_size:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0 and abs(player.rect.top - sprite.rect.bottom) < tile_size:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 0:
            player.on_ceiling = False

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.direction.x = round(player.direction.x,2)
        player.rect.x += player.direction.x * player.speed

        for sprite in self.terrain_sprites.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0 and abs(player.rect.left - sprite.rect.right) < tile_size:
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0 and abs(player.rect.right - sprite.rect.left) < tile_size:
                    player.rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right

        if player.on_left and (player.rect.left < self.current_x or player.direction.x>=0):
            player.on_left = False
        if player.on_right and (player.rect.right > self.current_x or player.direction.x<=0):
            player.on_right = False

    def run(self): 
        self.scroll_x()

        #background
        self.background.update_and_draw(self.display_surface, self.world_shift)
        
        # terrain
        self.terrain_sprites.update(self.world_shift)
        self.terrain_sprites.draw(self.display_surface)

        # decorations
        self.decorations_sprites.update(self.world_shift)
        self.decorations_sprites.draw(self.display_surface)

        # enemies
        self.border_sprites.update(self.world_shift)
        self.enemy_collision_reverse()
        self.enemies_sprites.update(self.world_shift)
        self.enemies_sprites.draw(self.display_surface)

        # dust paritcles
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)

        # player
        self.player.update(self.world_shift)
        self.get_player_on_ground()
        self.horizontal_movement_collision()
        self.vertical_movement_collision() 

        self.create_landing_dust()
        self.player.draw(self.display_surface)