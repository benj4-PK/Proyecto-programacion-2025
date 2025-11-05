import os
import pygame

os.chdir(os.path.dirname(os.path.abspath(__file__)))

pygame.init()
screen = pygame.display.set_mode((1200, 700))
pygame.display.set_caption("Menu Principal")

fondo = pygame.image.load("../sprites/fondo_menu.jpg")
fondo = pygame.transform.scale(fondo, (1200, 700))
clock = pygame.time.Clock()
music_vol = 0.5
pygame.mixer.init()
# Cargar la música
pygame.mixer.music.load("..\musica\music_menu.mp3")

# Reproducir la música en bucle
pygame.mixer.music.play(-1)

# Establecer un volumen inicial (por ejemplo, 50%)
pygame.mixer.music.set_volume(music_vol)

