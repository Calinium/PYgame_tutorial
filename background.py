import pygame
from settings import screen_width, screen_height

class BackGround():
    def __init__(self) -> None:
        # 배경 레이어 3개 로드
        self.layer_1 = pygame.image.load(r'assets\map\terrain\background\background_layer_1.png').convert_alpha()
        self.layer_2 = pygame.image.load(r'assets\map\terrain\background\background_layer_2.png').convert_alpha()
        self.layer_3 = pygame.image.load(r'assets\map\terrain\background\background_layer_3.png').convert_alpha()

        # 스크린 크기만큼 확대
        self.layer_1 = pygame.transform.scale(self.layer_1, (screen_width,screen_height))
        self.layer_2 = pygame.transform.scale(self.layer_2, (screen_width,screen_height))
        self.layer_3 = pygame.transform.scale(self.layer_3, (screen_width,screen_height))

        # 너비값, x값 변수에 저장
        self.width = self.layer_1.get_width()
        self.x = -screen_width * 2

    def update_and_draw(self, surface, x_shift): ## 업데이트 + 디스플레이 함수
        self.x += x_shift # x_shift만큼 x값 더하고
        for i in range(5):
            # 각각 다른 수치만큼 x 방향으로 이동
            surface.blit(self.layer_1, (i * self.width + self.x*0.1, 0))
            surface.blit(self.layer_2, (i * self.width + self.x*0.2, 0))
            surface.blit(self.layer_3, (i * self.width + self.x*0.6, 0))
        