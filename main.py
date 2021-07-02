import pygame
import random
from pygame import mixer
from pygame import sprite
import sys, os
import time, datetime

from pygame.constants import *

FPS = 60
ANCHO = 800
ALTO = 600
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
VIDAS_INICIALES = 5
TIEMPO_NIVEL_1 = 10
TIEMPO_NIVEL_2 = 10

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

class Texto(pygame.sprite.Sprite):  #Clase texto para usar aparte
    palabras = "{}"

    def __init__(self, x, y, t, justificado = "topright", fontsize=20, color=BLANCO):
        super().__init__()
        self.x = x
        self.y = y
        self.palabras = t
        self.fuente = pygame.font.SysFont("Namco", fontsize)
        self.color = color
        self.justificado = justificado
        self.image = self.fuente.render(self.palabras, True, self.color)
        d = {self.justificado: (self.x, self.y)}
        self.rect = self.image.get_rect(**d)

    def update(self):
        self.image = self.fuente.render(self.palabras, True, self.color)

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
        self.vidas = VIDAS_INICIALES

    def update(self):
        self.vy = 0
        tecla = pygame.key.get_pressed()
        if tecla[pygame.K_UP]:
            self.vy = -7
        if tecla[pygame.K_DOWN]:
            self.vy = 7
        self.rect.y += self.vy
        if self.rect.top < 25:
            self.rect.top = 25
        if self.rect.bottom > ALTO - 25:
            self.rect.bottom = ALTO - 25
    
    def reseteaVidas(self):
        self.vidas = VIDAS_INICIALES

#Los meteoritos
class Roca(pygame.sprite.Sprite):
    imagenes_roca = []

    def __init__(self):
        super().__init__()
        self.images = []
        for num in range(0, 9):
            img = pygame.image.load(f"images/small/a1000{num}.png")
            self.images.append(img)
        indice = random.randint(0, len(self.images) - 1)
        self.image = self.images[indice]
        self.image.set_colorkey(NEGRO)
        self.rect = self.image.get_rect()
        self.contador = indice

        self.reseteaRoca()
        #self.marcador = marcador

    
    def update(self):
        self.rect.x -= self.vx
        #self.image = pygame.transform.rotate(self.image, 15)  #Rotar rocas pero no funciona (preguntar a Ramón)
        if self.rect.right < 0:
            self.resetearRoca()
            #Eliminar las rocas que pasan la pantalla y que vuelvan a generarse en un lugar random
        
        ####Animacion       
        self.contador += 1

        if self.contador == len(self.images):
            self.contador = 0
        
        if self.contador % 2 == 0:
            self.image = self.images[self.contador]

    def reseteaRoca(self):  #Resetea la posicion de la roca
        self.rect.x = random.randrange(ANCHO + self.rect.width, ANCHO + self.rect.width + 30)
        self.rect.y = random.randrange(self.rect.height, ALTO - self.rect.height)
        self.vx = random.randrange(2, 8)

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

        self.muestraExplosion = False #Probatina para mostrarla o no

    def update(self):
        v_explosion = 3
        self.contador += 1
        if self.contador >= v_explosion and self.index < len(self.images) - 1:
            self.contador = 0
            self.index +=1
            self.image = self.images[self.index]
        if self.index >= len(self.images) - 1 and self.contador >= v_explosion:
            self.muestraExplosion = False #No elimina la explosión, la escondemos. Solo creamos una, no varias. Solo aparece cuando la llame.

class Enemigo(pygame.sprite.Sprite):  
    def __init__(self, x, y, v):
        super().__init__()
        self.image = pygame.image.load("images/enemigo.png").convert()
        self.image.set_colorkey(NEGRO)
        self.image = pygame.transform.scale(self.image, (80, 95))
        self.image = pygame.transform.rotate(self.image, 90)
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

        self.direccion = 1
        self.vy = v

        self.minTiempoDisparo = 3
        self.maxTiempoDisparo = 5

        self.tiempoDisparo = 0

        self.contador = 0

        self.start_ticks_balas = pygame.time.get_ticks()
        self.balasArray = [None] * 5
        self.iniciaBalas()

    def update(self):
        self.movimiento()      
        #if self.tiempoPartida(self.tiempoDisparo):
            #Disaprar Bala
            #self.tiempoDisparo = random.randint(self.minTiempoDisparo, self.maxTiempoDisparo)
            #print("Dispara " + str(self.contador))
            #self.contador += 1
            #self.start_ticks_balas = pygame.time.get_ticks()
    
    def movimiento(self):
        if self.rect.top < 0:
            self.rect.top = 0
            self.direccion *= -1
        if self.rect.bottom > ALTO:
            self.rect.bottom = ALTO
            self.direccion *= -1
        
        self.rect.y += self.vy * self.direccion

    def iniciaBalas(self):
        for i in range(5):
            self.balasArray[i] = Bala(self.rect.x, random.randint(0, ALTO), 10)
            #print("Bala creada")

    def impacto(self, nave):
        for i in range(5):
            if pygame.sprite.collide_rect(nave, self.balasArray[i]):
                self.balasArray[i].viva = False
                self.balasArray[i].rect.x = ANCHO + self.balasArray[i].rect.width
                nave.vidas -= 1

    def tiempoPartida(self, tiempo):            # Utiliza el tiempo, ver si pasa o no
        seconds = tiempo - (pygame.time.get_ticks() - self.start_ticks_balas)/1000 #para los segundos que pasa
        if seconds <= 0: 
            self.start_ticks_balas = pygame.time.get_ticks()
            return True
            
        else:
            return False
    
class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y, v):
        super().__init__()
        self.image = pygame.image.load("images/bala.png").convert()
        self.image.set_colorkey(NEGRO)
        self.image = pygame.transform.scale(self.image, (80, 55))
        self.image = pygame.transform.rotate(self.image, 180)
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

        self.vx = v

        self.viva = True

    def update(self):
        if self.viva:
            self.movimiento()

    def movimiento(self):
        self.rect.x -= self.vx
        if self.rect.right < 0:         
            pygame.sprite.Sprite.kill(self)

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
        
        self.indicePantalla = 0
        self.botonSoltado = False

        self.grupoSpritesMenu = pygame.sprite.Group()
        self.grupoSpritesGameOver = pygame.sprite.Group()
        self.roca_list = [None] * 20

        self.puedeJugar = False
        self.reseterTiempoJuego = False

        #Menu
        self.textoMenu = Texto(ANCHO/2, ALTO/2, "Bienvenido", "center", 200)
        self.grupoSpritesMenu.add(self.textoMenu)

        #Juego
        self.indice_Nivel = 1

        #self.bala = Bala(ANCHO/2, ALTO/2, 10)
        self.enemigo = Enemigo(ANCHO/4 * 3, ALTO/2, 4)

        self.marcador_puntos = Marcador(10,10, "topleft", fontsize = 35, color = (255, 0, 255))
        self.marcador_puntos.palabras = "Puntos: {}"

        self.marcador_vidas = Marcador(790, 10, "topright", fontsize = 35)
        self.marcador_vidas.palabras = "Vidas: {}"

        self.textoTiempo = Texto(ANCHO/2, 25, "00" ,"center", 45)

        self.textoNivel = Texto(ANCHO/2, ALTO/2, "Nivel " + str(self.indice_Nivel), "center", 45)
        
        for i in range(20):
            self.roca_list[i] = Roca()
        
        self.nave = Nave()
        self.nave.reseteaVidas()

        self.explosion = Explosion(self.nave.rect.centerx, self.nave.rect.centery, 2)

        #Game Over
        self.textoGameOver = Texto(ANCHO/2, ALTO/2, "GAME OVER" ,"center", 100)
        self.grupoSpritesGameOver.add(self.textoGameOver)

        #Temporizador
        self.start_ticks = pygame.time.get_ticks() #tick del inicio

    def mainloop(self):
        running = True
        while running:
            pantalla.fill(NEGRO) 
            dt = self.clock.tick(FPS)
            running = self.handleevent()
        
            if self.indicePantalla == 0: ### Pantalla Bienvenido
                
                tecla = pygame.key.get_pressed()
                if tecla[pygame.K_SPACE]:
                    self.indicePantalla = 1
                    self.reseteaJuego()
                
                self.mueveFondo()

                self.grupoSpritesMenu.draw(self.pantalla)

                pygame.display.flip()
                self.grupoSpritesMenu.update()
        
            elif self.indicePantalla == 1: ### Pantalla 1
                # Si hay una colisión
                if self.reseterTiempoJuego:
                    self.start_ticks = pygame.time.get_ticks()
                    self.reseterTiempoJuego = False

                if self.puedeJugar:
                    for roca in self.roca_list:    
                        self.sumarPunto(roca, self.marcador_puntos) #Alomejor sumamos un punto
                        colision1 = pygame.sprite.collide_rect(self.nave, roca)
                        if colision1:
                            self.explosion = Explosion(self.nave.rect.centerx, self.nave.rect.centery, 2) #voy a dejar el tamaño grande por el momento
                            self.explosion.muestraExplosion = True  #Arreglo de la explosión
                            boom.play()
                            self.nave.vidas -= 1

                            roca.reseteaRoca()

                            if self.nave.vidas == 0:
                                self.indicePantalla = 3
                                self.puedeJugar = False
                        self.marcador_vidas.contador = self.nave.vidas
                    self.enemigo.impacto(self.nave)
                else:
                    if self.tiempoPartida(3):
                        self.puedeJugar = True
                        self.reseterTiempoJuego = True

                self.mueveFondo()
                self.updateGame()

            
            elif self.indicePantalla == 2: ### Pantalla 2
                if self.reseterTiempoJuego:
                    self.start_ticks = pygame.time.get_ticks()
                    self.nave.vidas = self.marcador_vidas.contador
                    self.reseterTiempoJuego = False

                if self.puedeJugar:
                    for roca in self.roca_list:    
                        self.sumarPunto(roca, self.marcador_puntos)
                        colision = pygame.sprite.collide_rect(self.nave, roca)
                        if colision:
                            self.explosion = Explosion(self.nave.rect.centerx, self.nave.rect.centery, 2)
                            self.explosion.muestraExplosion = True
                            boom.play()
                            self.nave.vidas -= 1

                            roca.reseteaRoca()

                            if self.nave.vidas == 0:
                                self.indicePantalla = 3   
                                self.puedeJugar = False
                        self.marcador_vidas.contador = self.nave.vidas                   
                else:
                    if self.tiempoPartida(3):
                        self.puedeJugar = True
                        self.reseterTiempoJuego = True
                        #self.start_ticks = pygame.time.get_ticks()

                self.mueveFondo()
                self.updateGame()

            elif self.indicePantalla == 3: # GameOver
                
                if self.botonSoltado:
                    self.indicePantalla = 0                   

                self.grupoSpritesGameOver.draw(self.pantalla)

                pygame.display.flip()
                self.grupoSpritesGameOver.update()
        
        self.game_over()

    def handleevent(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                return False
            if event.type == KEYUP and event.key == K_SPACE:
                self.botonSoltado = True
            else:
                self.botonSoltado = False
        return True

    def game_over(self):
        pygame.quit()
        sys.exit()

    def resetearRocas(self):
        for i in range(20):
            self.roca_list[i].reseteaRoca()

    def sumarPunto(self, roca, marcador): #Arreglo para los puntos
        if(roca.rect.x < -roca.rect.width/2):
            marcador.contador += 1
            roca.reseteaRoca()
    
    def updateGame(self):
        grupoSpritesJuego = pygame.sprite.Group()
        
        if self.puedeJugar:
            grupoSpritesJuego.add(self.marcador_vidas)
            grupoSpritesJuego.add(self.marcador_puntos)
            grupoSpritesJuego.add(self.textoTiempo)
        else:
            grupoSpritesJuego.add(self.textoNivel)
        grupoSpritesJuego.add(self.nave)

        if self.explosion.muestraExplosion:   #Arreglo en la explosión
            grupoSpritesJuego.add(self.explosion)

        for i in range(20):
            grupoSpritesJuego.add(self.roca_list[i])
        
        if self.indicePantalla == 2:
            grupoSpritesJuego.add(self.enemigo)        
            for i in range(5):
                grupoSpritesJuego.add(self.enemigo.balasArray[i])

        grupoSpritesJuego.draw(self.pantalla)
        pygame.display.flip()

        if self.puedeJugar:
            if self.indicePantalla == 1:
                if self.tiempoPartida(TIEMPO_NIVEL_1):
                    self.indicePantalla += 1
                    self.indice_Nivel += 1
                    self.textoNivel = Texto(ANCHO/2, ALTO/2, "Nivel " + str(self.indice_Nivel), "center", 45)
                    self.puedeJugar = False
                    self.siguienteNivel()
            elif self.indicePantalla == 2:
                if self.tiempoPartida(TIEMPO_NIVEL_2):
                    self.indicePantalla = 0
                    self.indice_Nivel = 0

            grupoSpritesJuego.update()

    def reseteaJuego(self):
        self.resetearRocas()
        self.marcador_puntos.contador = 0
        self.marcador_vidas.contador = VIDAS_INICIALES
        self.explosion.rect.x += ANCHO
        self.nave = Nave()
        self.nave.vidas = VIDAS_INICIALES
        self.start_ticks = pygame.time.get_ticks() #starter tick, truco muy bueno para contar tiempos
        self.indice_Nivel = 1
        self.textoNivel = Texto(ANCHO/2, ALTO/2, "Nivel " + str(self.indice_Nivel), "center", 45)
        self.puedeJugar = False

    def siguienteNivel(self):
        self.resetearRocas()
        self.explosion.rect.x += ANCHO
        self.nave = Nave()        
        self.enemigo = Enemigo(ANCHO/4 * 3, ALTO/2, 4)
        self.start_ticks = pygame.time.get_ticks() #tengo que pasarlo al llegar al siguiente nivel

    def mueveFondo(self):
        # Mueve la pantalla
        x_mueve = self.x % self.fondo.get_rect().width
        self.pantalla.blit(self.fondo, [x_mueve - self.fondo.get_rect().width , 0])
        if x_mueve < ANCHO:
            self.pantalla.blit(self.fondo, (x_mueve, 0))
        self.x -= 1

    def tiempoPartida(self, tiempo):      # Funciona en generico, por lo que podemos pasarle cualquier tiempo, y nos devolvera si ese tiempo ha pasado o no
        seconds = tiempo - (pygame.time.get_ticks() - self.start_ticks)/1000 # Calcula cuántos segundos han pasado
        self.textoTiempo.palabras = str(int(seconds))
        if seconds <= 0: 
            return True
        else:
            return False

if __name__ == "__main__":
    pygame.init()
    game = Game()
    game.mainloop()