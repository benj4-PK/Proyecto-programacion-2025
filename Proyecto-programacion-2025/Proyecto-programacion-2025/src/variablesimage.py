import pygame
import sys
import os

def ruta(relativa):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relativa)
    return os.path.join(os.path.dirname(__file__), relativa)

# Inicializar Pygame
#sprites fondos y rings
rings = pygame.image.load(ruta("sprites/anillado2.png"))
rings = pygame.transform.scale(rings, (65, 65))
anilloimagen = pygame.image.load(ruta("sprites/anillado2.png"))
anilloimagen = pygame.transform.scale(anilloimagen, (35, 35))
enemigoimagen = pygame.image.load(ruta("sprites/Sprites_enemies/baknik.png"))
enemigoimagen = pygame.transform.scale(enemigoimagen, (35, 35))
fondo_day = pygame.image.load(ruta("sprites/day.jpg"))
fondo_day = pygame.transform.scale(fondo_day, (1200, 700))
fondo_day2 = pygame.image.load(ruta("sprites/day(sinsol).jpg"))
fondo_day2 = pygame.transform.scale(fondo_day2, (1200, 700))
fondo_midnight = pygame.image.load(ruta("sprites/midnight.jpg"))
fondo_midnight = pygame.transform.scale(fondo_midnight, (1200, 700))
fondo_midnight2 = pygame.image.load(ruta("sprites/midnight(sinsol).jpg"))
fondo_midnight2 = pygame.transform.scale(fondo_midnight2, (1200, 700))
fondo_seminight = pygame.image.load(ruta("sprites/casinoche.jpg"))
fondo_seminight = pygame.transform.scale(fondo_seminight, (1200, 700))
fondo_seminight2 = pygame.image.load(ruta("sprites/casinoche(sinsol).jpg"))
fondo_seminight2 = pygame.transform.scale(fondo_seminight2,(1200, 700))
fondo_night = pygame.image.load(ruta("sprites/night.jpg"))
fondo_night = pygame.transform.scale(fondo_night, (1200, 700))
fondo_night2 = pygame.image.load(ruta("sprites/night(sinmoon).jpg"))
fondo_night2 = pygame.transform.scale(fondo_night2, (1200, 700))
#sprites sonic
sprite_sonic = pygame.image.load(ruta("sprites/sprites_character/idle_character.png"))
sprite_sonic = pygame.transform.scale(sprite_sonic, (120, 120))
sprite_muerte = pygame.image.load(ruta("sprites/sprites_character/death.png"))
sprite_muerte = pygame.transform.scale(sprite_muerte, (120, 120))
sprite_damage = pygame.image.load(ruta("sprites/sprites_character/daño/HurtFrame1.png"))
sprite_damage = pygame.transform.scale(sprite_damage, (120, 120))
sprite_damage2 = pygame.image.load(ruta("sprites/sprites_character/daño/HurtFrame2.png"))
sprite_damage2 = pygame.transform.scale(sprite_damage2, (120, 120))
sprite_damage3 = pygame.image.load(ruta("sprites/sprites_character/daño/HurtFrame3.png"))
sprite_damage3 = pygame.transform.scale(sprite_damage3, (120, 120))
sprite_damage4 = pygame.image.load(ruta("sprites/sprites_character/daño/HurtFrame4.png"))
sprite_damage4 = pygame.transform.scale(sprite_damage4, (120, 120))

#sprites eu bata
sprite_eu_bata = pygame.image.load(ruta("sprites/eu_bata.png"))
sprite_eu_bata = pygame.transform.scale(sprite_eu_bata, (400, 120))
# Sprites enemigos
baknik = pygame.image.load(ruta("sprites/Sprites_enemies/baknik.png"))
baknik = pygame.transform.scale(baknik, (160, 100))  # Tamaño más pequeño

baknik2 = pygame.image.load(ruta("sprites/Sprites_enemies/baknik2.png"))
baknik2 = pygame.transform.scale(baknik2, (160, 100))

baknik3 = pygame.image.load(ruta("sprites/Sprites_enemies/baknik3.png"))
baknik3 = pygame.transform.scale(baknik3, (160, 100))

avispa = pygame.image.load(ruta("sprites/Sprites_enemies/avispa.png"))
avispa = pygame.transform.scale(avispa, (160, 100))  # Tama

avispa2 = pygame.image.load(ruta("sprites/Sprites_enemies/avispa2.png"))
avispa2 = pygame.transform.scale(avispa2, (160, 100))

avispa3 = pygame.image.load(ruta("sprites/Sprites_enemies/avispa3.png"))
avispa3 = pygame.transform.scale(avispa3, (160, 100))

avispa4 = pygame.image.load(ruta("sprites/Sprites_enemies/avispa4.png"))
avispa4 = pygame.transform.scale(avispa4, (160, 100))

proyectil = pygame.image.load(ruta("sprites/avispaproyectil.png"))
proyectil = pygame.transform.scale(proyectil, (50, 20))

crab = pygame.image.load(ruta("sprites/Sprites_enemies/crab.png"))
crab = pygame.transform.scale(crab, (150, 100))      # Mismo tamaño que baknik

crab2 = pygame.image.load(ruta("sprites/Sprites_enemies/crab2.png"))
crab2 = pygame.transform.scale(crab2, (150, 100))

crab3 = pygame.image.load(ruta("sprites/Sprites_enemies/crab3.png"))
crab3 = pygame.transform.scale(crab3, (150, 100))

pez = pygame.image.load(ruta("sprites/Sprites_enemies/pez.png"))
pez = pygame.transform.scale(pez, (140, 100))
#sprites obstaculos

espinas = pygame.image.load(ruta("sprites/spike.png"))
espinas = pygame.transform.scale(espinas, (100, 90))

roca1 = pygame.image.load(ruta("sprites/rock/roca1.png"))
roca1 = pygame.transform.scale(roca1, (120, 100))

roca2 = pygame.image.load(ruta("sprites/rock/roca2.png"))
roca2 = pygame.transform.scale(roca2, (120, 100))

roca3 = pygame.image.load(ruta("sprites/rock/roca3.png"))
roca3 = pygame.transform.scale(roca3, (120, 100))

#sprites lunas y soles
sol1 = pygame.image.load(ruta("sprites/sol1.png"))
sol1 = pygame.transform.scale(sol1, (850, 800))
sol_world_x = 1510 
sol_world_y = -70

atardecer = pygame.image.load(ruta("sprites/atardecer.png"))
atardecer = pygame.transform.scale(atardecer, (920, 920))

luna = pygame.image.load (ruta("sprites/luna.png"))
luna = pygame.transform.scale(luna, (120, 120))

solnight = pygame.image.load(ruta("sprites/seminoche.png"))
solnight = pygame.transform.scale(solnight, (120, 120))

eggman = pygame.image.load(ruta("sprites/sprite_mr.eggman/eggman.png"))
eggman = pygame.transform.scale(eggman, (200, 200))

eggman_attack = pygame.image.load(ruta("sprites/sprite_mr.eggman/eggman2.png"))
eggman_attack = pygame.transform.scale(eggman_attack, (200, 200))

eggman_attack2 = pygame.image.load(ruta("sprites/sprite_mr.eggman/eggman3.png"))
eggman_attack2 = pygame.transform.scale(eggman_attack2, (200, 200))