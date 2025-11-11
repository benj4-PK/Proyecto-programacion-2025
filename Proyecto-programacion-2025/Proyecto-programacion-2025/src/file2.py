import os
import pygame
import config
import sys

def ruta(relativa):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relativa)
    return os.path.join(os.path.dirname(__file__), relativa)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

pygame.init()
fondo = pygame.image.load(ruta("sprites/fondos.jpg"))
fondo = pygame.transform.scale(fondo, (1200, 700))
fondo2 = pygame.image.load(ruta("sprites/level.jpg"))
fondo2 = pygame.transform.scale(fondo2, (1200, 700))

screen = pygame.display.set_mode((1200, 700))
pygame.display.set_caption("Menu Principal")



imagen_analisis = pygame.image.load(ruta("sprites/diaprueba0.jpg"))
imagen_analisis = pygame.transform.scale(imagen_analisis, (150, 90))
clock = pygame.time.Clock()
music_vol = 0.5
fondo_elegido = 1
pygame.mixer.init()
# Cargar la música
pygame.mixer.music.load(ruta("musica\music_menu.mp3"))

# Reproducir la música en bucle
pygame.mixer.music.play(-1)

# Establecer un volumen inicial (por ejemplo, 50%)
pygame.mixer.music.set_volume(config.Music_Volumen)


# --- DEFINICIÓN DE BOTONES ---

# Botón JUGAR (superior)
ANCHO_BOTON_Opcion = 150
ALTO_BOTON = 90
X_BOTON = 610
Y_BOTON_JUGAR = 167  # Borde superior en y = 300

# Botón NUEVO (inferior)
Y_BOTON_NUEVO = Y_BOTON_JUGAR + ALTO_BOTON + 25.5  # 300 + 160 + 20 = 480

Y_BOTON_NUEVO2 = Y_BOTON_NUEVO + ALTO_BOTON + 25.5  # 300 + 90 + 20 = 410

Y_BOTON_NUEVO3 = Y_BOTON_NUEVO2 + ALTO_BOTON + 25.5  # 167 + 90 + 20 = 277

# Crear rect del botón JUGAR con la imagen
imagen_rect = imagen_analisis.get_rect(topleft=(X_BOTON, Y_BOTON_JUGAR))

# --- imagen para el botón NUEVO: usar midnight.jpg ---
imagen_nuevo = pygame.image.load(ruta("sprites/midnight.jpg"))
imagen_nuevo = pygame.transform.scale(imagen_nuevo, (ANCHO_BOTON_Opcion, ALTO_BOTON))
imagen_nuevo_rect = imagen_nuevo.get_rect(topleft=(X_BOTON, Y_BOTON_NUEVO))

imagen_nuevo2 = pygame.image.load(ruta("sprites/casinoche.jpg"))
imagen_nuevo2 = pygame.transform.scale(imagen_nuevo2, (ANCHO_BOTON_Opcion, ALTO_BOTON))
imagen_nuevo_rect2 = imagen_nuevo2.get_rect(topleft=(X_BOTON, Y_BOTON_NUEVO2))

imagen_nuevo3 = pygame.image.load(ruta("sprites/night.jpg"))
imagen_nuevo3 = pygame.transform.scale(imagen_nuevo3, (ANCHO_BOTON_Opcion, ALTO_BOTON))
imagen_nuevo_rect3 = imagen_nuevo3.get_rect(topleft=(X_BOTON, Y_BOTON_NUEVO3))

# Bucle principal del juego
ejecutando = True
while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

        # detectar clics con evento para evitar múltiples triggers
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if imagen_rect.collidepoint(evento.pos):
                print("Clic en JUGAR")
                pygame.mixer.music.stop()
                fondo_elegido = 0
                import file1
                ejecutando = False
            # nuevo: usar la imagen como botón para el segundo botón
            if imagen_nuevo_rect.collidepoint(evento.pos):
                print("Clic en NUEVO BOTÓN")
                pygame.mixer.music.stop()
                fondo_elegido = 1
                import file1
                ejecutando = False
            if imagen_nuevo_rect2.collidepoint(evento.pos):
                print("Clic en NUEVO BOTÓN 2")
                pygame.mixer.music.stop()
                fondo_elegido = 2
                import file1
                ejecutando = False
            if imagen_nuevo_rect3.collidepoint(evento.pos):
                print("Clic en NUEVO BOTÓN 3")
                pygame.mixer.music.stop()
                fondo_elegido = 3
                import file1
                ejecutando = False

    # Dibujar fondo y los botones como imagenes
    if config.Idioma == 0:
        fondo_actual = fondo
    else:
        fondo_actual = fondo2
    screen.blit(fondo_actual, (0, 0))
    screen.blit(imagen_analisis, imagen_rect)  # imagen usada como botón JUGAR
    screen.blit(imagen_nuevo, imagen_nuevo_rect)  # imagen midnight como botón NUEVO
    screen.blit(imagen_nuevo2, imagen_nuevo_rect2)  
    screen.blit(imagen_nuevo3, imagen_nuevo_rect3)  

    pygame.display.flip()
    clock.tick(30)

pygame.quit()