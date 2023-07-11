import pygame
from support import import_folder

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, surface, create_jump_particles): ##기초값 설정
        super().__init__()
        self.import_character_assets() # 캐릭터 모델 불러오기
        self.frame_index = 0 # 애니메이션 프레임 설정
        self.animation_speed = 0.15 #애니메이션 속도
        self.image = pygame.Surface((32, 64)) # 플레이어 히트박스 이미지
        self.image.set_alpha(0) # 히트박스 투명하게
        self.rect = self.image.get_rect(topleft=pos) #히트박스 이미지에서 히트박스 가져오기

        self.there_image = pygame.image.load(r'assets\character\there.png') # 플레이어 맵 나갔을 때 화살표 이미지 불러오기
        self.there_image = pygame.transform.scale(self.there_image, (64, 64)).convert_alpha() # 64x64 사이즈로 조정

        # dust particles
        self.import_dust_run_particles() # 더스트 파티클 불러오기
        self.dust_frame_index = 0 #  더스트 애니메이션 프레임 설정
        self.dust_animation_speed = 0.15 # 더스트 애니메이션 속도
        self.create_jump_particles = create_jump_particles # 점프 파티클 제작 
        
        # surface
        self.display_surface = surface # 디스플레이 스크린 설정

        # player movement
        self.direction = pygame.math.Vector2(0, 0) # 벡터값 설정
        self.orign_speed = 8 # 플레이어 static 속도
        self.speed = self.orign_speed # 플레이어 variable 속도
        self.gravity = 0.98 # 중력값 설정
        self.jump_speed = -16.5 # 점프 높이(벡터) 설정

        # player status
        self.hp = 3 # 체력 설정
        self.status = 'idle' # 상태를 idle로 설정
        self.attack_status: str = 'ground' # 공격 상태를 ground로 설정

        # True || False
        self.facing_right = True # 오른쪽 보는지 확인
        self.crouched = False # 숙이고 있는지 확인
        self.isJumpChanged = False # 점프모션 바꼈는지 확인
        self.on_ground = False # 땅에 서있는지 확인
        self.on_ceiling = False # 천장에 닿았는지 확인
        self.on_left = False # 왼쪽 벽에 닿았는지 확인
        self.on_right = False # 오른쪽 벽에 닿았는지 확인
        self.jumpable = 0 # 공중 점프 가능 여부 / 0: 불가능, 1: 가능, 2: 이미 점프함 

        # attack
        self.attack_type = 0 # 공격 유형 설정 / maximum = 3
        self.attacking = False # 공격 중인지 확인
        self.attack_hitbox = None # 공격 히트박스 설정
        
        #skill attack
        self.skill_attacking = False # 스킬공격 중인지 확인
        #self.skill_attack_hitbox = None

    def import_character_assets(self): ## 캐릭터 모델 로드 함수
        character_path = './assets/character/BattleImages/' # 캐릭터 경로설정
        self.animations = {'attack1':[],'attack2':[],'attack3':[],'crouch':[],
                           'crouch_attack':[],'dash':[],'death':[],'fast_magic':[],
                           'idle':[], 'jump_forward':[],'jump_natural':[],
                           'running':[], 'stop':[],'sustain_magic':[], 'fall':[]} # 캐릭터 애니메이션 종류 설정
        
        # self.animations 딕셔너리에 각 애니메이션 별 이미지 저장
        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def import_dust_run_particles(self): ## 더스트 파티클 로드 함수
        self.dust_run_particles = import_folder('./assets/character/BattleImages/dust_particles/run') # 더스트 파티클 리스트에 이미지 불러오기

    def animate(self): ## 애니메이션 함수
        animation = self.animations[self.status] # 현재 상태의 애니메이션 리스트 불러오기

        # 애니메이션 속도 설정
        if self.status == 'running' or self.attacking==True: self.animation_speed=0.3
        else: self.animation_speed=0.15

        self.frame_index += self.animation_speed # 인덱스에 속도값 더하기

        # 공격 중일 때
        if self.attacking:
            if self.attack_status == 'crouch': # 공격 상태가 crouch면
                if int(self.frame_index)<3:
                    self.create_attackbox() # 인덱스가 3 미만일 때 공격 히트박스 그리기
            elif self.attack_type == 1 or self.attack_type == 2: # 공격 유형이 1 or 2면
                if int(self.frame_index)==3 or int(self.frame_index)==4:
                    self.create_attackbox() # 인덱스가 3~4.9일때 공격 히트박스 그리기
            elif self.attack_type == 3: # 공격 유형이 3이면
                if int(self.frame_index)==4 or int(self.frame_index)==5:
                    self.create_attackbox() # 인덱스가 4~5.9일때 히트박스 그리기

        # 스킬 공격 중일 때
        elif self.skill_attacking: 
            pass 

        # 애니메이션이 종료됐을 때
        if self.frame_index >= len(animation):
            # 특정 상태는 애니메이션 종료 후 모션 유지
            if self.status in ['jump_natural','fall_natural','jump_forward','fall', 'crouch']:
                self.frame_index = len(animation)-1
            
            #공격중이면
            elif self.attacking:
                    if self.attack_type == 3: self.attack_type = 0 # 공격 유형 3이면 0으로 초기화
                    self.attacking=False # 공격 끝남
                    self.frame_index = 0 # 인덱스 0으로 설정
                    if self.crouched: animation = self.animations['crouch'] # 숙인 상태면 그대로 유지
                    else: animation = self.animations['idle'] # 아니면 기본 상태로 설정
            
            # 스킬 공격 중이면
            elif self.skill_attacking:
                self.skill_attacking = False # 스킬공격 끝남
                self.frame_index = 0 # 인덱스 0으로 설정
                animation = self.animations['idle'] # 기본 상태로 설정
            
            else: 
                self.frame_index = 0 # 전부 아니면 인덱스만 초기화

        image = animation[int(self.frame_index)] # 애니메이션의 인덱스 순서를 이미지로 가져오기

        # 우측 보고있으면 그대로, 좌측 보고있으면 반전해서 이미지 blit
        if self.facing_right:
            self.display_surface.blit(image, (self.rect.topleft[0]-39, self.rect.topleft[1]-32))
        else:
            flipped_image = pygame.transform.flip(image,True,False)
            self.display_surface.blit(flipped_image, (self.rect.topleft[0]-39, self.rect.topleft[1]-32))

    def run_dust_animation(self): ## 더스트 애니메이션 함수
        if self.status == 'running' and self.on_ground: # 걷는 중이고 땅에 있으면
            # 애니메이션 반복하기
            self.dust_frame_index += self.dust_animation_speed # 인덱스에 애니메이션 속도 더하기
            if self.dust_frame_index >= len(self.dust_run_particles): # 인덱스가 오버되면
                self.dust_frame_index = 0 # 인덱스를 다시 0으로

            dust_particle = self.dust_run_particles[int(self.dust_frame_index)] # 더스트 파티클의 특정 인덱스값 불러오기

            # 더스트 파티클 blit (스크린에 디스플레이)
            if self.facing_right:
                pos = self.rect.bottomleft - pygame.math.Vector2(6, 10)
                self.display_surface.blit(dust_particle, pos)
            else:
                pos = self.rect.bottomright - pygame.math.Vector2(6, 10)
                flipped_dust_particle = pygame.transform.flip(dust_particle, True, False)
                self.display_surface.blit(flipped_dust_particle, pos)

    def get_status(self): ## 플레이어 상태 받아오는 함수
        x = self.direction.x
        y = self.direction.y

        if y < -1 and x==0: # 제자리에서 점프하면
            if not self.isJumpChanged: # 점프 모션이 안바꼈으면
                self.status = 'jump_natural'
        elif y < -1 and x!=0: # 움직이면서 점프하면
            self.status = 'jump_forward'
            self.isJumpChanged = True # 점프 모션 변경여부 설정
        elif y > 3: # 떨어지는 중이면
            self.status = 'fall' 
            self.isJumpChanged = False # 점프 모션 변경여부 설정
        else:
            if self.direction.x != 0: # 움직이는 중이면
                self.status = 'running'
            else: # 가만히 있으면
                self.status = 'idle'

        if self.crouched: # 숙이고 있으면
            self.status = 'crouch'

        # 공격중이면 공격 상태에 따라 플레이어 상태 설정
        if self.attacking:
            if self.attack_status == 'ground':
                self.direction.x = 0
            if self.attack_status == 'crouch':
                self.status = 'crouch_attack'
            else: self.status = f'attack{self.attack_type}'

        elif self.skill_attacking: # 스킬 공격 중이면
            self.status = 'sustain_magic'

    def get_input(self): ## 키보드 입력 받아오는 함수
        keys = pygame.key.get_pressed() # 키보드 입력값
        mouse = pygame.mouse.get_pressed() # 마우스 입력값
        
        if keys[pygame.K_SPACE]: # 스페이스
            if not self.crouched and not self.skill_attacking: # 숙이거나 스킬공격하지 않으면
                # 공중 점프 여부 체크하면서 점프
                if self.on_ground: 
                    self.jump()
                elif self.jumpable==1:
                    self.jump()
                    self.jumpable = 2

        # 스페이스 뗐을 때 공중 점프 여부 설정
        else:
            if self.on_ground:
                self.jumpable = 0
            if not self.on_ground and self.jumpable==0:
                self.jumpable = 1

        self.crouched = True if keys[pygame.K_s] else False # s 누르면 숙임
        
        # 땅에 있고 숙이거나 스킬 공격중이면 천천히 정지
        if self.crouched and self.on_ground or self.skill_attacking:
            self.stop_slowly()

        if keys[pygame.K_a]: # a 누르면
            if not self.crouched and not self.attacking and not self.skill_attacking: # 숙임, 공격, 스킬공격 모두 아니면
                # x벡터 -= 0.2
                if self.direction.x>-1:
                    self.direction.x-=0.2
                self.facing_right = False

        elif keys[pygame.K_d]: # d 누르면
            if not self.crouched and not self.attacking and not self.skill_attacking: # 숙임, 공격, 스킬공격 모두 아니면
                # x벡터 += 0.2
                if self.direction.x<1:
                    self.direction.x+=0.2
                self.facing_right = True

        # 아무 키보드도 안눌렀으면 정지
        else: self.stop_slowly()

        if mouse[0]: # 좌클릭
            if not self.attacking and not self.skill_attacking: # 공격 or 스킬공격 중이 아니면
                if not self.crouched: # 숙이지 않았으면
                    # attack type 설정
                    if (self.attack_type < 3):
                        self.attack_type += 1
                self.swip_attack() # 휘두르기 공격 함수 실행

        elif mouse[2]: # 우클릭
            if not self.attacking and not self.skill_attacking: # 공격 or 스킬공격 중이 아니면
                if not self.crouched: # 숙이지 않았으면
                    self.skill_attack() # 스킬 공격 함수 실행

    def apply_gravity(self): ## 중력 적용 함수
        self.direction.y += self.gravity # 플레이어 벡터 y에 중력 더하기
        self.rect.y += self.direction.y # 플레이어 박스에 벡터 y 더하기

    def jump(self): ## 점프 함수
        self.direction.y = self.jump_speed # y벡터를 점프값으로 설정
        self.create_jump_particles(self.rect.midbottom) # 점프 파티클 생성 (midbottom위치에)

    def hurt(self): ## 피해 입었을 때 함수
        self.hp -= 1 #hp 깎고
        if self.hp <= 0: #hp 0 이하면
            #플레이어 사망 이벤트
            print("player dead")

    def swip_attack(self): ## 스윕 공격 함수
        # 플레이어 상태에 따라 공격 상태 설정
        if self.crouched:
            self.attack_status = 'crouch'
        elif self.direction.y > 0.15:
            self.attack_status = 'fall'
            self.direction.y = 0
        elif self.direction.y < -0.15:
            self.attack_status = 'jump'
        else: 
            self.attack_status = 'ground'

        self.attacking=True # 공격 중으로 설정
        self.frame_index = 0 # 인덱스 초기화

    def skill_attack(self): ## 스킬 공격 함수
        self.skill_attacking = True # 스킬 공격 중으로 설정
        self.status = 'sustain_magic' # 상태를 sustain_magic으로 변경
        self.frame_index = 0 # 인덱스 초기화
        
    def create_attackbox(self): ## 공격 히트박스 제작 함수
        rect = self.rect # 기본 히트박스를 플레이어 히트박스로 설정
        dist = (rect)

        # 공격 상태에 따라 히트박스 위치 조정
        if self.attack_status == 'crouch':
            dist = (5, -5, 1.5, 0.6)
        elif self.attack_type==1:
            dist = (3, -45, 1.5, 1.2)
        elif self.attack_type==2:
            dist = (-10, -20, 2, 0.7)
        else: dist = (0, -70, 1.8, 1.5)

        # 히트박스 그리기
        if self.facing_right:
            if self.attack_status == 'ground': self.direction.x += 0.25
            attacking_rect = pygame.Rect(rect.center[0]+dist[0],rect.center[1]+dist[1],rect.width*dist[2],rect.height*dist[3])
        else:
            if self.attack_status == 'ground': self.direction.x -= 0.25
            attacking_rect = pygame.Rect(rect.center[0]-dist[0]-rect.width*dist[2], rect.center[1]+dist[1], rect.width*dist[2], rect.height*dist[3])

        self.attack_hitbox = attacking_rect # 히트박스 변수를 attacking_rect로 설정

        # pygame.draw.rect(self.display_surface, (0, 255 ,0), attacking_rect) # 히트박스 표시
    
    def stop_slowly(self): ## 정지 함수
        if self.direction.x>0.15: self.direction.x -= 0.2 # x벡터가 양수면 천천히 빼고
        elif self.direction.x<-0.15: self.direction.x += 0.2 # x벡터가 음수면 천천히 더해서
        else: self.direction.x = 0 #0에 수렴하면 0으로 설정
            
    def he_is_there(self): ## 플레이어 화살표 표시 함수
        if self.rect.y > 800: # 플레이어가 맵 아래로 떨어지면
            self.rect.y = -300 # 위로 올려보내기
            self.direction.y = 0 # y벡터 0으로 설정
        elif self.rect.y < -25: # 플레이어가 맵 위로 올라가서 안보이면
            self.display_surface.blit(self.there_image, (self.rect.x-10, 10 + (self.rect.y/10))) # 플레이어 x위치에 화살표 디스플레이

    def update(self): ## 업데이트 함수
        # 순서 중요 !
        self.attack_hitbox = None # 공격 히트박스 기본값 None 설정
        self.he_is_there()
        self.get_input()
        self.get_status()
        self.animate()
        self.run_dust_animation()