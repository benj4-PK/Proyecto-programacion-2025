import os
import pygame
import time
import random
from vent_inicio import music_vol
from file2 import fondo_elegido
from enemigos import baknik, baknik2, baknik3, avispa, crab, crab2, crab3, pez

# Cambia el directorio de trabajo al del script actual
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Iniciar Pygame
pygame.init()


#Función para iniciar la desactivación

# variable para saber que nivel puedes usar

# --- fondos y ventana (igual que tenías) ---
rings = pygame.image.load("../sprites/anillado2.png")
rings = pygame.transform.scale(rings, (65, 65))
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

# Iniciar audio y reproducir música de nivel durante el bucle principal
try:
    # Preinit reduce latencia; si ya inicializaste mixer en otro sitio, esto es seguro
    pygame.mixer.init()
    music_path = os.path.join("..", "musica", "music_level.mp3")
    if os.path.exists(music_path):
        pygame.mixer.music.load(music_path)
        vol = music_vol if 'music_vol' in globals() else 0.5
        try:
            pygame.mixer.music.set_volume(max(0.0, min(1.0, float(vol))))
        except Exception:
            pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)  # reproducir en bucle mientras corre el loop
    else:
        print("Aviso: no se encontró música de nivel en:", music_path)
except Exception as e:
    print("Error iniciando audio/música:", e)

mirando_derecha = False

# --- Sprite y dimensiones ---
sprite_sonic = pygame.image.load("../sprites/sprites_character/idle_character.png")
sprite_sonic = pygame.transform.scale(sprite_sonic, (120, 120))
SPRITE_W, SPRITE_H = sprite_sonic.get_size()
sprite_muerte = pygame.image.load("../sprites/sprites_character/death.png")
sprite_muerte = pygame.transform.scale(sprite_muerte, (120, 120))
sprite_damage = pygame.image.load("../sprites/sprites_character/daño/HurtFrame1.png")
sprite_damage = pygame.transform.scale(sprite_damage, (120, 120))
sprite_damage2 = pygame.image.load("../sprites/sprites_character/daño/HurtFrame2.png")
sprite_damage2 = pygame.transform.scale(sprite_damage2, (120, 120))
sprite_damage3 = pygame.image.load("../sprites/sprites_character/daño/HurtFrame3.png")
sprite_damage3 = pygame.transform.scale(sprite_damage3, (120, 120))
sprite_damage4 = pygame.image.load("../sprites/sprites_character/daño/HurtFrame4.png")
sprite_damage4 = pygame.transform.scale(sprite_damage4, (120, 120))

# eu_bata
sprite_eu_bata = pygame.image.load("../sprites/eu_bata.png")
sprite_eu_bata = pygame.transform.scale(sprite_eu_bata, (400, 120))

# --- Hitbox (usamos una rect pequeño para colisiones) ---
HITBOX_W = 50
HITBOX_H_STAND = 100
HITBOX_H_CROUCH = 100

# ===================================================================
# --- ANIMACIONES DE ENEMIGOS (Agrupación de Sprites) ---
# ===================================================================
ENEMY_ANIMATIONS = {
    # Usamos listas para los frames de animación de cada enemigo
    "baknik": [baknik, baknik2, baknik3], 
    "crab": [crab, crab2, crab3] 
    # Agrega 'avispa' y 'pez' si tienen más de un sprite
}

# Constante para la velocidad de la animación (cambia cada 0.15 segundos)
ENEMY_FRAME_DURATION = 0.15
# ===================================================================

# sonic = hitbox en coordenadas del MUNDO
sonic = pygame.Rect(700, 350 - HITBOX_H_STAND, HITBOX_W, HITBOX_H_STAND)  # iniciar dentro de day2

# Suelo en coordenadas del mundo (largo)
suelo_y_default = 320
suelo = pygame.Rect(-10000, suelo_y_default, 120000, 100)


# === NUEVAS VARIABLES PARA INVULNERABILIDAD ===
invulnerable = False
invulnerability_timer = 0.0
INVULNERABILITY_DURATION = 3.0 # Duración de 3 segundos
# Variables físicas
vel_y = 0
gravedad = 2400
vel_salto = -1100
# El valor inicial de vel_lateral es 1200, el control se hace en el bucle
vel_lateral = 1200
en_suelo = False

# Cámara
camera_x = 0
mostrar_bata = False
tiempo_bata = 0

# Variables para cámara plantada al entrar en una zona
zona_actual = None      # id de la zona en la que estamos
plantada = False        # si la cámara está plantada en la nueva zona
camera_planted_x = 0    # posición de cámara mientras está plantada

# Limita retrocesos: guarda la mayor zona alcanzada (no se puede volver a zonas anteriores)
max_zona_reached = -1

# ===============================================
# === NUEVAS VARIABLES PARA ESTADO DE MUERTE ===
dead = False      # Indica si Sonic está en el estado de muerte
death_timer = 0.0        # Temporizador para la duración de la animación de muerte
DEATH_DURATION = 3.0     # Duración en segundos que se muestra el sprite de muerte
death_music_played = False  # evita reproducir la música de muerte repetidamente
# ===============================================
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

# Lista para almacenar los rings
rings_list = []

# Función para generar rings aleatorios
def generate_rings(num_rings):
    for _ in range(num_rings):
        # Posición x entre el inicio y final de TODO el mapa (no solo day2)
        x = random.randint(600, 79400)  # Hasta el final del último fondo
        y = random.randint(100, suelo_y_default - 50)
        rings_list.append(pygame.Rect(x, y, 30, 30))

# Generar rings iniciales
generate_rings(100)  # Puedes ajustar el número

# Agregar después de la inicialización de pygame:
ring_count = 0
font = pygame.font.Font(None, 36)

# Listas para almacenar los enemigos
crabs_list = []
bakniks_list = []

# Variables para la física y movimiento de los enemigos
enemy_states = {}  # Diccionario para guardar estados de enemigos
enemy_id = 0  # Contador para generar IDs únicos

# Constantes para enemigos
ENEMY_VEL_LATERAL = 200
ENEMY_TIEMPO_CAMBIO = 2.0
ENEMY_GRAVEDAD = 2400

def generate_enemies(num_enemies):
    global enemy_id
    crabs_list.clear()
    bakniks_list.clear()
    
    # Generar enemigos para cada zona
    zonas_spawn = [
        (600, 20000),      # day2
        (20000, 40000),    # midnight2
        (40000, 60000),    # seminight2
        (60000, 80000)     # night2
    ]
    
    for zona_start, zona_end in zonas_spawn:
        for _ in range(num_enemies):
            
            # Crear Crab en esta zona
            x = random.randint(zona_start, zona_end)
            crab_rect = pygame.Rect(x, suelo_y_default - 65, 65, 65)
            enemy_id += 1
            crabs_list.append((enemy_id, crab_rect))
            enemy_states[enemy_id] = {
                'vel_y': 0,
                'vel_x': ENEMY_VEL_LATERAL,
                'timer': 0,
                # NUEVO: Estado de animación
                'type': 'crab', 
                'frame_index': 0,
                'frame_timer': 0.0
            }
            
            # Crear Baknik en esta zona
            x = random.randint(zona_start, zona_end)
            baknik_rect = pygame.Rect(x, suelo_y_default - 65, 65, 65)
            enemy_id += 1
            bakniks_list.append((enemy_id, baknik_rect))
            enemy_states[enemy_id] = {
                'vel_y': 0,
                'vel_x': ENEMY_VEL_LATERAL,
                'timer': 0,
                # NUEVO: Estado de animación
                'type': 'baknik', 
                'frame_index': 0,
                'frame_timer': 0.0
            }

# ===================================================================
# --- FUNCIÓN UPDATE_ENEMY MODIFICADA PARA ANIMACIÓN ---
# ===================================================================
def update_enemy(enemy_id, enemy_rect, dt):
    """
    Actualiza la posición y la animación de un enemigo.
    """
    state = enemy_states[enemy_id]
    
    # Actualizar timer y cambiar dirección si necesario
    state['timer'] += dt
    if state['timer'] >= ENEMY_TIEMPO_CAMBIO:
        state['timer'] = 0
        state['vel_x'] *= -1  # cambiar dirección

    # Aplicar movimiento lateral
    enemy_rect.x += state['vel_x'] * dt

    # Aplicar gravedad
    state['vel_y'] += ENEMY_GRAVEDAD * dt
    enemy_rect.y += state['vel_y'] * dt

    # Colisión con el suelo
    if enemy_rect.colliderect(suelo):
        enemy_rect.bottom = suelo.y
        state['vel_y'] = 0
        
    # Lógica de animación: Actualizar el frame de la animación
    state['frame_timer'] += dt
    if state['frame_timer'] >= ENEMY_FRAME_DURATION:
        state['frame_timer'] = 0
        
        # Obtener la lista de frames para el tipo de enemigo
        frames = ENEMY_ANIMATIONS.get(state['type'], [])
        
        if frames:
            # Pasar al siguiente frame en el ciclo
            state['frame_index'] = (state['frame_index'] + 1) % len(frames)
# ===================================================================

generate_enemies(10)

# --- FUNCIÓN DE COLISIÓN MODIFICADA ---
def handle_hit(enemy_id, enemy_list, estado):
    """Maneja la lógica cuando Sonic colisiona con un enemigo."""
    global ring_count, running, invulnerable, invulnerability_timer, dead, death_timer
    global hurt, hurt_timer
    if invulnerable == True:
        sonic.x = sonic.x - 100  # Retroceder un poco al ser golpeado
    
        

    # Si Sonic está saltando o dasheando, elimina el enemigo
    if estado in ["jump", "dash"]:
        enemy_list[:] = [enemy for enemy in enemy_list if enemy[0] != enemy_id]
        if enemy_id in enemy_states:
            del enemy_states[enemy_id]
        return

    # Si Sonic está invulnerable o muerto, ignorar el golpe
    if invulnerable or dead:
        return

    # Si tiene rings, los pierde: activar invulnerabilidad y animación hurt
    if ring_count > 0:
        print(f"¡Sonic fue golpeado! Pierde {ring_count} rings, pero sobrevive.")
        ring_count = 0
        invulnerable = True
        invulnerability_timer = 0.0
        # activar animación de daño
        hurt = True
        hurt_timer = 0.0
        return

    # Si no tiene rings, iniciar secuencia de muerte
    print("¡Game Over! Sonic fue golpeado sin rings. Iniciando secuencia de muerte.")
    dead = True
    death_timer = 0.0
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.stop()  # Detener música actual
        death_music_path = "../musica/sonicded.mp3"
        if os.path.exists(death_music_path):
            pygame.mixer.music.load(death_music_path)
            pygame.mixer.music.play(0)  # Reproducir una vez (no en loop)
            death_music_played = True
    except Exception as e:
        print(f"Error al reproducir música de muerte: {e}")
    except Exception:
        pass
    return

# === Animación hurt (daño) ===
HURT_DURATION = 3.0         # duración total en segundos (ajusta a gusto)
HURT_FRAMES = []
HURT_FRAME_COUNT = 4
HURT_FRAME_TIME = HURT_DURATION / max(1, HURT_FRAME_COUNT)
for i in range(1, HURT_FRAME_COUNT + 1):
    path = f"../sprites/daño/hurt{i}.png"
    if os.path.exists(path):
        img = pygame.image.load(path)
        img = pygame.transform.scale(img, (SPRITE_W, SPRITE_H))
    else:
        # placeholder semitransparente si falta la imagen
        img = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
        img.fill((255, 100, 100, 180))
    HURT_FRAMES.append(img)

hurt = False
hurt_timer = 0.0

# --- Bucle principal ---____________________________________________________________________________________________________
running = True
last_time = time.time()
while running:
    now = time.time()
    dt = now - last_time
    last_time = now
    pygame.mixer.init()
    
    # =========================================================
    # 🌟 MODIFICACIÓN 1: Control de Movimiento por Invulnerabilidad
    # Anulamos la velocidad lateral si Sonic es invulnerable.
    # =========================================================
    vel_lateral_base = 1200 
    
    if invulnerable:
        vel_lateral = 0
    else:
        vel_lateral = vel_lateral_base
        
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

    keys = pygame.key.get_pressed()

    # Movimiento lateral (x) — usar la hitbox (sonic)
    # vel_lateral ahora está controlado por el estado 'invulnerable' (0 o 1200)
    if keys[pygame.K_d]:
        sonic.x += int(vel_lateral * dt)
        mirando_derecha = True


    if keys[pygame.K_a]:
        sonic.x -= int(vel_lateral * dt)
        mirando_derecha = False # Añadido 'mirando_derecha = False' que faltaba
        if sonic.x < -600:
            sonic.x = -600
            if not mostrar_bata:
                mostrar_bata = True
                tiempo_bata = now
    
    # Elimina las líneas duplicadas de K_d y K_a que estaban aquí
    # if keys[pygame.K_d]: # Duplicado, eliminado
    #     sonic.x += int(vel_lateral * dt)
    #     mirando_derecha = True
    # if keys[pygame.K_a]: # Duplicado, eliminado
    #    sonic.x -= int(vel_lateral * dt)

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

    # === Lógica de Invulnerabilidad (Actualización de Timer) ===
    
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

    # =========================================================
    # 🌟 MODIFICACIÓN 2: Ajuste de velocidad por estado de movimiento
    # Solo ajustamos si NO es invulnerable para mantener la anulación.
    # =========================================================
    if not invulnerable:
        if estado == "walk": 
            vel_lateral = 1200 # Usamos el valor original 1200
        elif estado == "run":
            vel_lateral = 1600
        elif estado == "dash":
            vel_lateral = 1800 # 1600 + 200
        elif estado == "crouch":
            vel_lateral = 0
    # Si 'invulnerable' es True, vel_lateral permanece en 0 (forzado al inicio del loop).
    elif estado == "crouch":
         # Mantener el croutch para hitbox, pero la velocidad ya es 0
        vel_lateral = 0
    # Si 'invulnerable' es True y el estado NO es 'crouch', vel_lateral sigue siendo 0.


    # Cámara centrada en la hitbox
    if sonic.x < 600:
        camera_x = 0

    # --- Definir zonas (start, end) y elegir fondo según sonic.x ---
    zonas = [
        ("day2", 600, 20000),
        ("midnight2", 20000, 40000),
        ("seminight2", 40000, 60000),
        ("night2", 60000, 80000)
    ]

    # seleccionar zona directamente 
    nueva_zona = fondo_elegido
        #Modificar ESTOOOOOO PARA FONDOS

    # asignar fondo_actual y limite_camara según nueva_zona

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

    # actualizar la mayor zona alcanzada (solo cuando avanzamos a una zona con índice mayor)
    if nueva_zona is not None and nueva_zona > max_zona_reached:
        max_zona_reached = nueva_zona

    # si ya alcanzamos alguna zona, impedir que sonic retroceda por debajo del inicio de esa zona
    if max_zona_reached >= 0:
        min_x_allowed = zonas[max_zona_reached][1]
        if sonic.x < min_x_allowed:
            sonic.x = min_x_allowed

    # Si cambiamos de zona, marcamos la entrada (plantado)
    if nueva_zona != zona_actual:
        zona_actual = nueva_zona
        plantada = True
        camera_planted_x = max(0, int(sonic.x - 10))

    # Lógica de cámara cuando está plantada: mantenerla fija hasta que Sonic supere la mitad (600 px)
    if plantada:
        if sonic.x - camera_planted_x <= 600:
            camera_x = camera_planted_x
        else:
            # cuando supera la mitad, la cámara empieza a seguir a Sonic y se quita la plantada
            plantada = False
            camera_x = sonic.x - 600
    else:
        # Lógica normal: seguir a Sonic pero respetar límites de la zona
        if sonic.x <= 0:
            camera_x = 0
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

    # Actualizar timer de invulnerabilidad
    if invulnerable:
        invulnerability_timer += dt
        if invulnerability_timer >= INVULNERABILITY_DURATION:
            invulnerable = False
            invulnerability_timer = 0.0
    
    # Para hacer parpadear a Sonic cuando es invulnerable
    should_draw_sonic = True
    if invulnerable:
        should_draw_sonic = (invulnerability_timer * 10) % 1 > 0.5

    # Modificar la sección donde dibujas a Sonic
    if should_draw_sonic:
        # Si está invulnerable y en el primer segundo, mostrar animación de daño
        if invulnerable and invulnerability_timer <= 1.0:
            # Calcular qué frame de daño mostrar (4 frames en 1 segundo)
            damage_frame_index = int((invulnerability_timer * 4)) % 4
            damage_sprites = [sprite_damage, sprite_damage2, sprite_damage3, sprite_damage4]
            current_sprite = damage_sprites[damage_frame_index]
            
            # Voltear sprite si es necesario
            if not mirando_derecha:
                current_sprite = pygame.transform.flip(current_sprite, True, False)
                
            screen.blit(current_sprite, (sonic.x - camera_x, sonic.y))
        else:
            # Dibujo normal de Sonic
            screen.blit(imagen_actual, (sonic.x - camera_x, sonic.y))

    # Mostrar "eu_bata"
    if mostrar_bata:
        screen.blit(sprite_eu_bata, (sonic.x - camera_x, sonic.y - 140))
        if now - tiempo_bata > 1:
            mostrar_bata = False

    # Dibujar y verificar colisiones con rings
    for ring in rings_list[:]:  # Usamos una copia de la lista para poder modificarla
        ring_draw_pos = (ring.x - camera_x, ring.y)
        if -50 <= ring_draw_pos[0] <= 1250:  # Solo dibujamos los rings visibles en pantalla
            screen.blit(rings, ring_draw_pos)
            if sonic.colliderect(ring):
                rings_list.remove(ring)
                # Aquí puedes agregar un sonido o incrementar el contador de rings
                if ring_count < 100:  # Solo aumenta si es menor a 100
                    ring_count += 1
                    # Nota: La línea 'vel_lateral = (1200 * 0.02) + vel_lateral' parecía ser un error
                    # de lógica en el movimiento de Sonic al recoger rings, la mantengo
                    # pero asegúrate de que es lo que deseas.
                    # vel_lateral = (1200 * 0.02) + vel_lateral 

    # Dibujar el contador en la pantalla
    ring_text = font.render(f'Rings: {ring_count}', True, (255, 255, 0))
    screen.blit(ring_text, (50, 50))

    # ===================================================================
    # --- SECCIÓN CORREGIDA: Actualizar y dibujar enemigos animados ---
    # ===================================================================

    # Actualizar y dibujar enemigos CRABS
    for enemy_id, crab_rect in crabs_list[:]: # Usa una copia de la lista
        update_enemy(enemy_id, crab_rect, dt)
        crab_draw_pos = (crab_rect.x - camera_x, crab_rect.y)
        
        if -65 <= crab_draw_pos[0] <= 1265:
            state = enemy_states.get(enemy_id)
            
            if state and state['type'] == 'crab':
                # Obtener el frame actual del Crab
                frames = ENEMY_ANIMATIONS.get('crab', [crab])
                current_sprite = frames[state['frame_index']]
                
                # Voltear el sprite si va hacia la izquierda (vel_x < 0)
                if state['vel_x'] < 0:
                    current_sprite = pygame.transform.flip(current_sprite, True, False)
                
                # DIBUJAR el sprite animado
                screen.blit(current_sprite, crab_draw_pos)
            else:
                # Fallback: Dibujar el sprite estático original
                screen.blit(crab, crab_draw_pos)


            if sonic.colliderect(crab_rect):
                handle_hit(enemy_id, crabs_list, estado)

    # Actualizar y dibujar enemigos BAKNIKS
    for enemy_id, baknik_rect in bakniks_list[:]: # Usa una copia de la lista
        update_enemy(enemy_id, baknik_rect, dt)
        baknik_draw_pos = (baknik_rect.x - camera_x, baknik_rect.y)
        
        if -65 <= baknik_draw_pos[0] <= 1265:
            state = enemy_states.get(enemy_id)
            
            if state and state['type'] == 'baknik':
                # Obtener el frame actual del Baknik
                frames = ENEMY_ANIMATIONS.get('baknik', [baknik])
                current_sprite = frames[state['frame_index']]
                
                # Voltear el sprite si va hacia la izquierda (vel_x < 0)
                if state['vel_x'] < 0:
                    current_sprite = pygame.transform.flip(current_sprite, True, False)
                
                # DIBUJAR el sprite animado
                screen.blit(current_sprite, baknik_draw_pos)
            else:
                # Fallback: Dibujar el sprite estático original
                screen.blit(baknik, baknik_draw_pos)

            if sonic.colliderect(baknik_rect):
                handle_hit(enemy_id, bakniks_list, estado)

    # ===================================================================

    pygame.display.flip()
    clock.tick(30)
    


    if fondo_elegido == 0:
        if sonic.x > 20000:
            print("¡Felicidades! Has completado el nivel 1.")
            running = False
            

    if fondo_elegido == 1:
        if sonic.x > 40000:
            print("¡Felicidades! Has completado el nivel 2.")
            running = False
            
    if fondo_elegido == 2:
        if sonic.x > 60000:
            print("¡Felicidades! Has completado el nivel 3.")
            running = False
            
    if fondo_elegido == 3:
        if sonic.x > 80000:
            print("¡Felicidades! Has completado el nivel 4.")
            running = False

pygame.quit()

# Iniciar audio y reproducir música de fondo (seguro: comprueba archivos y captura errores)
try:
    # pre-inicializar antes de init para reducir latencia
    
    pygame.mixer.init()
    # Rutas candidatas (ajusta si tu mp3 tiene otro nombre)
    music_paths = [
        "../musica/music_level.mp3",
        "../musica/sonicded.mp3"
    ]
    music_path = next((p for p in music_paths if os.path.exists(p)), None)
    if music_path:
        pygame.mixer.music.load(music_path)
        # usar music_vol si existe, sino volumen por defecto 0.5
        vol = music_vol if 'music_vol' in globals() else 0.5
        try:
            pygame.mixer.music.set_volume(float(vol))
        except Exception:
            pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    else:
        print("Aviso: no se encontró archivo de música en ninguna ruta:", music_paths)
except Exception as e:
    print("Error al iniciar audio/música:", e)