import pygame
import numpy as np

DEFAULT_SPAWN_PERCENT = 0.2
SIZE_DISPLAY = 1000
SIZE_BOARD = 100
DISPLAY_COLOUR = (160,160,160)
BACKGROUND_COLOUR = (0,0,0)

# ------------------------------ Game functions ------------------------#

# returns total amount of alive neighbours given cell[i][j]
# (i-1,j-1) | (i,j-1) | (i+1,j-1)
# -------------------------------
# (i-1,j)   | (i,j)   | (i+1,j)
# -------------------------------
# (i-1,j+1) | (i,j+1) | (i+1,j-+1)
def aliveNeighbours(board, i, j):
    aliveNeighbours = 0
    for x in range(-1,2):
        for y in range(-1,2):
            if board[(i+x)%SIZE_BOARD,(j+y)%SIZE_BOARD] == 1 and not (x == 0 and y == 0):
                aliveNeighbours += 1
    return aliveNeighbours

# Call for cell[i][j] == 1
# and checks if should die based on:
# Any live cell without two or three live neighbours dies.
def shouldDie(board, i, j):
    alive = aliveNeighbours(board, i, j)
    return not(alive == 2 or alive == 3)

# Call for cell[i][j] == 0
# and checks if should revive based on:
# Any dead cell with three live neighbours becomes a live cell
def shouldRevive(board, i, j):
    alive = aliveNeighbours(board, i, j)
    return alive == 3

# Updates board based on rules below
# RULES: (from: https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life)
# Any live cell with two or three live neighbours survives.
# Any dead cell with three live neighbours becomes a live cell.
# All other live cells die in the next generation. Similarly, all other dead cells stay dead
def updateBoard(board):
    new_board = np.copy(board)
    size = board.shape
    for i in range(size[0]):
        for j in range(size[1]):
            if board[i][j] == 0:
                if shouldRevive(board, i, j):
                    new_board[i][j] = 1
            else:
                if shouldDie(board, i, j):
                    new_board[i][j] = 0
    return new_board

def getRandomBoard(percentage):
    percentAlive = percentage
    board = np.zeros((SIZE_BOARD**2))
    board[:int(SIZE_BOARD**2*percentAlive)] = 1
    np.random.shuffle(board)
    return board.reshape((SIZE_BOARD,SIZE_BOARD))

# ------------------------- Helper Functions --------------------------#

# Gets value of pygames key 
# if key is a number between 0,9 will return value
# else returns False
def getKeyNumber(keyValue):
    if 47 < keyValue < 58:
        return keyValue - 48
    if 1073741912 < keyValue < 1073741922:
        return keyValue - 1073741912
    if keyValue == 1073741922:
        return 0
    return False

# ------------------------------ UI functions ------------------------#

# Scales each cell to display board and calls display
# BACKGROUND_COLOUR and DISPLAY_COLOUR defined above
def displayBoard(screen, board):
    screen.fill(BACKGROUND_COLOUR)
    displayKey(screen)
    size = board.shape
    cellSize = SIZE_DISPLAY / SIZE_BOARD
    for i in range(size[0]):
        for j in range(size[1]):
            if board[i][j] == 1:
                pygame.draw.rect(screen, DISPLAY_COLOUR, (i*cellSize, j*cellSize, cellSize, cellSize))

# Gets and dispaly user input percent for new board
# "Enter the percent of Alive Cells"
# "<input>%"  0 <= input < 100
# "and then press enter."
def displayGetInputPercent(screen):
    screen.fill(BACKGROUND_COLOUR)
    font = pygame.font.SysFont("Courier New", 40)
    text = font.render("Enter the percent of Alive Cells", True, DISPLAY_COLOUR)
    screen.blit(text, (0, 0))
    text = font.render("0%", True, DISPLAY_COLOUR)
    screen.blit(text, (0, 40))
    text = font.render("and then press enter.", True, DISPLAY_COLOUR)
    screen.blit(text, (0, 80))
    pygame.display.update()
    number = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return (False, number/100)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return (True, number/100)
            if event.type == pygame.KEYDOWN:
                number = (getKeyNumber(event.key)+ number*10)%100
                pygame.draw.rect(screen, BACKGROUND_COLOUR, (0, 40, 100, 40))
                text = font.render(str(number) + "%", True, DISPLAY_COLOUR)
                screen.blit(text, (0, 40))
                pygame.display.update()

# Display input keys at bottom of screen
# Options: P to Pause, R to Restart
def displayKey(screen):
    pygame.draw.line(screen, DISPLAY_COLOUR, (0,SIZE_DISPLAY), (SIZE_DISPLAY,SIZE_DISPLAY), 1)
    font = pygame.font.SysFont("Courier New", int(SIZE_DISPLAY/25))
    text = font.render("Press: P to Pause, R to Restart", True, DISPLAY_COLOUR)
    screen.blit(text, (0, SIZE_DISPLAY+2))

# MAIN FUNCTION
def main():
    board = getRandomBoard(DEFAULT_SPAWN_PERCENT)
    pygame.init()
    screen = pygame.display.set_mode([SIZE_DISPLAY,SIZE_DISPLAY+ 10 + int(SIZE_DISPLAY/25)])
    paused = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                paused = not paused
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                running, percentage = displayGetInputPercent(screen)
                board = getRandomBoard(percentage)
                paused = False
        if not paused:
            displayBoard(screen, board)
            board = updateBoard(board)
            pygame.display.update()
            pygame.time.wait(200)

if __name__ == "__main__":
    main()