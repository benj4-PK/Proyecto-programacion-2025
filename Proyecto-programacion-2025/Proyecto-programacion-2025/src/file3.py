import os
import pygame
import vent_inicio
import config
import sys

def ruta(relativa):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relativa)
    return os.path.join(os.path.dirname(__file__), relativa)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

pygame.init()
fondo = pygame.image.load(ruta("sprites/opciones.jpg"))
fondo = pygame.transform.scale(fondo, (1200, 700))
fondo2 = pygame.image.load(ruta("sprites/options.jpg"))
fondo2 = pygame.transform.scale(fondo2, (1200, 700))
screen = pygame.display.set_mode((1200, 700))
pygame.display.set_caption("Menu Principal")
regresar = pygame.image.load(ruta("sprites/back.png"))
regresar = pygame.transform.scale(regresar, (70, 50))



clock = pygame.time.Clock()
sonido = 4

Idioma = 0
pygame.mixer.init()
# Cargar la música
pygame.mixer.music.load(ruta("musica\music_menu.mp3"))

# Reproducir la música en bucle
pygame.mixer.music.play(-1)

# Establecer un volumen inicial (por ejemplo, 50%)
pygame.mixer.music.set_volume(config.Music_Volumen)


# --- DEFINICIÓN DE BOTONES ---

# Botón JUGAR (superior)
ANCHO_BOTON_Opcion = 167
ALTO_BOTON = 40
X_BOTON = 192
Y_BOTON_JUGAR = 335  # Borde superior en y = 300

# Botón NUEVO (inferior)
Y_BOTON_NUEVO = Y_BOTON_JUGAR 
X_BOTON_NUEVO = X_BOTON + ANCHO_BOTON_Opcion + 40

Y_BOTON_NUEVO2 = Y_BOTON_NUEVO 
X_BOTON_NUEVO2 = X_BOTON + ANCHO_BOTON_Opcion * 2 + 88

Y_BOTON_NUEVO3 = Y_BOTON_NUEVO2 
X_BOTON_NUEVO3 = X_BOTON + ANCHO_BOTON_Opcion * 3 + 136

# Crear rect del botón JUGAR con la imagen


# --- imagen para el botón NUEVO: usar midnight.jpg ---
Boton_nulo = pygame.image.load(ruta("sprites/midnight.jpg"))
Boton_nulo = pygame.transform.scale(Boton_nulo, (ANCHO_BOTON_Opcion, ALTO_BOTON))
Boton_nulo_rect = Boton_nulo.get_rect(topleft=(X_BOTON, Y_BOTON_NUEVO))

Boton_bajo = pygame.image.load(ruta("sprites/casinoche.jpg"))
Boton_bajo = pygame.transform.scale(Boton_bajo, (ANCHO_BOTON_Opcion, ALTO_BOTON))
Boton_bajo_rect = Boton_bajo.get_rect(topleft=(X_BOTON_NUEVO, Y_BOTON_NUEVO2))

Boton_Medio = pygame.image.load(ruta("sprites/night.jpg"))
Boton_Medio = pygame.transform.scale(Boton_Medio, (ANCHO_BOTON_Opcion, ALTO_BOTON))
Boton_Medio_rect = Boton_Medio.get_rect(topleft=(X_BOTON_NUEVO2, Y_BOTON_NUEVO3))

Boton_Alto = pygame.image.load(ruta("sprites/diaprueba0.jpg"))
Boton_Alto = pygame.transform.scale(Boton_Alto, (ANCHO_BOTON_Opcion, ALTO_BOTON))
Boton_Alto_rect = Boton_Alto.get_rect(topleft=(X_BOTON_NUEVO3, Y_BOTON_JUGAR))

boton_español = pygame.image.load(ruta("sprites/night.jpg"))
boton_español = pygame.transform.scale(boton_español, (ANCHO_BOTON_Opcion, ALTO_BOTON))
boton_español_rect = boton_español.get_rect(topleft=(X_BOTON + 208, Y_BOTON_JUGAR + 205.5))

boton_ingles = pygame.image.load(ruta("sprites/night.jpg"))
boton_ingles = pygame.transform.scale(boton_ingles, (ANCHO_BOTON_Opcion, ALTO_BOTON))
boton_ingles_rect = boton_ingles.get_rect(topleft=(X_BOTON_NUEVO + 250, Y_BOTON_NUEVO + 205.5))

regresar_rect = regresar.get_rect(topleft=(0, 0))
# Bucle principal del juego
ejecutando = True
while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

        # detectar clics con evento para evitar múltiples triggers
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if Boton_Alto_rect.collidepoint(evento.pos):
                print("Clic en JUGAR")
                sonido = 4
                if sonido == 4:
                    config.Music_Volumen = 0.5 # <--- CAMBIO CLAVE: Modificar la variable del módulo
                else:
                    config.Music_Volumen = 0.5
                
            # nuevo: usar la imagen como botón para el segundo botón
            if Boton_bajo_rect.collidepoint(evento.pos):
                print("Clic en NUEVO BOTÓN")
                sonido = 2
                if sonido == 2:
                    config.Music_Volumen = 0.2 # <--- CAMBIO CLAVE: Modificar la variable del módulo
                else:
                    config.Music_Volumen = 0.5
                
                
            if Boton_Medio_rect.collidepoint(evento.pos):
                print("Clic en NUEVO BOTÓN 2")
                sonido = 3
                if sonido == 3:
                    config.Music_Volumen = 0.35 # <--- CAMBIO CLAVE: Modificar la variable del módulo
                else:
                    config.Music_Volumen = 0.5
                
                
            if Boton_nulo_rect.collidepoint(evento.pos):
                print("Clic en NUEVO BOTÓN 3")
                sonido = 1
                if sonido == 1:
                    config.Music_Volumen = 0 # <--- CAMBIO CLAVE: Modificar la variable del módulo
                else:
                    config.Music_Volumen = 0.5
            if boton_español_rect.collidepoint(evento.pos):
                print("Clic en ESPAÑOL")
                config.Idioma = 0
            if boton_ingles_rect.collidepoint(evento.pos):
                print("Clic en INGLES")
                config.Idioma = 1
            if regresar_rect.collidepoint(evento.pos):
                print("Clic en REGRESAR AL MENU")
                pygame.mixer.music.stop()
                ejecutando = False 
                try:
                    import vent_inicio
                except ImportError:
                    print("Error: No se puede importar vent_inicio.py. Asegúrate de que existe.")
                    pygame.quit()
                    break
    if sonido == 1:
        config.MUSIC_VOLUME = 0
    elif sonido == 2:
        config.MUSIC_VOLUME = 0.2
    elif sonido == 3:
        config.MUSIC_VOLUME = 0.35
    elif sonido == 4:
        config.MUSIC_VOLUME = 0.5            
    pygame.mixer.music.set_volume(config.MUSIC_VOLUME)            

    # Dibujar fondo y los botones como imagenes
    if config.Idioma == 0:
        fondo_actual = fondo
    else:
        fondo_actual = fondo2
    screen.blit(fondo_actual, (0, 0))
    screen.blit(regresar, regresar_rect)
    #screen.blit(Boton_Alto, Boton_Alto_rect)  # imagen usada como botón JUGAR
    #screen.blit(Boton_nulo, Boton_nulo_rect)  # imagen midnight como botón NUEVO
   #screen.blit(Boton_bajo, Boton_bajo_rect)  
    #screen.blit(Boton_Medio, Boton_Medio_rect)  
    #screen.blit(boton_español, boton_español_rect)
    #screen.blit(boton_ingles, boton_ingles_rect)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()