import os
import time
import random
import pygame

# Inicializar Pygame


# Cargar sprite
baknik = pygame.image.load("../sprites/Sprites_enemies/baknik.png")
baknik = pygame.transform.scale(baknik, (160, 100))  # Tamaño más pequeño

baknik2 = pygame.image.load("../sprites/Sprites_enemies/baknik2.png")
baknik2 = pygame.transform.scale(baknik2, (160, 100))

baknik3 = pygame.image.load("../sprites/Sprites_enemies/baknik3.png")
baknik3 = pygame.transform.scale(baknik3, (160, 100))

avispa = pygame.image.load("../sprites/Sprites_enemies/avispa.png")
avispa = pygame.transform.scale(avispa, (65, 65))  # Tama

crab = pygame.image.load("../sprites/Sprites_enemies/crab.png")
crab = pygame.transform.scale(crab, (150, 100))      # Mismo tamaño que baknik

crab2 = pygame.image.load("../sprites/Sprites_enemies/crab2.png")
crab2 = pygame.transform.scale(crab2, (150, 100))

crab3 = pygame.image.load("../sprites/Sprites_enemies/crab3.png")
crab3 = pygame.transform.scale(crab3, (150, 100))

pez = pygame.image.load("../sprites/Sprites_enemies/pez.png")
pez = pygame.transform.scale(pez, (140, 100))

espinas = pygame.image.load("../sprites/spike.png")
espinas = pygame.transform.scale(espinas, (50, 50))

sol1 = pygame.image.load("../sprites/sol1.png")
sol1 = pygame.transform.scale(sol1, (120, 120))

atardecer = pygame.image.load("../sprites/atardecer.png")
atardecer = pygame.transform.scale(atardecer, (120, 120))

luna = pygame.image.load ("../sprites/luna.png")
luna = pygame.transform.scale(luna, (120, 120))

solnight = pygame.image.load("../sprites/seminoche.png")
solnight = pygame.transform.scale(solnight, (120, 120))