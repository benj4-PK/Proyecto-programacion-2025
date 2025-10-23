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



# --- DEFINICIÓN DE BOTONES ---

# Botón JUGAR (superior)
ANCHO_BOTON = 350
ALTO_BOTON = 90
X_BOTON = 430
Y_BOTON_JUGAR = 300 # Borde superior en y = 300

# Botón NUEVO (inferior)
# Su borde superior es 20 píxeles debajo del borde inferior del botón JUGAR.
# Borde inferior JUGAR = Y_BOTON_JUGAR + ALTO_BOTON = 300 + 90 = 390
# Borde superior NUEVO = 390 + 20 = 410
Y_BOTON_NUEVO = Y_BOTON_JUGAR + ALTO_BOTON + 20 # 300 + 90 + 20 = 410

# Bucle principal del juego
ejecutando = True
while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

    screen.blit(fondo, (0, 0))
    pygame.display.flip()
    clock.tick(30)

    # Detectar clic sobre los botones
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()

    # --- LÓGICA DEL BOTÓN JUGAR (superior) ---
    # Área: X_BOTON a X_BOTON + ANCHO_BOTON (430 a 780)
    # Área: Y_BOTON_JUGAR a Y_BOTON_JUGAR + ALTO_BOTON (300 a 390)
    if X_BOTON <= mouse_pos[0] <= X_BOTON + ANCHO_BOTON and \
       Y_BOTON_JUGAR <= mouse_pos[1] <= Y_BOTON_JUGAR + ALTO_BOTON:
        if mouse_click[0] == 1:  # clic izquierdo
            print("Clic en JUGAR") # Mensaje de prueba
            import file2
            # Importar file1 y salir del bucle
            ejecutando = False # Se corrigió la variable a 'ejecutando'

    # --- LÓGICA DEL SEGUNDO BOTÓN (inferior) ---
    # Área: X_BOTON a X_BOTON + ANCHO_BOTON (430 a 780)
    # Área: Y_BOTON_NUEVO a Y_BOTON_NUEVO + ALTO_BOTON (410 a 500)
    if X_BOTON <= mouse_pos[0] <= X_BOTON + ANCHO_BOTON and \
       Y_BOTON_NUEVO <= mouse_pos[1] <= Y_BOTON_NUEVO + ALTO_BOTON:
        if mouse_click[0] == 1:  # clic izquierdo
            print("Clic en NUEVO BOTÓN") # Mensaje de prueba
            import file3 # Llama al segundo archivo de juego/opciones
            # Importar file2 y salir del bucle
            ejecutando = False # Se corrigió la variable a 'ejecutando'

pygame.quit()