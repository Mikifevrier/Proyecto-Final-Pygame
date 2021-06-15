import pygame
import random

from pygame.constants import *


ANCHO = 800
ALTO = 600
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Space Trooper Adventure")
clock = pygame.time.Clock()

class Nave(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("images/nave.png").convert()
        self.image.set_colorkey(NEGRO)
        self.rect = self.image.get_rect()
        self.rect.centerx = ANCHO - 750
        self.rect.bottom = ALTO // 2
        self.vy = 0

    def update(self):
        self.vy = 0
        tecla = pygame.key.get_pressed()
        if tecla[pygame.K_UP]:
            self.vy = -7
        if tecla[pygame.K_DOWN]:
            self.vy = 7
        self.rect.y += self.vy
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > ALTO:
            self.rect.bottom = ALTO

class Roca(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("images/asteroide.png").convert()
        self.image = pygame.transform.scale(self.image, (50, 60))
        self.image.set_colorkey(NEGRO)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(780, 800)
        self.rect.y = random.randrange(ALTO - self.rect.height)
        self.vx = random.randrange(1, 10)
    
    def update(self):
        self.rect.x -= self.vx
        if self.rect.right < 0:
            self.rect.x = random.randrange(780, 800)
            self.rect.y = random.randrange(ALTO - self.rect.height)
            self.vx = random.randrange(1, 10)

fondo = pygame.image.load("images/fondo.jpg").convert()

grupoSprites = pygame.sprite.Group()
roca_list = pygame.sprite.Group()
for i in range(20):
    roca = Roca()
    grupoSprites.add(roca)
    roca_list.add(roca)

nave = Nave()
grupoSprites.add(nave)

running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False
    
    grupoSprites.update()

    pantalla.blit(fondo, [0, 0])

    grupoSprites.draw(pantalla)

    pygame.display.flip()

pygame.quit()