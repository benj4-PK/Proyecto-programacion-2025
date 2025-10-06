import os
import pygame
import time

# Cambia el directorio de trabajo al del script actual
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Iniciar Pygame
pygame.init()

fondo_day = pygame.image.load("../sprites/day.jpg")
fondo_day = pygame.transform.scale(fondo_day, (1200, 700))
fondo_day2 = pygame.image.load("../sprites/day(sinsol).jpg")
fondo_day2 = pygame.transform.scale(fondo_day2, (1200, 700))
fondo_midnight = pygame.image.load("../sprites/midnight.jpg")
fondo_midnight = pygame.transform.scale(fondo_midnight, (1200, 700))
fondo_midnight2 = pygame.image.load("../sprites/midnight(sinsol).jpg")
fondo_midnight2 = pygame.transform.scale(fondo_midnight2, (1200, 700))
fondo_seminight = pygame.image.load("../sprites/casinoche.jpg")
fondo_seminight = pygame.transform.scale(fondo_seminight, (1200, 700))
fondo_seminight2 = pygame.image.load("../sprites/casinoche(sinsol).jpg")
fondo_seminight2 = pygame.transform.scale(fondo_seminight2,(1200, 700))
fondo_night = pygame.image.load("../sprites/night.jpg")
fondo_night = pygame.transform.scale(fondo_night, (1200, 700))
fondo_night2 = pygame.image.load("../sprites/night(sinmoon).jpg")
fondo_night2 = pygame.transform.scale(fondo_night2, (1200, 700))

# crear ventana
screen = pygame.display.set_mode((1200, 700))
pygame.display.set_caption("El veloz")

# Cargar imágenes
fondo = pygame.image.load("../sprites/sprite_fondo.jpg")
fondo = pygame.transform.scale(fondo, (1200, 700))
sprite_sonic = pygame.image.load("../sprites/sonic.png")
sprite_sonic = pygame.transform.scale(sprite_sonic, (120, 120))

# Cargar imagen "eu_bata"
sprite_eu_bata = pygame.image.load("../sprites/eu_bata.png")
sprite_eu_bata = pygame.transform.scale(sprite_eu_bata, (400, 120))

# Definir personaje
sonic = pygame.Rect(-599, 250 - 50, 50, 50)  # Sonic aparece en x = -599

# Definir suelo
suelo = pygame.Rect(-10000, 280, 120000, 100)  # Suelo centrado verticalmente


# Variables de movimiento
vel_y = 0
gravedad = 2500
vel_salto = -1100
vel_lateral = 1400
en_suelo = False

# Variable de cámara
camera_x = 0
mostrar_bata = False
tiempo_bata = 0
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
        if sonic.x > -600:
            sonic.x -= int(vel_lateral * dt)
        else:
            sonic.x = -600  # Bloquea en -600
            # Mostrar "eu_bata" momentáneamente
            if not mostrar_bata:
                mostrar_bata = True
                tiempo_bata = now

    if keys[pygame.K_d]:
        sonic.x += int(vel_lateral * dt)

    # agacharse papu
    keys = pygame.key.get_pressed()
    if keys[pygame.K_s] and en_suelo:
        sonic.height = 25
        sonic.y = suelo.y - sonic.height
    else:
        sonic.height = 50

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
    
    if sonic.x < 600:
        camera_x = 0
  
    if sonic.x > 4400:
        camera_x = 5000 - 600
    elif sonic.x > 9400:
        camera_x = 10000 - 600
    elif sonic.x > 14400:
        camera_x = 100 - 600

    # --- Selección de fondo y lógica de cámara ---
    if sonic.x < 600:
        fondo_actual = fondo_day
        limite_camara = 0
    elif sonic.x < 5000:
        fondo_actual = fondo_day2
        limite_camara = 4400
    elif sonic.x < 6200:
        fondo_actual = fondo_midnight
        limite_camara = 5600
    elif sonic.x < 10000:
        fondo_actual = fondo_midnight2
        limite_camara = 9400
    elif sonic.x < 11200:
        fondo_actual = fondo_seminight
        limite_camara = 10600
    elif sonic.x < 15000:
        fondo_actual = fondo_seminight2
        limite_camara = 14400
    elif sonic.x < 16200:
        fondo_actual = fondo_night
        camera_x = 15600
   
    else:
        fondo_actual = fondo_night2
        limite_camara = 19400

    # Lógica de cámara
    if sonic.x <= 0:
        camera_x = -600
    elif sonic.x < limite_camara:
        camera_x = sonic.x - 600
    else:
        camera_x = limite_camara - 600
 



    
    # Lógica especial para fondo Day2: sigue hasta centro=4400 y luego se queda fija; mantiene bloqueo inicial en 1200
    if fondo_actual == fondo_day2:
        if sonic.x <= 1200:
            camera_x = 1200 - 600
        elif sonic.x < 4400:
            camera_x = sonic.x - 600
        else:
            camera_x = 4400 - 600
    if fondo_actual == fondo_midnight:
        # Cámara fija en centro=5600 durante toda la sección midnight
        camera_x = 5600 - 600
    if fondo_actual == fondo_midnight2:
        # Sigue hasta centro=9400 y luego se queda fija; mantiene bloqueo inicial en 6800
        if sonic.x <= 6800:
            camera_x = 6800 - 600
        elif sonic.x < 9400:
            camera_x = sonic.x - 600
        else:
            camera_x = 9400 - 600

    if fondo_actual == fondo_seminight:
        # Cámara fija en centro=10600 en toda la sección
        camera_x = 10600 - 600
    if fondo_actual == fondo_seminight2:
        # Mantener cámara fija en centro=11800 hasta superarlo; seguir hasta 14400 y fijar ahí hasta cambiar de fondo
        if sonic.x <= 11800:
            camera_x = 11800 - 600
        elif sonic.x < 14400:
            camera_x = sonic.x - 600
        else:
            camera_x = 14400 - 600
    if fondo_actual == fondo_night:
        if sonic.x <= 15600:
            camera_x = 15600 - 600
        else:
            camera_x = sonic.x - 600

    # Teletransportar Sonic si supera el último fondo
    if sonic.x > 20000:
        sonic.x -= 20000

    # Dibujo de fondo infinito usando fondo_actual
    fondo_width = fondo_actual.get_width()
    fondo_x = -camera_x % fondo_width
    screen.blit(fondo_actual, (fondo_x, 0))
    screen.blit(fondo_actual, (fondo_x - fondo_width, 0))


    if fondo_seminight == fondo_actual:
        suelo = pygame.Rect(-10000, 265, 120000, 100)  # Suelo más alto en esta sección
    else:
        suelo = pygame.Rect(-10000, 280, 120000, 100)  # Suelo centrado verticalmente
        # Suelo y Sonic desplazados por la cámara
    suelo_draw = suelo.move(-camera_x, 0)
    # pygame.draw.rect(screen, (0, 0, 0), suelo_draw)
    screen.blit(sprite_sonic, (sonic.x - camera_x, sonic.y))

    # Mostrar "eu_bata" por 1 segundo si corresponde
    if mostrar_bata:
        screen.blit(sprite_eu_bata, (sonic.x - camera_x, sonic.y - 130))  # Arriba de Sonic
        if now - tiempo_bata > 1:
            mostrar_bata = False

    pygame.display.flip()

pygame.quit()
