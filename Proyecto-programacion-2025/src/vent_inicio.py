import os
import pygame

# Inicializar aquí, pero la lógica principal en la función
os.chdir(os.path.dirname(os.path.abspath(__file__)))

pygame.init()

# Variables que necesita file1 al importarse
music_vol = 0.5 

def menu_principal(start_level=0):
    """
    Muestra el menú principal y maneja las transiciones.
    'start_level' indica qué nivel se cargará al presionar JUGAR.
    """
    global music_vol
    
    # 1. SETUP DEL MENÚ
    music_vol = 0.5 # Reinicia el volumen
    screen = pygame.display.set_mode((1200, 700))
    pygame.display.set_caption("Menu Principal")

    fondo = pygame.image.load("../sprites/fondo_menu.jpg")
    fondo = pygame.transform.scale(fondo, (1200, 700))
    clock = pygame.time.Clock()
    
    try:
        pygame.mixer.init()
        pygame.mixer.music.load("..\musica\music_menu.mp3")
        pygame.mixer.music.set_volume(music_vol)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Error cargando música del menú: {e}")

    # --- DEFINICIÓN DE BOTONES ---
    ANCHO_BOTON = 350
    ALTO_BOTON = 90
    X_BOTON = 430
    Y_BOTON_JUGAR = 300 
    Y_BOTON_NUEVO = Y_BOTON_JUGAR + ALTO_BOTON + 20 

    # 2. BUCLE DEL MENÚ
    ejecutando = True
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

        screen.blit(fondo, (0, 0))

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        # --- LÓGICA DEL BOTÓN JUGAR (superior) ---
        if X_BOTON <= mouse_pos[0] <= X_BOTON + ANCHO_BOTON and \
           Y_BOTON_JUGAR <= mouse_pos[1] <= Y_BOTON_JUGAR + ALTO_BOTON:
            if mouse_click[0] == 1:  # clic izquierdo
                print(f"Clic en JUGAR. Cargando Nivel: {start_level + 1}") 
                pygame.mixer.music.stop()
                ejecutando = False 
                
                # Importamos el archivo del juego
                try:
                    import file1 
                except ImportError:
                    print("Error: No se puede importar file1.py. Asegúrate de que existe.")
                    pygame.quit()
                    return

                # LLAMADA CLAVE: Usamos el nivel actual (start_level)
                next_action = file1.jugar_nivel(start_level) 
                
                # Manejar el resultado de jugar_nivel
                if isinstance(next_action, int):
                    # El jugador completó el nivel N. next_action es el índice N+1
                    print(f"Nivel {start_level + 1} completado. Iniciando menú para Nivel {next_action + 1}.")
                    # Recursivamente llamamos al menú con el nuevo nivel
                    return menu_principal(next_action) 
                elif next_action == "MENU":
                    # El jugador murió o presionó ESC. Volvemos al nivel 0 (Nuevo juego) o al último nivel
                    # Para simplificar el "Continue", simplemente reiniciamos el menú con el nivel 0.
                    print("Volviendo al menú principal (Nuevo Juego).")
                    return menu_principal(0)
                elif next_action == "QUIT":
                    return 

        # --- LÓGICA DEL SEGUNDO BOTÓN (inferior - asume que es un menú de opciones/NUEVO JUEGO) ---
        if X_BOTON <= mouse_pos[0] <= X_BOTON + ANCHO_BOTON and \
           Y_BOTON_NUEVO <= mouse_pos[1] <= Y_BOTON_NUEVO + ALTO_BOTON:
            if mouse_click[0] == 1:  # clic izquierdo
                print("Iniciando Nuevo Juego (Nivel 1)") 
                pygame.mixer.music.stop()
                ejecutando = False 
                # Si es un botón de Nuevo Juego, reiniciamos el flujo del menú desde el nivel 0
                return menu_principal(0)

        pygame.display.flip()
        clock.tick(30)
    
    # Al salir del bucle (ejecutando = False)
    pygame.quit()
    
# --- Ejecución inicial ---
if __name__ == "__main__":
    menu_principal(0) # Siempre comienza en el menú con el nivel 0 seleccionado