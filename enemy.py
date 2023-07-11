import pygame
from tiles import Tile
from random import randint
from support import import_folder
from fireball import Fireball

class Enemy(Tile):
    def __init__(self, pos, size, surface, player, type_): ## 기초 설정
        super().__init__(pos, size)

        # setup animation
        self.import_enemies_assets(type_) # 적 모델 불러오기
        self.import_bang_assets() # 느낌표(적이 아군 감지했을 때) 모델 불러오기
        self.frame_index = 0 # 애니메이션 프레임 인덱스 설정
        self.bang_index = 0 # 느낌표 인덱스 설정
        self.detect_level = 0 # 플레이어 감지 레벨 설정 /  0: walk, 1: idle, 2: attack
        self.type = type_ # 적 타입 설정

        # 상태 설정
        self.facing_right = True
        self.status = 'walk'
        
        # 히트박스 그리기
        self.image = pygame.Surface((32, 64))
        self.image.set_alpha(0)
        self.rect = self.image.get_rect(topleft=pos)

        # 플레이어 sprite 가져오기
        self.player = player.sprite

        # 디스플레이 스크린 가져오기
        self.display_surface: pygame.Surface = surface

        # 적 타입 구분하기
        if type_ == 'worrior':
            self.speed = randint(4, 5)
            self.hp = 2
        else: #mage
            self.speed = randint(2, 3)
            self.hp = 1
            #fireball
            self.fireball_sprites = pygame.sprite.Group() # 메이지는 파이어볼 스프라이트 설정
            
    def import_enemies_assets(self, type_): ## 적 모델 로드 함수
        enemies_path = './assets/enemies/'+type_+'/'
        self.animations = {'attack':[],'death':[],'hurt':[],'idle':[], 'walk':[]}

        for animation in self.animations.keys():
            full_path = enemies_path + animation
            self.animations[animation] = import_folder(full_path)

    def import_bang_assets(self): ## 느낌표 모델 로드 함수
        bang_path = r'assets\enemies\bang_mark'
        self.bang_animations = import_folder(bang_path)

    def move(self): ## 움직임 함수
        self.rect.x += self.speed # 히트박스 x값에 스피드만큼 더하기

    def hurt(self, damage): ## 피해 입었을 때 함수
        if self.status != 'hurt' and self.status != 'death': # 아프지 않거나 죽지 않았으면
            self.status = 'hurt' # 상태를 hurt로 설정
            self.frame_index = 0 # 인덱스 0으로 설정
            self.hp -= damage # hp를 데미지만큼 차감
            
            #hp가 0보다 낮으면 death() 함수 실행
            if self.hp <=0:
                self.death()

    def death(self): ## 죽었을 때 함수
        self.status = 'death' # 상태를 death로 설정
        self.frame_index = 0 # 인덱스 초기화

    def attack(self): ## 공격 함수
        if self.type == 'worrior': # worrior라면
                # 감지 반경 설정
                detection_radius = 1 
                deteciton_rect = pygame.Rect(self.rect.center[0] - (64*detection_radius)/2,self.rect.center[1] - (64*detection_radius)/2, 64*detection_radius, 64*detection_radius)
                
                # 플레이어가 감지 반경에 들어오지 않고 인덱스가 3 미만이면 움직임
                if not deteciton_rect.colliderect(self.player) and self.frame_index<3:
                    if self.rect.x < self.player.rect.x: # is_player_on_right
                        self.speed = abs(self.speed)
                    else:
                        self.speed = -abs(self.speed)
                    self.move()

                # 인덱스가 6~6.9면 공격 히트박스 그리기
                elif int(self.frame_index)==6:
                    if self.speed>0:
                        rect = pygame.rect.Rect(self.rect.right, self.rect.top, self.rect.width*1.2, self.rect.height)
                    else:
                        rect = pygame.rect.Rect(self.rect.left-self.rect.width*1.2, self.rect.top, self.rect.width*1.2, self.rect.height)
                    
                    # pygame.draw.rect(self.display_surface, (255, 255, 0), rect) # 공격 히트박스 디스플레이
                    
        else: #mage
            fireball = Fireball(self.display_surface, self.rect.centerx-16, self.rect.centery-16, self.player, self.last_player_x, self.last_player_y+16)
            self.fireball_sprites.add(fireball)

    def animate(self): ## 애니메이션 함수
        animation = self.animations[self.status] # 현재 상태의 애니메이션 불러오기
        self.frame_index += 0.15 # 인덱스 값 증가

        # 애니메이션 끝났을 때
        if self.frame_index >= len(animation):
            self.frame_index = 0 # 인덱스 초기화
            if self.status == 'hurt': self.status = 'walk' # 다쳤던 상태면 걷기로 변경
            elif self.status == 'death': self.kill() # 죽었으면 스프라이트 kill
            elif self.status == 'idle': self.detect_level = 2 # 걷기 상태면 감지 레벨을 2로 설정
            elif self.status == 'attack': self.status = 'walk' # 공격 상태면 걷기 상태로 변경

        #animate
        image = animation[int(self.frame_index)]

        # act
        if self.status == 'walk': self.move()
        elif self.status == 'idle': self.draw_bang()
        elif self.status == 'attack':
            if self.type == 'worrior': self.attack()
            else: #mage
                if self.frame_index == 9.450000000000012:
                    self.attack()

        # animate
        is_player_on_right = self.rect.x < self.player.rect.x
        if self.status == 'walk':
            if self.detect_level == 2:
                self.facing_right = True if is_player_on_right else False
            else:
                self.facing_right = True if self.speed > 0 else False
        elif (self.status == 'hurt' or self.status == 'idle') and not is_player_on_right:
            self.facing_right = False
        elif (self.status == 'attack'):
            if (self.type=='worrior' and self.speed < 0):
                self.facing_right = False
            elif self.type=='mage' and self.frame_index<5:
                if is_player_on_right:
                    self.facing_right = True
                else: self.facing_right = False

                self.last_player_x = self.player.rect.x
                self.last_player_y = self.player.rect.y

            elif self.type=='mage' and self.frame_index>=3: pass
            else: self.facing_right = True
        else: self.facing_right = True

        if not self.facing_right:
            image = pygame.transform.flip(image, not self.facing_right, False)
            self.display_surface.blit(image, (self.rect.topleft[0]-40, self.rect.topleft[1]-22))
        else:
            self.display_surface.blit(image, (self.rect.topleft[0]-22.5, self.rect.topleft[1]-22))

    def detect_player(self):
        if self.status != 'hurt' and self.status != 'death' and self.status != 'attack':
            detection_radius = 7
            if self.type == 'mage':
                deteciton_rect = pygame.Rect(self.rect.center[0] - (64*detection_radius)/2,self.rect.center[1] - (64*detection_radius)/2, 64*detection_radius, 64*detection_radius)
            else:
                deteciton_rect = pygame.Rect(self.rect.center[0] - (64*detection_radius+2)/2,self.rect.top-self.rect.height*2, 64*detection_radius, self.rect.height*3)
                
            if deteciton_rect.colliderect(self.player):
                if self.detect_level == 0: 
                    self.status = 'idle'
                    self.detect_level = 1
                elif self.detect_level == 2:
                    self.status = 'attack'
            else:
                self.detect_level = 0
                self.status = 'walk'
            # pygame.draw.rect(self.display_surface, (0, 255, 0), deteciton_rect)

    def reverse(self):
        self.speed *= -1

    def get_attackbox(self):
        attackBox = self.player.attack_hitbox
        if attackBox != None and attackBox.colliderect(self.rect):
            self.hurt(1)

    def draw_bang(self):
        self.bang_index += 0.1

        # when animation ended
        if self.bang_index >= len(self.bang_animations):
            self.bang_index = 0

        image = self.bang_animations[int(self.bang_index)]
        self.display_surface.blit(image, (self.rect.centerx-image.get_width()/2 , self.rect.centery-64*1.2))

    def update(self, x_shift):
        self.rect.x += x_shift
        self.get_attackbox()
        self.detect_player()
        self.animate()
        if self.type == 'mage':
            self.fireball_sprites.update(x_shift)
