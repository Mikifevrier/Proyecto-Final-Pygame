import pygame
import random
from pygame import mixer
from pygame import sprite

from pygame.constants import *

FPS = 60
ANCHO = 800
ALTO = 600
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)


# Inicio del juego y crear la pantalla
pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Space Trooper Adventure")
clock = pygame.time.Clock()
pygame.mixer.music.load("audio/metroid.wav")
pygame.mixer.music.set_volume(0.2)

#Por ahora voy a dejar el marcador muy normalito
class Marcador(pygame.sprite.Sprite):
    def __init__(self, x, y, fontsize=40, color=BLANCO):
        super().__init__()
        self.fuente = pygame.font.SysFont("Namco", fontsize)
        self.texto = 0
        self.color = color
        self.image = self.fuente.render(str(self.texto), True, self.color)
        self.rect = self.image.get_rect()
    
    def update(self):
        self.image = self.fuente.render(str(self.texto), True, self.color)

# El jugador que controla la nave
class Nave(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("images/nave.png").convert()
        self.image = pygame.transform.scale(self.image, (50, 60))
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

#Los meteoritos
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
            marcador.texto += 1

# Fondo de la pantalla 
fondo = pygame.image.load("images/fondo.jpg").convert()
#Hacer que el fondo sea dinámico si me da tiempo (estrellitas brillando, que se mueva, ¿que haga cosas chulas?)

# Incluir los objetos en el Group
grupoSprites = pygame.sprite.Group()
roca_list = pygame.sprite.Group()
for i in range(15):
    roca = Roca()
    grupoSprites.add(roca)
    roca_list.add(roca)

nave = Nave()
grupoSprites.add(nave)

marcador = Marcador(10, 10)
grupoSprites.add(marcador)

pygame.mixer.music.play(loops=-1)

# Bucle Principal
running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False
    
    grupoSprites.update()

# Si hay una colisión
    colision = pygame.sprite.spritecollide(nave, roca_list, True)
    if colision:
        running = False

# Blit, Draw, Displays
    pantalla.blit(fondo, [0, 0])

    grupoSprites.draw(pantalla)

    pygame.display.flip()

pygame.quit()