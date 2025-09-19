import pygame

# Iniciar Pygame
pygame.init()

# crear ventana
screen = pygame.display.set_mode((1200, 700))
pygame.display.set_caption("Sonic 90s")

# Cargar imágenes
fondo = pygame.image.load("sprites/sprite_fondo.jpg")
fondo = pygame.transform.scale(fondo, (1200, 700))
sprite_sonic = pygame.image.load("sprites/sonic.png")
sprite_sonic = pygame.transform.scale(sprite_sonic, (120, 120))

# Definir personaje
sonic = pygame.Rect(100, 100, 50, 50)

# Definir suelo
suelo = pygame.Rect(-10000, 560, 120000, 1)

# Variables de movimiento
vel_y = 0.2
gravedad = 0.2
en_suelo = False

# Variable de cámara
camera_x = 0

# Bucle principal del juego
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movimiento lateral
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        sonic.x -= 3
    if keys[pygame.K_d]:
        sonic.x += 3

    # Saltar
    if keys[pygame.K_w] and en_suelo:
        vel_y = -7  # salto

    # Aplicar gravedad
    vel_y += gravedad
    sonic.y += vel_y

    # Colisión con el suelo
    if sonic.colliderect(suelo):
        sonic.y = suelo.y - sonic.height
        vel_y = 0
        en_suelo = True
    else:
        en_suelo = False

    # Actualizar cámara para centrar a Sonic
    camera_x = sonic.x - 600  # 600 es la mitad del ancho de la pantalla

    # Dibujo de fondo infinito
    fondo_width = fondo.get_width()
    fondo_x = -camera_x % fondo_width
    screen.blit(fondo, (fondo_x, 0))
    screen.blit(fondo, (fondo_x - fondo_width, 0))
    screen.blit(fondo, (fondo_x + fondo_width, 0))

    # Suelo y Sonic desplazados por la cámara
    suelo_draw = suelo.move(-camera_x, 0)
    pygame.draw.rect(screen, (0, 0, 0), suelo_draw)
    screen.blit(sprite_sonic, (sonic.x - camera_x, sonic.y))

    pygame.display.flip()

pygame.quit()

