import pygame, gs, assets

pygame.init()

# Pygame setup
WIDTH, HEIGHT, FPS = 1280, 960, 60
surface = pygame.display.set_mode((WIDTH, HEIGHT), vsync = 1)
assets.load_assets()
pygame.display.set_caption("Hallowtale")
pygame.display.set_icon(assets.images["favicon"])
clock = pygame.time.Clock()

# Game loop setup
current_state = gs.menu_gs()
 
# Game loop
running = True
while running:
    # Handling events and state changes
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
    new_state = current_state.handle_events(events)
    if new_state is not None:
        current_state = new_state
    # Update and state changes
    dt = clock.tick(FPS) / 1000
    new_state = current_state.update(dt)
    if new_state is not None:
        current_state = new_state
    # Draw
    surface.fill((0, 0, 0))
    current_state.draw(surface)
    pygame.display.flip()

pygame.quit()