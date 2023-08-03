import pygame
import numpy as np
import pickle
import sys
import os

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
    return  not(alive == 2 or alive == 3)  

# Call for cell[i][j] == 0
# and checks if should revive based on:
# Any dead cell with three live neighbours becomes a live cell
def shouldRevive(board, i, j):
    alive = aliveNeighbours(board, i, j)
    return  alive == 3

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
    board = np.zeros((SIZE_BOARD**2), dtype=np.bool)
    board[:int(SIZE_BOARD**2*percentAlive)] = 1
    np.random.shuffle(board)
    return board.reshape((SIZE_BOARD,SIZE_BOARD))

def detectStableState(boards):
    length = len(boards)
    if length > 2:
        return np.array_equal(boards[length - 1], boards[length - 3])
    return False

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
            displayKey(screen)
            board = updateBoard(board)
            pygame.display.update()
            pygame.time.wait(200)

def mainGetData(gameNumber, percentage):
    board = getRandomBoard(percentage)
    pastBoards = [board]
    pygame.init()
    screen = pygame.display.set_mode([SIZE_DISPLAY,SIZE_DISPLAY])
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        displayBoard(screen, board)
        board = updateBoard(board)
        pastBoards.append(board)
        if detectStableState(pastBoards):
            print (f'Percent: {percentage} just reach stable state\n After {len(pastBoards)} ticks.\n Game number {gameNumber}')
            with open('data/gameOfLife'+ str(gameNumber) + ".pickle", 'wb') as handle:
                pickle.dump({'percent': percentage, 'boards': pastBoards}, handle, protocol=pickle.HIGHEST_PROTOCOL)
            percentage = (percentage + 0.01)%100
            board = getRandomBoard(percentage)
            pastBoards = []
            gameNumber += 1
        pygame.display.update()

def mainDisplayPastGame(index, delay):
    with open("data/gameOfLife" + str(index) + ".pickle", 'rb') as handle:
                b = pickle.load(handle)
    pygame.init()
    screen = pygame.display.set_mode([SIZE_DISPLAY,SIZE_DISPLAY])
    boards = b["boards"]
    for board in boards:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        displayBoard(screen, board)
        pygame.time.wait(delay)
        pygame.display.update()

def updateBoardNet(model, board):
    return np.round(model.predict(board.reshape(-1,10000))).reshape(100,100)

if __name__ == "__main__":
    args = sys.argv
    if len(sys.argv) > 1:
        if sys.argv[1] == 'main':
            main()
        elif sys.argv[1] == 'data':
            mainGetData(int(sys.argv[2]), float(sys.argv[3]))
        elif sys.argv[1] == 'display':
            mainDisplayPastGame(int(sys.argv[2]), int(sys.argv[3]))
    else:
        import tensorflow as tf 
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import Dense
        from tensorflow import keras
        #'''
        X = []
        Y = []
        length = 0
        for filename in os.listdir("data"):
            with open("data/" + filename, 'rb') as handle:
                data = pickle.load(handle)
            boards = []
            for board in data['boards']:
                boards.append(board.reshape(-1,10000))
            X += boards[0:len(boards)-1]
            Y += boards[1:len(boards)]
        print(np.array(X).shape)
        #'''
        
        model = Sequential()
        model.add(keras.layers.Flatten(input_shape=(1,10000)))
        model.add(keras.layers.Dense(30, activation='relu'))
        model.add(keras.layers.Dense(30, activation='relu'))
        model.add(keras.layers.Dense(10000))
        #model.add(Dense(10000, activation='softmax', input_dim=10000))
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['categorical_accuracy'])
        #model.compile(loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True), optimizer='adam', metrics=['accuracy'])
        #model.summary()
        model.load_weights('model/model.hz')
        #'''
        TRAIN_SIZE = 100000
        TEST_SIZE = 10000


        xtrain = np.array(X[0:TRAIN_SIZE])
        ytrain = np.array(Y[0:TRAIN_SIZE]).reshape((TRAIN_SIZE,10000))
        xtest = np.array(X[TRAIN_SIZE:TRAIN_SIZE+TEST_SIZE])
        ytest = np.array(Y[TRAIN_SIZE:TRAIN_SIZE+TEST_SIZE]).reshape((TEST_SIZE,10000))
        #model.fit(xtrain, ytrain, epochs=10, batch_size=512)

        result = np.round(model.predict(xtest))
        print(np.count(ytest == 1 and result == 1))#/(np.sum(ytest == 1)))

        pygame.init()
        screen = pygame.display.set_mode([SIZE_DISPLAY,SIZE_DISPLAY])
        displayBoard(screen, xtest[0].reshape(100,100))
        pygame.display.update()
        input()
        displayBoard(screen, result[0].reshape(100,100))
        pygame.display.update()
        input()
        model.save_weights('model/model.hz')
        #'''
        '''
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
                displayKey(screen)
                board = updateBoardNet(model, board)
                pygame.display.update()
                pygame.time.wait(200)'''