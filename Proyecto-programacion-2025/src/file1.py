import os
import pygame
import time

# Cambia el directorio de trabajo al del script actual
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Iniciar Pygame
pygame.init()

# --- fondos y ventana (igual que tenías) ---
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

screen = pygame.display.set_mode((1200, 700))
pygame.display.set_caption("El veloz")
clock = pygame.time.Clock()

mirando_derecha = False

# --- Sprite y dimensiones ---
sprite_sonic = pygame.image.load("../sprites/sprites_character/idle_character.png")
sprite_sonic = pygame.transform.scale(sprite_sonic, (120, 120))
SPRITE_W, SPRITE_H = sprite_sonic.get_size()

# eu_bata
sprite_eu_bata = pygame.image.load("../sprites/eu_bata.png")
sprite_eu_bata = pygame.transform.scale(sprite_eu_bata, (400, 120))

# --- Hitbox (usamos una rect pequeño para colisiones) ---
HITBOX_W = 50
HITBOX_H_STAND = 100
HITBOX_H_CROUCH = 100

# sonic = hitbox en coordenadas del MUNDO
sonic = pygame.Rect(-499, 350 - HITBOX_H_STAND, HITBOX_W, HITBOX_H_STAND)

# Suelo en coordenadas del mundo (largo)
suelo_y_default = 320
suelo = pygame.Rect(-10000, suelo_y_default, 120000, 100)

# Variables físicas
vel_y = 0
gravedad = 2400
vel_salto = -1100
vel_lateral = 1400
en_suelo = False

# Cámara
camera_x = 0
mostrar_bata = False
tiempo_bata = 0

# --- Función para cargar frames (fuera del loop) ---
def cargar_frames(ruta_carpeta, tamaño=(120,120)):
    frames = []
    if not os.path.isdir(ruta_carpeta):
        return frames
    for archivo in sorted(os.listdir(ruta_carpeta)):
        if archivo.endswith(".png"):
            imagen = pygame.image.load(os.path.join(ruta_carpeta, archivo)).convert_alpha()
            imagen = pygame.transform.scale(imagen, tamaño)
            frames.append(imagen)
    return frames

# Cargar animaciones
walk_frames = cargar_frames("../sprites/sprites_character/movs")
run_frames = cargar_frames("../sprites/sprites_character/run")
dash_frames = cargar_frames("../sprites/sprites_character/dash")

idle_frame = pygame.transform.scale(pygame.image.load("../sprites/sprites_character/idle_character.png"), (SPRITE_W, SPRITE_H))
jump_frame = pygame.transform.scale(pygame.image.load("../sprites/sprites_character/jumping.png"), (SPRITE_W, SPRITE_H))
crouch_frame = pygame.transform.scale(pygame.image.load("../sprites/sprites_character/Crouching_character.png"), (SPRITE_W, SPRITE_H))

animaciones = {
    "walk": walk_frames,
    "run": run_frames,
    "dash": dash_frames,
    "jump": [jump_frame],
    "crouch": [crouch_frame],
    "idle": [idle_frame],
}

# Animación runtime
estado = "idle"
frame_index = 0
frame_timer = 0.0
frame_duracion = 0.08

# --- Bucle principal ---
running = True
last_time = time.time()
while running:
    now = time.time()
    dt = now - last_time
    last_time = now

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # Movimiento lateral (x) — usar la hitbox (sonic)
    if keys[pygame.K_d]:
        sonic.x += int(vel_lateral * dt)
        mirando_derecha = True


    if keys[pygame.K_a]:
        sonic.x -= int(vel_lateral * dt)
        mirando_derecha = False
        if sonic.x < -600:
            sonic.x = -600
            if not mostrar_bata:
                mostrar_bata = True
                tiempo_bata = now
    # Saltar
    if keys[pygame.K_w] and en_suelo:
        vel_y = vel_salto
        en_suelo = False

    # Agacharse (cambiar altura de hitbox)
    if keys[pygame.K_s] and en_suelo:
        sonic.height = HITBOX_H_CROUCH
        # siempre que esté en suelo, anclamos la bottom al suelo
        sonic.bottom = suelo.y
    else:
        # volver a altura de pie; si está en suelo, lo anclamos
        old_bottom = sonic.bottom
        sonic.height = HITBOX_H_STAND
        if en_suelo:
            sonic.bottom = suelo.y
        else:
            # si estaba parcialmente en el aire, preservamos la y aproximada
            sonic.y = old_bottom - sonic.height

    # Aplicar gravedad y mover en y
    vel_y += gravedad * dt
    sonic.y += vel_y * dt


    if sonic.colliderect(suelo):
        if vel_y > 0:
            # anclar la base de la hitbox al tope del suelo
            sonic.bottom = suelo.y
            vel_y = 0
        en_suelo = True
    else:
        en_suelo = False

    # Determinar estado (usamos en_suelo actualizado)
    if not en_suelo:
        estado = "jump"
    elif keys[pygame.K_s] and (keys[pygame.K_d] or keys[pygame.K_a]):
        estado = "dash"
    elif keys[pygame.K_s]:
        estado = "crouch"
    elif keys[pygame.K_LSHIFT] and (keys[pygame.K_d] or keys[pygame.K_a]):
        estado = "run"
    elif keys[pygame.K_d] and keys[pygame.K_a]:
        estado = "idle"
    elif keys[pygame.K_ESCAPE]:
        import vent_inicio  # Volver al menú principal
        running = False
    elif keys[pygame.K_d] or keys[pygame.K_a]:
        estado = "walk"
    else:
        estado = "idle"

    if estado == "walk":
        vel_lateral = 1200
    elif estado == "run":
        vel_lateral = 1500
    elif estado == "dash":
        vel_lateral = 1800
    elif estado == "crouch":
        vel_lateral = 0

    # Cámara centrada en la hitbox
    camera_x = sonic.x - 600
    if sonic.x < 600:
        camera_x = 0

    # --- Selección de fondo y limite_camara ---
    if sonic.x < 600:
        fondo_actual = fondo_day
        limite_camara = 0
    elif sonic.x < 5000:
        fondo_actual = fondo_day2
        limite_camara = 4400
    elif sonic.x < 5600:
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
        limite_camara = 15600
    else:
        fondo_actual = fondo_night2
        limite_camara = 19400

    # Ajustes de camara según límites
    if sonic.x <= 0:
        camera_x = -600
    elif sonic.x < limite_camara:
        camera_x = sonic.x - 600
    else:
        camera_x = limite_camara - 600

    # --- Animación: seleccionar frames y actualizar índice ---
    frames = animaciones.get(estado, [idle_frame])
    if estado in ["walk", "run", "dash"]:
        frame_timer += dt
        if frame_timer >= frame_duracion:
            frame_timer = 0
            frame_index = (frame_index + 1) % max(1, len(frames))
    else:
        frame_index = 0

    imagen_actual = frames[frame_index] if len(frames) > 0 else idle_frame

    # --- Dibujado ---
    fondo_width = fondo_actual.get_width()
    fondo_x = -camera_x % fondo_width
    screen.blit(fondo_actual, (fondo_x, 0))
    screen.blit(fondo_actual, (fondo_x - fondo_width, 0))

    # Si querés dibujar el rect del suelo para debug:
    # suelo_draw = suelo.move(-camera_x, 0)
    # pygame.draw.rect(screen, (255,0,0), suelo_draw, 2)

    # Calcular posición de dibujo del sprite respecto al hitbox
    sprite_draw_x = sonic.x - camera_x - (SPRITE_W - sonic.width) // 10
    sprite_draw_y = sonic.y - (SPRITE_H - sonic.height)

    imagen_actual = frames[frame_index] if len(frames) > 0 else idle_frame

# Si está mirando a la izquierda, voltear el frame
    if not mirando_derecha:
        imagen_actual = pygame.transform.flip(imagen_actual, True, False)

    screen.blit(imagen_actual, (sonic.x - camera_x, sonic.y))

    # Mostrar "eu_bata"
    if mostrar_bata:
        screen.blit(sprite_eu_bata, (sonic.x - camera_x, sonic.y - 140))
        if now - tiempo_bata > 1:
            mostrar_bata = False

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
