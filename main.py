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

# Inicio del juego y creao la pantalla
pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Space Trooper Adventure")
clock = pygame.time.Clock()
pygame.mixer.init()
pygame.mixer.music.load("audio/metroid.wav")
boom = pygame.mixer.Sound("audio/explosion.wav")
boom.set_volume(0.1)
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(loops=-1)


#Por ahora voy a dejar el marcador muy normalito
class Marcador(pygame.sprite.Sprite):
    palabras = "{}"

    def __init__(self, x, y, justificado = "topright", fontsize=20, color=BLANCO):
        super().__init__()
        self.x = x
        self.y = y
        self.fuente = pygame.font.SysFont("Namco", fontsize)
        self.contador = 0
        self.color = color
        self.justificado = justificado
        self.image = self.fuente.render(str(self.contador), True, self.color)
    
    def update(self):
        self.image = self.fuente.render(str(self.palabras.format(self.contador)), True, self.color)
        d = {self.justificado: (self.x, self.y)}
        self.rect = self.image.get_rect(**d)

# El jugador que controla la nave
class Nave(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("images/nave.png").convert()
        self.image = pygame.transform.scale(self.image, (45, 55))
        self.image.set_colorkey(NEGRO)
        self.rect = self.image.get_rect()
        self.rect.centerx = ANCHO - 750
        self.rect.bottom = ALTO // 2
        self.vy = 0
        self.vidas = 5

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
    imagenes_roca = []
    imagenes_roca_lista = ["images/output-onlinepngtools2.png", "images/output-onlinepngtools3.png"]

    for i in imagenes_roca_lista:
        imagenes_roca.append(pygame.image.load(i).convert())

    def __init__(self):
        super().__init__()
        self.image = random.choice(self.imagenes_roca)
        self.image.set_colorkey(NEGRO)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(780, 800)
        self.rect.y = random.randrange(ALTO - self.rect.height)
        self.vx = random.randrange(2, 8)

    
    def update(self):
        self.rect.x -= self.vx
        if self.rect.right < 0:
            self.rect.x = random.randrange(780, 800)
            self.rect.y = random.randrange(ALTO - self.rect.height)
            self.vx = random.randrange(2, 8)
            marcador_puntos.contador += 1
            #Eliminar las rocas que pasan la pantalla y que vuelvan a generarse en un lugar random

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, tamaño):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f"images/exp{num}.png")
            # voy a darle tamaño a las explosiones
            if tamaño == 1:
                img = pygame.transform.scale(img, (40, 40))
            if tamaño == 2:
                img = pygame.transform.scale(img, (100, 100))
            self.images.append(img)

        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.contador = 0

    def update(self):
        v_explosion = 3
        self.contador += 1
        if self.contador >= v_explosion and self.index < len(self.images) - 1:
            self.contador = 0
            self.index +=1
            self.image = self.images[self.index]
        if self.index >= len(self.images) - 1 and self.contador >= v_explosion:
            self.kill()


# Fondo de la pantalla 
fondo = pygame.image.load("images/maxresdefault.jpg").convert()
x = 0
#Hacer que el fondo sea dinámico si me da tiempo (estrellitas brillando, que se mueva, ¿que haga cosas chulas?)

# Incluir los objetos en el Group
grupoSprites = pygame.sprite.Group()
roca_list = pygame.sprite.Group()
for i in range(20):
    roca = Roca()
    grupoSprites.add(roca)
    roca_list.add(roca)

nave = Nave()
grupoSprites.add(nave)

marcador_puntos = Marcador(10,10, "topleft", fontsize = 35, color = (255, 0, 255))
marcador_puntos.palabras = "Puntos: {}"
grupoSprites.add(marcador_puntos)

marcador_vidas = Marcador(790, 10, "topright", fontsize = 35)
marcador_vidas.palabras = "Vidas: {}"
grupoSprites.add(marcador_vidas)

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
        explosion = Explosion(nave.rect.centerx, nave.rect.centery, 2) #voy a dejar el tamaño grande por el momento
        grupoSprites.add(explosion)
        boom.play()
        nave.vidas -= 1
        if nave.vidas == 0:
            running = False
    marcador_vidas.contador = nave.vidas

# Blit, Draw, Displays
    x_mueve = x % fondo.get_rect().width
    pantalla.blit(fondo, [x_mueve - fondo.get_rect().width , 0])
    if x_mueve < ANCHO:
        pantalla.blit(fondo, (x_mueve, 0))
    x -= 1

    grupoSprites.draw(pantalla)

    pygame.display.flip()

pygame.quit()