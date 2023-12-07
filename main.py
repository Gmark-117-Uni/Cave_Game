from Game import Game

if __name__=='__main__':
    # Create a game
    g = Game()

    # While game is running
    while g.running:
        # Display and navigate menus
        g.curr_menu.display()
        # Run game loop
        g.game_loop()
        # Reset keys after processing events
        g.reset_keys()
    