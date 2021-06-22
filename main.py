import pygame
import random
from pygame import mixer
from pygame import sprite
import sys, os

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

fondo = pygame.image.load("images/maxresdefault.jpg").convert()
x = 0

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
        self.rect = self.image.get_rect()

    
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

    def __init__(self, marcador):
        super().__init__()
        self.image = random.choice(self.imagenes_roca)
        self.image.set_colorkey(NEGRO)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(780, 800)
        self.rect.y = random.randrange(ALTO - self.rect.height)
        self.vx = random.randrange(2, 8)
        self.marcador = marcador

    
    def update(self):
        self.rect.x -= self.vx
        if self.rect.right < 0:
            self.rect.x = random.randrange(780, 800)
            self.rect.y = random.randrange(ALTO - self.rect.height)
            self.vx = random.randrange(2, 8)
            self.marcador.contador += 1
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

class Game():
    clock = pygame.time.Clock()

    def __init__(self):
        self.display = pygame.display
        self.pantalla = self.display.set_mode((ANCHO, ALTO))
        self.w = ANCHO
        self.h = ALTO
        self.x = 0
        self.display.set_caption("Space Trooper Adventure")
        self.fondo = pygame.image.load("images/maxresdefault.jpg").convert()
        self.grupoSprites = pygame.sprite.Group()
        self.roca_list = pygame.sprite.Group()
        
        self.marcador_puntos = Marcador(10,10, "topleft", fontsize = 35, color = (255, 0, 255))
        self.marcador_puntos.palabras = "Puntos: {}"
        self.grupoSprites.add(self.marcador_puntos)

        self.marcador_vidas = Marcador(790, 10, "topright", fontsize = 35)
        self.marcador_vidas.palabras = "Vidas: {}"
        self.grupoSprites.add(self.marcador_vidas)
        
        for i in range(20):
            self.roca = Roca(self.marcador_puntos)
            self.grupoSprites.add(self.roca)
            self.roca_list.add(self.roca)
        
        self.nave = Nave()
        self.grupoSprites.add(self.nave)

    def mainloop(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            running = self.handleevent()
        
        # Si hay una colisión
            colision = pygame.sprite.spritecollide(self.nave, self.roca_list, True)
            if colision:
                self.explosion = Explosion(self.nave.rect.centerx, self.nave.rect.centery, 2) #voy a dejar el tamaño grande por el momento
                self.grupoSprites.add(self.explosion)
                boom.play()
                self.nave.vidas -= 1
                if self.nave.vidas == 0:
                    running = False
            self.marcador_vidas.contador = self.nave.vidas
            
            # Mueve la pantalla
            x_mueve = self.x % self.fondo.get_rect().width
            self.pantalla.blit(self.fondo, [x_mueve - self.fondo.get_rect().width , 0])
            if x_mueve < ANCHO:
                self.pantalla.blit(self.fondo, (x_mueve, 0))
            self.x -= 1
            
            self.grupoSprites.draw(self.pantalla)

            pygame.display.flip()
            self.grupoSprites.update()
        
        self.game_over()

    def handleevent(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                return False
        return True

    def game_over(self):
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    pygame.init()
    game = Game()
    game.mainloop()