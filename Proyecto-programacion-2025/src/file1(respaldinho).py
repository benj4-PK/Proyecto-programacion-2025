import os
import pygame
import time
import random
import serial
from vent_inicio import music_vol
from vent_inicio2 import music_vol
from variablesimage import baknik, baknik2, baknik3, avispa, avispa2, avispa3, avispa4, crab, crab2, crab3, pez, sol1, atardecer, luna, solnight, espinas, fondo_day, fondo_day2, fondo_midnight, fondo_midnight2, fondo_seminight, fondo_seminight2, fondo_night, fondo_night2, rings, sprite_sonic, sprite_muerte, sprite_damage, sprite_damage2, sprite_damage3, sprite_damage4, sprite_eu_bata, sol_world_x, sol_world_y, proyectil, roca1, roca2, roca3
from file2 import fondo_elegido

os.chdir(os.path.dirname(os.path.abspath(__file__)))

pygame.init()

# ---------- Configuración Arduino (abrir una vez) ----------
arduino = None
COM_PORT = 'COM3' # ajustá si tu Arduino está en otro puerto
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
umbral_movimiento = 100  # zona muerta para el joystick

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
ROCA_GRAVEDAD = 1200 
ROCA_VEL_Y_INICIAL = -10

# --- NUEVAS VARIABLES PARA EL DISPARO DE AVISPAS ---
SHOOT_INTERVAL = 3.5 # Disparará cada 2.5 segundos (ajustable)
avispa_shoot_timers = {} # {id_avispa: tiempo_ultimo_disparo}
proyectiles_avispa_list = [] # Lista para almacenar los proyectiles
# ---------------------------------------------------

camera_x = 0
# Fijar cámara en nivel 1 durante lock
camera_locked_fixed = False
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
#ggg
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
        (1000, 18750),
        (22000, 38750),
        (42000, 58750),
        (62000, 78750)
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
            # Inicializar el temporizador de disparo para esta avispa
            avispa_shoot_timers[enemy_id] = time.time()
            
def generate_rocks(start_x, end_x, num_rocks, rock_images):
    global roca_id_counter
    rocas_list.clear()
    
    # Aseguramos que las rocas aparezcan por encima de la pantalla
    spawn_y = -150 
    
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
            'image': imagen_roca # Guardamos qué imagaen usa para dibujarla
        }

# Imágenes disponibles para las rocas
ROCK_IMAGES = [roca1, roca2, roca3]

# Flags para spawnear rocas una sola vez por zona
zona_rocks_spawned = {0: False, 1: False, 2: False, 3: False}

# Bloqueo y spawns escalonados por nivel
lock_active = False
lock_timer = 0.0
lock_duration = 0.0
lock_camera_x = 0
spawn_plan = []  # lista de tuplas (t_spawn, count)
random.seed()

def update_enemy(enemy_id, enemy_rect, dt):
    state = enemy_states[enemy_id]
    
    state['timer'] += dt
    if state['timer'] >= ENEMY_TIEMPO_CAMBIO:
        state['timer'] = 0
        state['vel_x'] *= -1

    # Movimiento horizontal
    enemy_rect.x += state['vel_x'] * dt

    # Colisión con espinas: las espinas actúan como pared para los enemigos
    # Si un enemigo colisiona con una espina, lo alineamos justo al borde y volteamos su dirección
    try:
        for espina_rect in espinas_rects:
            if enemy_rect.colliderect(espina_rect):
                # Si se estaba moviendo hacia la derecha
                if state.get('vel_x', 0) > 0:
                    enemy_rect.right = espina_rect.left - 1
                else:
                    enemy_rect.left = espina_rect.right + 1
                # Invertir la dirección horizontal para que no intente atravesarla
                state['vel_x'] = -state.get('vel_x', 0)
                break
    except Exception:
        # Si por alguna razón espinas_rects no está definido aún, ignoramos
        pass

 
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

generate_enemies(15)
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
            (20000, suelo_y_default+15)
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
            (39900, suelo_y_default+15),
            (40000, suelo_y_default+15)
    
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
            (59900, suelo_y_default+25),
            (60000, suelo_y_default+25)
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
    
# Modificación de handle_hit para poder eliminar las rocas y que el código funcione tanto para rocas como para enemigos.
def handle_hit(hit_id, hit_list, estado, is_rock=False): 
    global ring_count, running, invulnerable, invulnerability_timer, dead, death_timer, hurt, hurt_timer, death_music_played, rocas_estados

    # Si se está invulnerable, empujar a sonic y salir
    if invulnerable:
        sonic.x -= 100  # Retroceder un poco al ser golpeado

    if estado in ["jump", "dash"] and not is_rock:
        # Si es un ataque válido (salto/dash) y NO es una roca (las rocas dañan, no se destruyen por golpe)
        hit_list[:] = [hit for hit in hit_list if hit[0] != hit_id]
        if hit_id in enemy_states:
            del enemy_states[hit_id]
        return
    
    # Si es una roca, SIEMPRE se elimina (ya sea que cause daño o no, desaparece al chocar)
    if is_rock:
        hit_list[:] = [hit for hit in hit_list if hit[0] != hit_id]
        if hit_id in rocas_estados:
            del rocas_estados[hit_id]
        # Continuar para ver si la roca causó daño o si Sonic era invulnerable
        if invulnerable or dead:
            return # No causa daño si es invulnerable

    if invulnerable or dead:
        return

    # Lógica de daño
    if ring_count > 0:
        print(f"¡Sonic fue golpeado! Pierde {ring_count} rings, pero sobrevive.")
        sonic.x = sonic.x - 100 if mirando_derecha else sonic.x + 100
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
                import vent_inicio
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

    # --- Lógica de la Roca: Actualización y Colisión (NO DIBUJADO AQUÍ) ---
    for roca_id, roca_rect, roca_image in rocas_list[:]:
        state = rocas_estados.get(roca_id)
        
        if state:
            # Aplicar Gravedad
            state['vel_y'] += ROCA_GRAVEDAD * dt
            roca_rect.y += state['vel_y'] * dt
        
        # Colisión con Sonic (Usamos handle_hit, que maneja el daño)
        if sonic.colliderect(roca_rect):
            # Llama a handle_hit para manejar la colisión y posible daño, indicando que es una roca.
            handle_hit(roca_id, rocas_list, estado, is_rock=True) 
            
        # Eliminar si sale por la parte inferior de la pantalla (cae y desaparece)
        if roca_rect.y > 700 + 100: # 700 es la altura de la pantalla + un margen
            # Para evitar errores si la roca ya fue eliminada por colisión, comprobamos la existencia
            if (roca_id, roca_rect, roca_image) in rocas_list: 
                rocas_list.remove((roca_id, roca_rect, roca_image))
            if roca_id in rocas_estados:
                del rocas_estados[roca_id]

    # --- Lógica de Proyectiles Avispa: Actualización y Colisiódddddddddn ---
    for proyectil_data in proyectiles_avispa_list[:]:
        proyectil_rect = proyectil_data['rect']
        
        # Actualizar posición
        proyectil_rect.x += proyectil_data['vel_x'] * dt
        
        proyectil_rect.y += proyectil_data['vel_y'] * dt
        # Colisión con Sonic
        if sonic.colliderect(proyectil_rect):
            if not invulnerable and not dead:
                if ring_count > 0:
                    print("¡Sonic fue golpeado por un proyectil! Pierde rings.")
                    ring_count = 0
                    invulnerable = True
                    invulnerability_timer = 0.0
                    hurt = True
                    hurt_timer = 0.0
                    sonic.x = sonic.x - 200 # Empujar un poco
                else:
                    print("¡Game Over! Sonic fue golpeado por un proyectil sin rings.")
                    dead = True
                    death_timer = 0.0
                    # Lógica de música de muerte
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
            
            # Eliminar el proyectil después de la colisión o si es invulnerable
            if proyectil_data in proyectiles_avispa_list:
                proyectiles_avispa_list.remove(proyectil_data)
            continue # Pasar al siguiente proyectil

        # Eliminar si sale por la izquierda de la pantalla
        if proyectil_rect.x < camera_x - 100:
            if proyectil_data in proyectiles_avispa_list:
                proyectiles_avispa_list.remove(proyectil_data)
                
    # --- Lógica de Disparo de Avispas (Temporizador) ---
    for enemy_id, avispa_rect in avispas_list[:]:
        
        # 1. Comprobación de Disparo Temporizado
        avispa_id = enemy_id
        if (avispa_id in avispa_shoot_timers and 
            now - avispa_shoot_timers[avispa_id] >= SHOOT_INTERVAL and 
            # Avispa en pantalla (margen de 100 a 1200)
            avispa_rect.x < camera_x + 1200 and avispa_rect.x > camera_x - 100): 

            # 2. Lógica para crear el nuevo proyectilavispa (moviéndose hacia la izquierda)
            proyectil_x = avispa_rect.x 
            proyectil_y = avispa_rect.y + 30 # Ajuste vertical
            
            proyectiles_avispa_list.append({
                'rect': pygame.Rect(proyectil_x, proyectil_y, proyectil.get_width(), proyectil.get_height()),
                'vel_x': -300, # Velocidad del proyectil (300 pixeles por segundo)
                'vel_y': 150,
            })
            
            # 3. Reiniciar el Temporizador
            avispa_shoot_timers[avispa_id] = now
            
    # ---------------------------------------------------


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
            sonic.x = sonic.x + int(300 * dt) if mirando_derecha else sonic.x - int(300 * dt)
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

    # Disparar BLOQUEO y plan de spawns al alcanzar x objetivo por nivel
    trigger_hit = False
    if fondo_elegido == 0 and not zona_rocks_spawned[0] and sonic.x >= 19400:
        zona_rocks_spawned[0] = True
        lock_duration = 5.0
        trigger_hit = True
        lock_end_x = 20000
        spawn_range = (18800, 20000)
    elif fondo_elegido == 1 and not zona_rocks_spawned[1] and sonic.x >= 39400:
        zona_rocks_spawned[1] = True
        lock_duration = 10.0
        trigger_hit = True
        lock_end_x = 40000
        spawn_range = (38800, 40000)
    elif fondo_elegido == 2 and not zona_rocks_spawned[2] and sonic.x >= 59400:
        zona_rocks_spawned[2] = True
        lock_duration = 15.0
        trigger_hit = True
        lock_end_x = 60000
        spawn_range = (58800, 60000)
    elif fondo_elegido == 3 and not zona_rocks_spawned[3] and 78800 <= sonic.x <= 80000:
        zona_rocks_spawned[3] = False
        lock_end_x = 80000
        lock_duration = 0.0
        trigger_hit = False
        spawn_range = (78800, 80000)

    if trigger_hit:
        lock_active = True
        lock_timer = 0.0
        # Fijar la cámara al borde final - 600 para bloquear avance
        lock_camera_x = lock_end_x - 600
        if fondo_elegido == 0:
            # Nivel 1: fijar cámara en 19400 y limitar sonic a 19999
            camera_locked_fixed = True
            camera_x = 19400
            if sonic.x > 19999:
                sonic.x = 19999
        else:
            # Otros niveles: comportamiento anterior
            camera_x = lock_camera_x
            if sonic.x > lock_camera_x + 600:
                sonic.x = lock_camera_x + 600
        # Crear un plan de spawns aleatorios durante la ventana
        spawn_plan = []
        # Definir dificultad por nivel (más oleadas y más rocas en niveles avanzados)
        if fondo_elegido == 0:       # day
            waves = random.randint(3, 4)
            count_min, count_max = 3, 5
        elif fondo_elegido == 1:     # midnight
            waves = random.randint(5, 6)
            count_min, count_max = 4, 6
        elif fondo_elegido == 2:     # seminight
            waves = random.randint(7, 9)
            count_min, count_max = 5, 7
        else:                        # night
            waves = random.randint(8, 9)
            count_min, count_max = 6, 8
        for _ in range(waves):
            t_spawn = random.uniform(0.2, max(0.2, lock_duration - 0.2))
            count = random.randint(count_min, count_max)
            spawn_plan.append((t_spawn, count))
        # ordenar por tiempo
        spawn_plan.sort(key=lambda x: x[0])
        # Guardar el rango a usar en el plan
        planned_spawn_range = spawn_range

    # Ejecutar plan de spawns durante el bloqueo
    if lock_active and spawn_plan:
        # Spawnear todas las oleadas cuyo t_spawn <= lock_timer (y eliminarlas)
        ready = [p for p in spawn_plan if p[0] <= lock_timer]
        if ready:
            for (_, count) in ready:
                # generar 'count' rocas en posiciones aleatorias del rango
                for _ in range(count):
                    x = random.randint(planned_spawn_range[0], planned_spawn_range[1])
                    imagen_roca = random.choice(ROCK_IMAGES)
                    w, h = imagen_roca.get_size()
                    roca_rect = pygame.Rect(x, -100, w, h)
                    roca_id_counter += 1
                    rocas_list.append((roca_id_counter, roca_rect, imagen_roca))
                    rocas_estados[roca_id_counter] = {'vel_y': ROCA_VEL_Y_INICIAL, 'image': imagen_roca}
            # remover las oleadas ya usadas
            spawn_plan = [p for p in spawn_plan if p[0] > lock_timer]

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
    # Clamp definitivo para fondo day (nivel 1): no pasar de 19400
    if fondo_elegido == 0:
        camera_x = min(camera_x, 19400)
    # Clamp global para todos los niveles: no pasar del límite del nivel
    camera_x = min(camera_x, limite_camara - 600)

    # Aplicar bloqueo mientras dure: fijar cámara y evitar avanzar a la derecha (con transición suave)
    if lock_active:
        lock_timer += dt
        if camera_locked_fixed and fondo_elegido == 0:
            # Nivel 1: cámara fija en 19400 y clamp sonic en 19999
            camera_x = 19400
            if sonic.x > 19999:
                sonic.x = 19999
        else:
            # Transición suave de cámara hacia lock_camera_x para evitar tirones
            lerp_factor = min(1.0, dt * 8.0)  # factor de suavizado
            camera_x = camera_x + (lock_camera_x - camera_x) * lerp_factor
            # Limitar avance del jugador al borde derecho del lock
            max_sonic_x = lock_camera_x + 600
            if sonic.x > max_sonic_x:
                sonic.x = max_sonic_x
        # Clamp también durante lock en fondo day
        if fondo_elegido == 0:
            camera_x = min(camera_x, 19400)
        # Clamp global durante lock: no pasar del límite del nivel
        camera_x = min(camera_x, limite_camara - 600)
        # Liberar al terminar
        if lock_timer >= lock_duration:
            lock_active = False
            camera_locked_fixed = False
            # Reenganchar la cámara con lógica de plantado para evitar salto brusco
            plantada = True
            camera_planted_x = max(0, int(sonic.x - 10))

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

    # 2. Dibujar el Sol/Luna (solo si estás en la zona 0)
    if nueva_zona == 0:
        # La posición en pantalla es la posición del mundo menos la cámara
        sol_draw_x = sol_world_x - camera_x
        # Si la imagen está dentro de la pantalla (opcional)
        if -sol1.get_width() < sol_draw_x < 1200:
            screen.blit(sol1, (sol_draw_x, sol_world_y)) 

    # 2.5. Dibujar Múltiples Espinas y Comprobar Colisiones
    
    for espina_rect in espinas_rects[:]:
        espinas_draw_x = espina_rect.x - camera_x
        
        # Optimización: Solo dibujar si está en la pantalla
        if -espina_rect.width < espinas_draw_x < screen.get_width():
            screen.blit(espinas, (espinas_draw_x, espina_rect.y))
        
        # --- Lógica de Colisión ---
        if sonic.colliderect(espina_rect):
            # Lógica para manejar el daño ambiental (espinas)
            if invulnerable == True:
                sonic.x = sonic.x - 100  # Retroceder un poco al ser golpeado
            if not invulnerable and not dead:
                if ring_count > 0:
                    print("¡Sonic fue golpeado por pínchos, Pierde rings.")
                    ring_count = 0
                    invulnerable = True
                    invulnerability_timer = 0.0
                    hurt = True
                    hurt_timer = 0.0
                    sonic.x = sonic.x - 200 if mirando_derecha else sonic.x + 200  # Retroceder un poco al ser golpeado
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
    
    # --- 3. DIBUJAR ROCAS (CORREGIDO) ---
    for roca_id, roca_rect, roca_image in rocas_list[:]:
        roca_draw_pos = (roca_rect.x - camera_x, roca_rect.y)
        
        # Dibujado
        if -roca_rect.width < roca_draw_pos[0] < screen.get_width() and roca_draw_pos[1] < screen.get_height():
            screen.blit(roca_image, roca_draw_pos)

    # 3.5. Dibujar Proyectiles de Avispa
    for proyectil_data in proyectiles_avispa_list[:]:
        proyectil_rect = proyectil_data['rect']
        proyectil_draw_pos = (proyectil_rect.x - camera_x, proyectil_rect.y)
        
        # Dibujar si está en pantalla
        if -proyectil_rect.width < proyectil_draw_pos[0] < screen.get_width():
            # Asumo que 'proyectil' es la imagen importada
            screen.blit(proyectil, proyectil_draw_pos)

    # 4. Dibujar Sonic (capa media)
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
        import vent_inicio
        running = False

    if fondo_elegido == 1 and sonic.x > 40000:
        print("¡Felicidades! Has completado el nivel 2.")
        volverabrir = 2
        import vent_inicio
        running = False
    if fondo_elegido == 2 and sonic.x > 60000:
        print("¡Felicidades! Has completado el nivel 3.")
        volverabrir = 3
        import vent_inicio
        running = False
    if fondo_elegido == 3 and sonic.x > 80000:
        print("¡Felicidades! Has completado el nivel 4.")
        volverabrir = 4
        import vent_inicio
        running = False

# ---------- Salir: cerrar Arduino si está abierto ----------
try:
    if arduino and arduino.is_open:
        arduino.close()
except Exception:
    pass

pygame.quit()