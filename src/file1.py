import os
import pygame
import time

# Cambia el directorio de trabajo al del script actual
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Iniciar Pygame
pygame.init()

# crear ventana
screen = pygame.display.set_mode((1200, 700))
pygame.display.set_caption("El veloz")

# Cargar imágenes
fondo = pygame.image.load("../sprites/sprite_fondo.jpg")
fondo = pygame.transform.scale(fondo, (1200, 700))
sprite_sonic = pygame.image.load("../sprites/sonic.png")
sprite_sonic = pygame.transform.scale(sprite_sonic, (120, 120))

# Definir personaje
sonic = pygame.Rect(100, 550, 50, 50)

# Definir suelo
suelo = pygame.Rect(-10000, 560, 120000, 100)

# Variables de movimiento
vel_y = 0
gravedad = 2500
vel_salto = -1100
vel_lateral = 1000
en_suelo = False

# Variable de cámara
camera_x = 0

clock = pygame.time.Clock()

# Bucle principal del juego
running = True
last_time = time.time()
while running:
    now = time.time()
    dt = now - last_time
    last_time = now

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movimiento lateral
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        sonic.x -= int(vel_lateral * dt)
    if keys[pygame.K_d]:
        sonic.x += int(vel_lateral * dt)

    # Saltar
    if keys[pygame.K_w] and en_suelo:
        vel_y = vel_salto

    # Aplicar gravedad
    vel_y += gravedad * dt
    sonic.y += vel_y * dt

    # Colisión con el suelo (siempre que esté tocando el suelo)
    if sonic.colliderect(suelo):
        if vel_y > 0:
            sonic.y = suelo.y - sonic.height
            vel_y = 0
        en_suelo = True
    else:
        en_suelo = False

    # Actualizar cámara para centrar a Sonic
    camera_x = sonic.x - 600

    # Dibujo de fondo infinito
    fondo_width = fondo.get_width()
    fondo_x = -camera_x % fondo_width
    screen.blit(fondo, (fondo_x, 0))
    screen.blit(fondo, (fondo_x - fondo_width, 0))

    # Suelo y Sonic desplazados por la cámara
    suelo_draw = suelo.move(-camera_x, 0)
    # pygame.draw.rect(screen, (0, 0, 0), suelo_draw)
    screen.blit(sprite_sonic, (sonic.x - camera_x, sonic.y))
    pygame.display.flip()

pygame.quit()

