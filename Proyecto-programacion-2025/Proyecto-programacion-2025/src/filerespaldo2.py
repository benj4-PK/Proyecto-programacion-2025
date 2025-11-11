import os
import pygame
import time
import random
import serial
from vent_inicio import music_vol
from variablesimage import baknik, baknik2, baknik3, avispa, avispa2, avispa3, avispa4, crab, crab2, crab3, pez, sol1, atardecer, luna, solnight, espinas, fondo_day, fondo_day2, fondo_midnight, fondo_midnight2, fondo_seminight, fondo_seminight2, fondo_night, fondo_night2, rings, sprite_sonic, sprite_muerte, sprite_damage, sprite_damage2, sprite_damage3, sprite_damage4, sprite_eu_bata, sol_world_x, sol_world_y, proyectil, roca1, roca2, roca3
from file2 import fondo_elegido
import sys

def ruta(relativa):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relativa)
    return os.path.join(os.path.dirname(__file__), relativa)

pygame.init()

# ---------- Configuración Arduino (abrir una vez) ----------
arduino = None
COM_PORT = 'COM3'  # ajustá si tu Arduino está en otro puerto
BAUDRATE = 9600
try:
    print("🔄 Intentando conectar a", COM_PORT)
    arduino = serial.Serial(COM_PORT, BAUDRATE, timeout=0.05)
    time.sleep(2)
    arduino.reset_input_buffer()
    print("✅ Conectado a Arduino en", COM_PORT)
except Exception as e:
    print(f"❌ No se pudo conectar a Arduino ({e}) — seguir con teclado únicamente.")
    arduino = None

# Variables del joystick y botones
joystick_x = 512
joystick_y = 513
joystick_btn = 1
joystick_menu_btn = 1
joystick_run_btn = 1
umbral_movimiento = 200

def leer_joystick():
    """Lee una línea del Arduino si hay datos disponibles y actualiza las variables globales."""
    global joystick_x, joystick_y, joystick_btn, joystick_menu_btn, joystick_run_btn
    if not arduino:
        return
    try:
        # Leer hasta una línea completa (con timeout)
        if arduino.in_waiting > 0:
            arduino.reset_input_buffer()
            linea = arduino.readline().decode('utf-8', errors='ignore').strip()
            if linea:
                datos = linea.split(',')
                if len(datos) >= 5:
                    try:
                        joystick_x = int(datos[0])
                        joystick_y = int(datos[1])
                        joystick_btn = int(datos[2])
                        joystick_run_btn = int(datos[3])
                        joystick_menu_btn = int(datos[4])
                        
                    except ValueError:
                        # datos malformados, ignorar
                        pass
    except Exception:
        # no queremos que fallos en la lectura detengan el juego
        pass


screen = pygame.display.set_mode((1200, 700))
pygame.display.set_caption("El veloz")
clock = pygame.time.Clock()

# ---------- Audio: inicializar una sola vez ----------
try:
    pygame.mixer.init()
    music_path = os.path.join("..", "musica", "music_level.mp3")
    if os.path.exists(music_path):
        pygame.mixer.music.load(music_path)
        vol = music_vol if 'music_vol' in globals() else 0.5
        try:
            pygame.mixer.music.set_volume(max(0.0, min(1.0, float(vol))))
        except Exception:
            pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    else:
        print("Aviso: no se encontró música de nivel en:", music_path)
except Exception as e:
    print("Error iniciando audio/música:", e)

mirando_derecha = False


SPRITE_W, SPRITE_H = sprite_sonic.get_size()

HITBOX_W = 50
HITBOX_H_STAND = 100
HITBOX_H_CROUCH = 100

ENEMY_ANIMATIONS = {
    "baknik": [baknik, baknik2, baknik3],
    "crab": [crab, crab2, crab3],
    "avispa": [avispa, avispa2, avispa3, avispa4]
}

ENEMY_FRAME_DURATION = 0.15



sonic = pygame.Rect(700, 350 - HITBOX_H_STAND, HITBOX_W, HITBOX_H_STAND)

if fondo_elegido == 2:
    suelo_y_default = 300
    suelo = pygame.Rect(-10000, suelo_y_default, 120000, 100)
else:
    suelo_y_default = 320
    suelo = pygame.Rect(-10000, suelo_y_default, 120000, 100)

invulnerable = False
invulnerability_timer = 0.0
INVULNERABILITY_DURATION = 3.0
vel_y = 0
gravedad = 2400
vel_salto = -1100
vel_lateral = 1000
en_suelo = False
cont_spindash = 0
disminuir_spindash = 100
# Variables para hacer las roquinhas
rocas_estados = {} 
roca_id_counter = 0 
ROCA_GRAVEDAD = 1800 
ROCA_VEL_Y_INICIAL = 0

camera_x = 0
mostrar_bata = False
tiempo_bata = 0

zona_actual = None
plantada = False
camera_planted_x = 0

max_zona_reached = -1

dead = False
death_timer = 0.0
DEATH_DURATION = 3.0
death_music_played = False

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

estado = "idle"
frame_index = 0
frame_timer = 0.0
frame_duracion = 0.08
rocas_list = []
rings_list = []

def generate_rings(num_rings):
    for _ in range(num_rings):
        x = random.randint(600, 78800)
        y = random.randint(100, suelo_y_default - 50)
        rings_list.append(pygame.Rect(x, y, 30, 30))



generate_rings(100)
ring_count = 0
font = pygame.font.Font(None, 36)

crabs_list = []
bakniks_list = []
avispas_list = []

enemy_states = {}
enemy_id = 0

ENEMY_VEL_LATERAL = 200
ENEMY_TIEMPO_CAMBIO = 2.0
ENEMY_GRAVEDAD = 2400

def generate_enemies(num_enemies):
    global enemy_id
    avispas_list.clear()
    crabs_list.clear()
    bakniks_list.clear()
    
    zonas_spawn = [
        (1000, 18800),
        (24000, 38800),
        (44000, 58800),
        (64000, 78800)
    ]
    
    for zona_start, zona_end in zonas_spawn:
        for _ in range(num_enemies):
            
            x = random.randint(zona_start, zona_end)
            crab_rect = pygame.Rect(x, suelo_y_default - 65, 65, 65)
            enemy_id += 1
            crabs_list.append((enemy_id, crab_rect))
            enemy_states[enemy_id] = {
                'vel_y': 0,
                'vel_x': ENEMY_VEL_LATERAL,
                'timer': 0,
                'type': 'crab', 
                'frame_index': 0,
                'frame_timer': 0.0
            }
            
            x = random.randint(zona_start, zona_end)
            baknik_rect = pygame.Rect(x, suelo_y_default - 65, 65, 65)
            enemy_id += 1
            bakniks_list.append((enemy_id, baknik_rect))
            enemy_states[enemy_id] = {
                'vel_y': 0,
                'vel_x': ENEMY_VEL_LATERAL,
                'timer': 0,
                'type': 'baknik', 
                'frame_index': 0,
                'frame_timer': 0.0
            }

            x = random.randint(zona_start, zona_end)
            avispa_rect = pygame.Rect(x, (suelo_y_default-220) - 65, 65, 65)
            enemy_id += 1
            avispas_list.append((enemy_id, avispa_rect))
            enemy_states[enemy_id] = {
                'vel_y': 0,
                'vel_x': ENEMY_VEL_LATERAL,
                'timer': 0,
                'type': 'avispa',
                'frame_index': 0,
                'frame_timer': 0.0
            }
def generate_rocks(start_x, end_x, num_rocks, rock_images):
    global roca_id_counter
    rocas_list.clear()
    
    # Aseguramos que las rocas aparezcan por encima de la pantalla
    spawn_y = -100 
    
    for _ in range(num_rocks):
        x = random.randint(start_x, end_x)
        
        # Elegir una imagen de roca aleatoria para el tamaño
        imagen_roca = random.choice(rock_images)
        w, h = imagen_roca.get_size()
        
        roca_rect = pygame.Rect(x, spawn_y, w, h)
        roca_id_counter += 1
        
        # Guardar la roca en la lista principal y su estado en el diccionario
        rocas_list.append((roca_id_counter, roca_rect, imagen_roca))
        
        rocas_estados[roca_id_counter] = {
            'vel_y': ROCA_VEL_Y_INICIAL,
            'image': imagen_roca # Guardamos qué imagen usa para dibujarla
        }

# Imágenes disponibles para las rocas
ROCK_IMAGES = [roca1, roca2, roca3]
# Generar Rocas 
# Ajusta el rango final según el fondo_elegido
if fondo_elegido == 2:
    generate_rocks(58800, 60000, 15, ROCK_IMAGES) # 15 rocas en la última zona del nivel 4
def update_enemy(enemy_id, enemy_rect, dt):
    state = enemy_states[enemy_id]
    
    state['timer'] += dt
    if state['timer'] >= ENEMY_TIEMPO_CAMBIO:
        state['timer'] = 0
        state['vel_x'] *= -1

    enemy_rect.x += state['vel_x'] * dt

 
    if state['type'] != 'avispa':
        state['vel_y'] += ENEMY_GRAVEDAD * dt
        enemy_rect.y += state['vel_y'] * dt

        if enemy_rect.colliderect(suelo):   
            enemy_rect.bottom = suelo.y
            state['vel_y'] = 0
    
            
    state['frame_timer'] += dt
    if state['frame_timer'] >= ENEMY_FRAME_DURATION:
        state['frame_timer'] = 0
        frames = ENEMY_ANIMATIONS.get(state['type'], [])
        if frames:
            state['frame_index'] = (state['frame_index'] + 1) % len(frames)

generate_enemies(20)
espinas_positions = []
nueva_zona = fondo_elegido
if nueva_zona == 0:
    espinas_positions = [
        # Zona 1: Dia
        
            (2000, suelo_y_default+15),
            (4500, suelo_y_default+15),
            (7000, suelo_y_default+15),
            (9500, suelo_y_default+15),
            (12000, suelo_y_default+15),
            (14500, suelo_y_default+15),
            (17000, suelo_y_default+15),
            (18600, suelo_y_default+15),
            (18800, suelo_y_default+15),
            (19900, suelo_y_default+15),
    ]
    
elif nueva_zona == 1:
    espinas_positions = [
            # Zona 2: Medianoche (ejemplo)
            (22000, suelo_y_default+15),
            (21900, suelo_y_default+15),
            (25000, suelo_y_default+15),
            (25000, suelo_y_default+15-90),
            (28000, suelo_y_default+15),
            (30500, suelo_y_default+15),
            (30400, suelo_y_default+15),
            (33000, suelo_y_default+15),
            (35500, suelo_y_default+15),
            (35500, suelo_y_default+15-90),
            (38000, suelo_y_default+15),
            (38800, suelo_y_default+15),
            (39900, suelo_y_default+15)
    
    ]
            
elif nueva_zona == 2:
    espinas_positions = [
            # Zona 3 : Seminoche 
            (42000, suelo_y_default+25),
            (44500, suelo_y_default+25),
            (47000, suelo_y_default+25),
            (49500, suelo_y_default+25),
            (52000, suelo_y_default+25),
            (54500, suelo_y_default+25),
            (57000, suelo_y_default+25),
            (57100, suelo_y_default+25),
            (57100, suelo_y_default+25-90),
            (57200, suelo_y_default+25),
            (58000, suelo_y_default+25),
            (58100, suelo_y_default+25),
            (58200, suelo_y_default+25),
            (58100, suelo_y_default+25-90),
            (58800, suelo_y_default+25),
            (59900, suelo_y_default+25)
    ]

elif nueva_zona == 3:
            espinas_positions = [
            # Zona 4 _ Noche
            (62000, suelo_y_default+15),
            (62100, suelo_y_default+15),
            (62200, suelo_y_default+15),
            (62500, suelo_y_default+15),
            (63000, suelo_y_default+15),
            (63000, suelo_y_default+15-90),
            (63500, suelo_y_default+15),
            (63600, suelo_y_default+15),
            (64000, suelo_y_default+15),
            (64300, suelo_y_default+15),
            (64300, suelo_y_default+15-90),
            (64400, suelo_y_default+15),
            (64800, suelo_y_default+15),
            (64800, suelo_y_default+15-90),
            (65100, suelo_y_default+15),
            (65200, suelo_y_default+15),
            (65300, suelo_y_default+15),
            (67000, suelo_y_default+15),
            (67100, suelo_y_default+15),
            (67200, suelo_y_default+15),
            (69500, suelo_y_default+15),
            (72000, suelo_y_default+15),
            (74500, suelo_y_default+15),
            (77000, suelo_y_default+15),
            (78500, suelo_y_default+15-90),
            (78500, suelo_y_default+15),
            (78800, suelo_y_default+15),
            (79900, suelo_y_default+15)
            




    ]
# Ajustar la 'y' para que el dibujo y la colisión sean correctos
# El sprite de espinas tiene una altura, y queremos que 'suelo_y_default' sea la parte inferior.
# Obtener la altura de las espinas una sola vez
if 'espinas' in globals():
    ESPINAS_HEIGHT = espinas.get_height()
else:
    ESPINAS_HEIGHT = 90 # Valor por defecto si no se pudo cargar

# Transformamos la lista de posiciones (x) en rectángulos de colisión (Rect)
espinas_rects = []
for x_world, y_world_base in espinas_positions:
    # Creamos el Rect: x, y (ajustada para el suelo), ancho, alto
    rect = pygame.Rect(x_world, y_world_base - ESPINAS_HEIGHT, espinas.get_width(), ESPINAS_HEIGHT)
    espinas_rects.append(rect)
def handle_hit(enemy_id, enemy_list, estado):
    global ring_count, running, invulnerable, invulnerability_timer, dead, death_timer, hurt, hurt_timer, death_music_played
    # Si se está invulnerable, empujar a sonic y salir
    if invulnerable == True:
        sonic.x = sonic.x - 100  # Retroceder un poco al ser golpeado

    if estado in ["jump", "dash"]:
        # matar enemigo
        enemy_list[:] = [enemy for enemy in enemy_list if enemy[0] != enemy_id]
        if enemy_id in enemy_states:
            del enemy_states[enemy_id]
        return

    if invulnerable or dead:
        return

    if ring_count > 0:
        print(f"¡Sonic fue golpeado! Pierde {ring_count} rings, pero sobrevive.")
        ring_count = 0
        invulnerable = True
        invulnerability_timer = 0.0
        hurt = True
        hurt_timer = 0.0
        return

    print("¡Game Over! Sonic fue golpeado sin rings. Iniciando secuencia de muerte.")
    dead = True
    
    death_timer = 0.0
    try:
        pygame.mixer.music.stop()
        death_music_path = "../musica/sonicded.mp3"
        if os.path.exists(death_music_path):
            pygame.mixer.music.load(death_music_path)
            pygame.mixer.music.play(0)
            death_music_played = True
    except Exception as e:
        print(f"Error al reproducir música de muerte: {e}")

HURT_DURATION = 3.0
HURT_FRAMES = []
HURT_FRAME_COUNT = 5
HURT_FRAME_TIME = HURT_DURATION / max(1, HURT_FRAME_COUNT)
for i in range(1, HURT_FRAME_COUNT + 1):
    path = f"../sprites/daño/hurt{i}.png"
    if os.path.exists(path):
        img = pygame.image.load(path)
        img = pygame.transform.scale(img, (SPRITE_W, SPRITE_H))
    else:
        img = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
        img.fill((255, 100, 100, 180))
    HURT_FRAMES.append(img)

hurt = False
hurt_timer = 0.0

running = True
last_time = time.time()

# Si fondo_elegido no viene de otro archivo, ponemos por defecto 0
if 'fondo_elegido' not in globals():
    fondo_elegido = 0
if 'fondo_actual' not in globals():
    fondo_actual = fondo_day2

while running:
    now = time.time()
    dt = now - last_time
    last_time = now


    # Leer Arduino al inicio de cada frame
    leer_joystick()

    if dead:
        # 1. Actualizar el temporizador de muerte
        death_timer += dt
        
        # 2. Procesar eventos (solo para poder cerrar la ventana manualmente)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
        # 3. Dibujado en estado de muerte:
        # Recalcular fondo (necesario si la cámara se movió antes de morir)
        fondo_width = fondo_actual.get_width()
        fondo_x = -camera_x % fondo_width
        screen.blit(fondo_actual, (fondo_x, 0))
        screen.blit(fondo_actual, (fondo_x - fondo_width, 0))
        
        sprite_draw_x = sonic.x - camera_x
        sprite_draw_y = sonic.y - (SPRITE_H - sonic.height)
        
        screen.blit(sprite_muerte, (sprite_draw_x, sprite_draw_y)) 
        
        pygame.display.flip()
        
        # detener la música y cerrar tras el tiempo de muerte
        if death_timer >= DEATH_DURATION:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
            running = False # Termina el bucle principal después del tiempo
            
        clock.tick(30)
        continue  
    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Lógica de la Roca ---
for roca_id, roca_rect, roca_image in rocas_list[:]:
    # 1. Aplicar Gravedad (ignora el suelo)
    state = rocas_estados.get(roca_id)
    if state:
        state['vel_y'] += ROCA_GRAVEDAD * dt
        roca_rect.y += state['vel_y'] * dt
    
    roca_draw_pos = (roca_rect.x - camera_x, roca_rect.y)
    
    # 2. Dibujado
    # Solo dibujamos si está visible en la pantalla
    if -roca_rect.width < roca_draw_pos[0] < screen.get_width() and roca_draw_pos[1] < screen.get_height():
        screen.blit(roca_image, roca_draw_pos)
    
    # 3. Colisión con Sonic
    if sonic.colliderect(roca_rect):
        # Usamos tu función de golpe para manejar la pérdida de rings o la muerte
        handle_hit(roca_id, rocas_list, estado) 
        
    # 4. Eliminar si sale de la pantalla (cae)
    # Si la roca cae fuera del borde inferior (ej: 800 pixeles de alto)
    if roca_rect.y > 800:
        # Nota: handle_hit elimina al enemigo de la lista, pero la roca
        # necesita ser eliminada manualmente si solo cae.
        if (roca_id, roca_rect, roca_image) in rocas_list:
            rocas_list.remove((roca_id, roca_rect, roca_image))
        if roca_id in rocas_estados:
            del rocas_estados[roca_id]

    keys = pygame.key.get_pressed()
    
    # calcular movimientos del joystick
    movimiento_joystick_derecha = joystick_x > (512 + umbral_movimiento)
    movimiento_joystick_izquierda = joystick_x < (512 - umbral_movimiento)
    movimiento_joystick_abajo = joystick_y > (513 + umbral_movimiento)

    # velocidad lateral base
    vel_lateral_base = 1100

    if invulnerable:
        vel_lateral = 0
    else:
        vel_lateral = vel_lateral_base

    # MOVIMIENTO horizontal
    if (keys[pygame.K_d] or movimiento_joystick_derecha):
        sonic.x += int(vel_lateral * dt)
        mirando_derecha = True

    if (keys[pygame.K_a] or movimiento_joystick_izquierda):
        sonic.x -= int(vel_lateral * dt)
        mirando_derecha = False
        if sonic.x < -600:
            sonic.x = -600
            if not mostrar_bata:
                mostrar_bata = True
                tiempo_bata = now

    # SALTO (botón de Arduino asumido 0 cuando presionado)
    if (keys[pygame.K_w] or joystick_btn == 0) and en_suelo:
        vel_y = vel_salto
        en_suelo = False

    # AGACHARSE
    if (keys[pygame.K_s] or movimiento_joystick_abajo) and en_suelo:
        sonic.height = HITBOX_H_CROUCH
        sonic.bottom = suelo.y
    else:
        old_bottom = sonic.bottom
        sonic.height = HITBOX_H_STAND
        if en_suelo:
            sonic.bottom = suelo.y
        else:
            sonic.y = old_bottom - sonic.height

    # FÍSICA vertical
    vel_y += gravedad * dt
    sonic.y += vel_y * dt

    if sonic.colliderect(suelo):
        if vel_y > 0:
            sonic.bottom = suelo.y
            vel_y = 0
        en_suelo = True
    else:
        en_suelo = False
   # Si se presiona el botón de menú (o ESC) se vuelve al menú
    if keys[pygame.K_ESCAPE] or joystick_menu_btn == 0:
        import vent_inicio
        running = False
    # Determinar estado (walk/run/dash/crouch...)
    if not en_suelo:
        estado = "jump"
    elif (keys[pygame.K_s] or movimiento_joystick_abajo) and (
        keys[pygame.K_d] or keys[pygame.K_a] or movimiento_joystick_derecha or movimiento_joystick_izquierda
    ):
        estado = "dash"
    elif (keys[pygame.K_s] or movimiento_joystick_abajo):
        estado = "crouch"
    elif (keys[pygame.K_LSHIFT] or joystick_run_btn == 0) and (keys[pygame.K_d] or keys[pygame.K_a] or movimiento_joystick_derecha or movimiento_joystick_izquierda):
        estado = "run"
    elif (keys[pygame.K_d] and keys[pygame.K_a]) or (movimiento_joystick_derecha and movimiento_joystick_izquierda):
        estado = "idle"
    elif keys[pygame.K_ESCAPE]:
        import vent_inicio
        running = False
    elif keys[pygame.K_d] or keys[pygame.K_a] or movimiento_joystick_derecha or movimiento_joystick_izquierda:
        estado = "walk"
    else:
        estado = "idle"

    # ajustar velocidades según estado
    if not invulnerable:
        if estado == "walk":
            vel_lateral = 1100
        elif estado == "run":
            vel_lateral = 1600
        elif estado == "dash":
            vel_lateral = 1400

        elif estado == "crouch":
            vel_lateral = 0
    elif estado == "crouch":
        vel_lateral = 0

    # lógica de cámaras y zonas (igual que antes)
    if sonic.x < 600:
        camera_x = 0

    zonas = [
        ("day2", 600, 20000),
        ("midnight2", 20000, 40000),
        ("seminight2", 40000, 60000),
        ("night2", 60000, 80000)
    ] 

    

    if nueva_zona == 0:
        fondo_actual = fondo_day2; limite_camara = 19400
    elif nueva_zona == 1:
        fondo_actual = fondo_midnight2; limite_camara = 39400
    elif nueva_zona == 2:
        fondo_actual = fondo_seminight2; limite_camara = 59400
    elif nueva_zona == 3:
        fondo_actual = fondo_night2; limite_camara = 79400
    else:
        fondo_actual = fondo_night2; limite_camara = 79400

    if nueva_zona is not None and nueva_zona > max_zona_reached:
        max_zona_reached = nueva_zona

    if max_zona_reached >= 0:
        min_x_allowed = zonas[max_zona_reached][1]
        if sonic.x < min_x_allowed:
            sonic.x = min_x_allowed

    if nueva_zona != zona_actual:
        zona_actual = nueva_zona
        plantada = True
        camera_planted_x = max(0, int(sonic.x - 10))

    if plantada:
        if sonic.x - camera_planted_x <= 600:
            camera_x = camera_planted_x
        else:
            plantada = False
            camera_x = sonic.x - 600
    else:
        if sonic.x <= 0:
            camera_x = 0
        elif sonic.x < limite_camara:
            camera_x = sonic.x - 600
        else:
            camera_x = limite_camara - 600

    # animación de frames
    frames = animaciones.get(estado, [idle_frame])
    if estado in ["walk", "run", "dash"]:
        frame_timer += dt
        if frame_timer >= frame_duracion:
            frame_timer = 0
            frame_index = (frame_index + 1) % max(1, len(frames))
    else:
        frame_index = 0

    imagen_actual = frames[frame_index] if len(frames) > 0 else idle_frame

    # 1. Dibujar el Fondo (capa más profunda)
    fondo_width = fondo_actual.get_width()
    fondo_x = -camera_x % fondo_width
    screen.blit(fondo_actual, (fondo_x, 0))
    screen.blit(fondo_actual, (fondo_x - fondo_width, 0))

    # 2. Dibujar el Sol (solo si estás en la zona 0)
    if nueva_zona == 0:
        # La posición en pantalla es la posición del mundo menos la cámara
        sol_draw_x = sol_world_x - camera_x
        # Si la imagen está dentro de la pantalla (opcional)
        if -sol1.get_width() < sol_draw_x < 1200:
            screen.blit(sol1, (sol_draw_x, sol_world_y)) 

    # Solución: restar la posición de la cámara (camera_x) a la posición del mundo (2000)
        #espinas_draw_x = 2000 - camera_x
        #screen.blit(espinas, (espinas_draw_x, suelo_y_default-75) )
        # 2.5. Dibujar Múltiples Espinas y Comprobar Colisiones
    
    for espina_rect in espinas_rects[:]:
        espinas_draw_x = espina_rect.x - camera_x
        
        # Optimización: Solo dibujar si está en la pantalla
        if -espina_rect.width < espinas_draw_x < screen.get_width():
            screen.blit(espinas, (espinas_draw_x, espina_rect.y))
        
        # --- Lógica de Colisión ---
        if sonic.colliderect(espina_rect):
            # Lógica para manejar el daño ambiental (espinas)
            if not invulnerable and not dead:
                if ring_count > 0:
                    print("¡Sonic fue golpeado por pínchos, Pierde rings.")
                    ring_count = 0
                    invulnerable = True
                    invulnerability_timer = 0.0
                    hurt = True
                    hurt_timer = 0.0
                    sonic.x = sonic.x - 200  # Retroceder un poco al ser golpeado
                else:
                    print("¡Game Over! Sonic tocó espinas sin rings.")
                    dead = True
                    death_timer = 0.0
                    
                    # Lógica de música de muerte (copiada de handle_hit)
                    if not death_music_played:
                        try:
                            pygame.mixer.music.stop()
                            death_music_path = "../musica/sonicded.mp3"
                            if os.path.exists(death_music_path):
                                pygame.mixer.music.load(death_music_path)
                                pygame.mixer.music.play(0)
                                death_music_played = True
                        except Exception as e:
                            print(f"Error al reproducir música de muerte: {e}")
            break # Si chocó con una espina, no necesitas comprobar las demás.

    # 3. Dibujar Sonic (capa media)
    sprite_draw_x = sonic.x - camera_x - (SPRITE_W - sonic.width) // 10
    sprite_draw_y = sonic.y - (SPRITE_H - sonic.height)

    if not mirando_derecha:
        imagen_actual = pygame.transform.flip(imagen_actual, True, False)

    if invulnerable:
        invulnerability_timer += dt
        if invulnerability_timer >= INVULNERABILITY_DURATION:
            invulnerable = False
            invulnerability_timer = 0.0

    should_draw_sonic = True
    if invulnerable:
        should_draw_sonic = (invulnerability_timer * 10) % 1 > 0.5

    if should_draw_sonic:
        if invulnerable and invulnerability_timer <= 1.0:
            damage_frame_index = int((invulnerability_timer * 4)) % 4
            damage_sprites = [sprite_damage, sprite_damage2, sprite_damage3, sprite_damage4]
            current_sprite = damage_sprites[damage_frame_index]
            if not mirando_derecha:
                current_sprite = pygame.transform.flip(current_sprite, True, False)
            screen.blit(current_sprite, (sonic.x - camera_x, sonic.y))
        else:
            screen.blit(imagen_actual, (sonic.x - camera_x, sonic.y))

    if mostrar_bata:
        screen.blit(sprite_eu_bata, (sonic.x - camera_x, sonic.y - 140))
        if now - tiempo_bata > 1:
            mostrar_bata = False

    for ring in rings_list[:]:
        ring_draw_pos = (ring.x - camera_x, ring.y)
        if -50 <= ring_draw_pos[0] <= 1250:
            screen.blit(rings, ring_draw_pos)
            if sonic.colliderect(ring):
                rings_list.remove(ring)
                if ring_count < 100:
                    ring_count += 1

    ring_text = font.render(f'Rings: {ring_count}', True, (255, 255, 0))
    screen.blit(ring_text, (50, 50))

    for enemy_id, crab_rect in crabs_list[:]:
        update_enemy(enemy_id, crab_rect, dt)
        crab_draw_pos = (crab_rect.x - camera_x, crab_rect.y)
        
        if -65 <= crab_draw_pos[0] <= 1265:
            state = enemy_states.get(enemy_id)
            if state and state['type'] == 'crab':
                frames_e = ENEMY_ANIMATIONS.get('crab', [crab])
                current_sprite = frames_e[state['frame_index']]
                if state['vel_x'] < 0:
                    current_sprite = pygame.transform.flip(current_sprite, True, False)
                screen.blit(current_sprite, crab_draw_pos)
            else:
                screen.blit(crab, crab_draw_pos)

            if sonic.colliderect(crab_rect):
                handle_hit(enemy_id, crabs_list, estado)

    for enemy_id, baknik_rect in bakniks_list[:]:
        update_enemy(enemy_id, baknik_rect, dt)
        baknik_draw_pos = (baknik_rect.x - camera_x, baknik_rect.y)
        
        if -65 <= baknik_draw_pos[0] <= 1265:
            state = enemy_states.get(enemy_id)
            if state and state['type'] == 'baknik':
                frames_e = ENEMY_ANIMATIONS.get('baknik', [baknik])
                current_sprite = frames_e[state['frame_index']]
                if state['vel_x'] < 0:
                    current_sprite = pygame.transform.flip(current_sprite, True, False)
                screen.blit(current_sprite, baknik_draw_pos)
            else:
                screen.blit(baknik, baknik_draw_pos)

            if sonic.colliderect(baknik_rect):
                handle_hit(enemy_id, bakniks_list, estado)
    for enemy_id, avispa_rect in avispas_list[:]:
        update_enemy(enemy_id, avispa_rect, dt)
        avispa_draw_pos = (avispa_rect.x - camera_x, avispa_rect.y)
        
        if -65 <= avispa_draw_pos[0] <= 1265:
            state = enemy_states.get(enemy_id)
            if state and state['type'] == 'avispa':
                frames_e = ENEMY_ANIMATIONS.get('avispa', [avispa])
                current_sprite = frames_e[state['frame_index']]
                if state['vel_x'] < 0:
                    current_sprite = pygame.transform.flip(current_sprite, True, False)
                screen.blit(current_sprite, avispa_draw_pos)
            else:
                screen.blit(avispa, avispa_draw_pos)

            if sonic.colliderect(avispa_rect):
                handle_hit(enemy_id, avispas_list, estado)

    pygame.display.flip()
    clock.tick(30)
    volverabrir= 0
    # comprobaciones de final de nivel
    if fondo_elegido == 0 and sonic.x > 20000:
        print("¡Felicidades! Has completado el nivel 1.")
        volverabrir = 1
        running = False
    if fondo_elegido == 1 and sonic.x > 40000:
        print("¡Felicidades! Has completado el nivel 2.")
        volverabrir = 2
        running = False
    if fondo_elegido == 2 and sonic.x > 60000:
        print("¡Felicidades! Has completado el nivel 3.")
        volverabrir = 3
        running = False
    if fondo_elegido == 3 and sonic.x > 80000:
        print("¡Felicidades! Has completado el nivel 4.")
        volverabrir = 4
        running = False

# ---------- Salir: cerrar Arduino si está abierto ----------
try:
    if arduino and arduino.is_open:
        arduino.close()
except Exception:
    pass

pygame.quit()
if volverabrir == 1:
    import vent_inicio
if volverabrir == 2:
    import vent_inicio
if volverabrir == 3:
    import vent_inicio
if volverabrir == 4:
    import vent_inicio