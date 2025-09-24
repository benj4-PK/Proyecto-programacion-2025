import pygame

pygame.init()

# crear ventana
screen = pygame.display.set_mode((1200, 700))
pygame.display.set_caption("Menu Principal")
pygame.display.set_icon(pygame.image.load("sprites/sprite_icono_prueba.png"))
fondo = pygame.image.load("sprites/fondo_menu.png")
fondo = pygame.transform.scale(fondo, (1200, 700))
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(fondo, (0, 0))  # Dibuja el fondo
    pygame.display.flip()       # Actualiza la pantalla

    #btn jugar
    pygame.draw.rect(screen, (168, 230, 29), (485, 400, 263, 115))  # Dibuja un rectángulo verde
    font = pygame.font.Font(None, 46)
    text = font.render("Jugar", True, (0, 0, 0 ))
    screen.blit(text, (580, 440))  # Dibuja el texto en el rectángulo
    pygame.display.flip()
    clock.tick(5)

    #redirigir a la ventana del juego
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()
    if 550 <= mouse_pos[0] <= 650 and 300 <= mouse_pos[1] <= 350:
        if mouse_click[0] == 1:  # Si se hace clic izquierdo
            import file1  # Importa la ventana del juego
            running = False  # Cierra la ventana del menú

pygame.quit()

