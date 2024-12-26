import pygame
import random
import os
import neat

# Constants defining the window size.
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 800

# Global variable to keep track of the generations
generation = -1

# Load bird images and scale them up.
BIRD_IMAGES = [
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))
]

# Load and scale other game images: Pipe, Base (floor), and Background.
PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BACKGROUND_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

# Constants for bird movement
MAX_ROTATION = 25
ROTATION_VELOCITY = 20
ANIMATION_TIME = 5

# Bird functions
def createBird(x, y):
    """
    Create a bird with initial parameters.
    """
    return {
        'x': x,
        'y': y,
        'tilt': 0,
        'tickCount': 0,
        'velocity': 0,
        'height': y,
        'imageCount': 0,
        'image': BIRD_IMAGES[0],
        'displacement': 0  # Initialize displacement
    }

def birdJump(bird):
    """
    Make the bird jump by setting its velocity upwards.
    """
    bird['velocity'] = -11
    bird['tickCount'] = 0
    bird['height'] = bird['y']

def birdHighJump(bird, windActive):
    """
    Make the bird perform a high jump.
    If wind is active, stop the downward displacement.
    Otherwise, set a higher upward velocity.
    """
    if windActive:
        bird['displacement'] = 0  # Stop the downward displacement
    else:
        bird['velocity'] = -20
    bird['tickCount'] = 0
    bird['height'] = bird['y']

def birdMove(bird):
    """
    Move the bird based on its velocity and gravity.
    """
    bird['tickCount'] += 1
    displacement = bird['velocity'] * bird['tickCount'] + 1.5 * (bird['tickCount'] ** 2)
    if displacement >= 16:
        displacement = 16
    if displacement < 0:
        displacement -= 2
    bird['y'] += displacement
    if displacement < 0 or bird['y'] < bird['height'] + 50:
        if bird['tilt'] < MAX_ROTATION:
            bird['tilt'] = MAX_ROTATION
    else:
        if bird['tilt'] > -90:
            bird['tilt'] -= ROTATION_VELOCITY

def birdDraw(window, bird):
    """
    Draw the bird on the window with the appropriate image and rotation.
    """
    bird['imageCount'] += 1
    if bird['imageCount'] < ANIMATION_TIME:
        bird['image'] = BIRD_IMAGES[0]
    elif bird['imageCount'] < ANIMATION_TIME * 2:
        bird['image'] = BIRD_IMAGES[1]
    elif bird['imageCount'] < ANIMATION_TIME * 3:
        bird['image'] = BIRD_IMAGES[2]
    elif bird['imageCount'] < ANIMATION_TIME * 4:
        bird['image'] = BIRD_IMAGES[1]
    elif bird['imageCount'] == ANIMATION_TIME * 4 + 1:
        bird['image'] = BIRD_IMAGES[0]
        bird['imageCount'] = 0
    if bird['tilt'] <= -80:
        bird['image'] = BIRD_IMAGES[1]
        bird['imageCount'] = ANIMATION_TIME * 2
    rotatedImage = pygame.transform.rotate(bird['image'], bird['tilt'])
    newRect = rotatedImage.get_rect(center=bird['image'].get_rect(topleft=(bird['x'], bird['y'])).center)
    window.blit(rotatedImage, newRect.topleft)

def birdGetCollisionMask(bird):
    """
    Get the collision mask for the bird's current image for collision detection.
    """
    return pygame.mask.from_surface(bird['image'])

# Pipe functions
def createPipe(x):
    """
    Create a pipe with a random height.
    """
    height = random.randint(50, 200) if random.random() < 0.5 else random.randint(400, 550)
    return {
        'x': x,
        'height': height,
        'top': height - PIPE_IMAGE.get_height(),
        'bottom': height + 200,  # Pipe.GAP replaced with 200
        'PIPE_TOP': pygame.transform.flip(PIPE_IMAGE, False, True),
        'PIPE_BOTTOM': PIPE_IMAGE,
        'passed': False
    }

def movePipe(pipe):
    """
    Move the pipe to the left.
    """
    pipe['x'] -= 5  # Pipe.VELOCITY replaced with 5

def drawPipe(window, pipe):
    """
    Draw the pipe on the window.
    """
    window.blit(pipe['PIPE_TOP'], (pipe['x'], pipe['top']))
    window.blit(pipe['PIPE_BOTTOM'], (pipe['x'], pipe['bottom']))

def pipeCollide(pipe, bird):
    """
    Check if the bird collides with the pipe.
    """
    birdMask = birdGetCollisionMask(bird)
    topMask = pygame.mask.from_surface(pipe['PIPE_TOP'])
    bottomMask = pygame.mask.from_surface(pipe['PIPE_BOTTOM'])
    topOffset = (pipe['x'] - bird['x'], pipe['top'] - round(bird['y']))
    bottomOffset = (pipe['x'] - bird['x'], pipe['bottom'] - round(bird['y']))
    bottomPoint = birdMask.overlap(bottomMask, bottomOffset)
    topPoint = birdMask.overlap(topMask, topOffset)
    return topPoint or bottomPoint

# Floor functions
def createFloor(y):
    """
    Create the floor with initial parameters.
    """
    return {
        'y': y,
        'x1': 0,
        'x2': BASE_IMAGE.get_width(),
        'image': BASE_IMAGE
    }

def moveFloor(floor):
    """
    Move the floor to the left to create a scrolling effect.
    """
    floor['x1'] -= 5  # Floor.VELOCITY replaced with 5
    floor['x2'] -= 5
    if floor['x1'] + floor['image'].get_width() < 0:
        floor['x1'] = floor['x2'] + floor['image'].get_width()
    if floor['x2'] + floor['image'].get_width() < 0:
        floor['x2'] = floor['x1'] + floor['image'].get_width()

def drawFloor(window, floor):
    """
    Draw the floor on the window.
    """
    window.blit(floor['image'], (floor['x1'], floor['y']))
    window.blit(floor['image'], (floor['x2'], floor['y']))

# Wind effect function
def applyWindEffect(birds, pipes, windActive, windTimer):
    """
    Apply the wind effect to the birds.
    """
    for bird in birds:
        for pipe in pipes:
            if pipe['x'] - 50 < bird['x'] < pipe['x'] + pipe['PIPE_TOP'].get_width() + 10:
                return False, 0
    if not windActive:
        if random.random() < 0.1:
            windActive = True
            windTimer = random.randint(12, 30)
    if windActive:
        for bird in birds:
            bird['displacement'] += 20  # Directly modify displacement
        windTimer -= 1
        if windTimer <= 0:
            windActive = False
    return windActive, windTimer

# Drawing function
def drawWindow(window, pipes, birds, floor, score, font, generation, windActive, highJumpActive, windIncoming):
    """
    Draw all game elements on the window.
    """
    window.blit(BACKGROUND_IMAGE, (0, 0))
    for pipe in pipes:
        drawPipe(window, pipe)
    drawFloor(window, floor)
    for bird in birds:
        birdDraw(window, bird)
    scoreText = font.render(f"Score: {score}", 1, (255, 255, 255))
    window.blit(scoreText, (WINDOW_WIDTH - scoreText.get_width() - 10, 10))
    generationText = font.render(f"Gen: {generation}", 1, (255, 255, 255))
    window.blit(generationText, (10, 10))
    if windActive:
        windText = font.render("Wind Active!", 1, (255, 0, 0))
        window.blit(windText, (WINDOW_WIDTH // 2 - windText.get_width() // 2, 50))
    if windIncoming:
        windIncomingText = font.render("Wind Incoming!", 1, (0, 255, 0))
        window.blit(windIncomingText, (WINDOW_WIDTH // 2 - windIncomingText.get_width() // 2, 100))
    pygame.display.update()
  
# Main function
def main(genomes, config):
    """
    Main function to run the NEAT algorithm and the game.
    """
    global generation 
    generation += 1

    pygame.init()
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    birds = []
    networks = []
    genomeList = []

    for _, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        networks.append(net)
        birds.append(createBird(230, 350))
        genome.fitness = 0
        genomeList.append(genome)

    floor = createFloor(730)
    pipes = [createPipe(400)]
    clock = pygame.time.Clock()
    score = 0
    font = pygame.font.SysFont("comicsans", 50)

    run = True
    windActive = False
    windTimer = 0
    highJumpActive = False
    
    while run:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipeIndex = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0]['x'] > pipes[0]['x'] + pipes[0]['PIPE_TOP'].get_width():
                pipeIndex = 1
        else:
            run = False
            break

        for birdIndex, bird in enumerate(birds):
            birdMove(bird)
            genomeList[birdIndex].fitness += 0.1  # Reward for staying alive

            windIncoming = 1 if windTimer > 12 else 0  # Wind incoming in approximately 0.4 seconds
            inputs = (bird['y'], abs(bird['y'] - pipes[pipeIndex]['height']), abs(bird['y'] - pipes[pipeIndex]['bottom']), pipes[pipeIndex]['height'], windIncoming, int(windActive))
            output = networks[birdIndex].activate(inputs)

            highJumpOutput = output[1]
            jumpOutput = output[0]

            if highJumpOutput > jumpOutput and highJumpOutput > 0.5:
                birdHighJump(bird, windActive)
                highJumpActive = True
                genomeList[birdIndex].fitness += 0.5

                if bird['y'] > pipes[pipeIndex]['top'] and bird['y'] < pipes[pipeIndex]['bottom']:
                    genomeList[birdIndex].fitness -= 1.0  # Punishment for using high jump inside the pipes

            elif jumpOutput > 0.5:
                birdJump(bird)
                highJumpActive = False

        moveFloor(floor)

        addPipe = False
        for pipe in pipes:
            for birdIndex, bird in enumerate(birds):
                if pipeCollide(pipe, bird):
                    genomeList[birdIndex].fitness -= 1
                    birds.pop(birdIndex)
                    networks.pop(birdIndex)
                    genomeList.pop(birdIndex)
                    continue

                if not pipe['passed'] and pipe['x'] < bird['x']:
                    pipe['passed'] = True
                    score += 1
                    for genome in genomeList:
                        genome.fitness += 5
                    addPipe = True

                    if highJumpActive and (bird['y'] < pipes[pipeIndex]['bottom']):
                        genomeList[birdIndex].fitness += 10  # Higher reward for successful high jump
                        highJumpActive = False  # Reset highJumpActive after rewarding

            movePipe(pipe)

        if addPipe:
            pipes.append(createPipe(pipes[-1]['x'] + 300))  # Fixed gap between pipes

        pipes = [pipe for pipe in pipes if pipe['x'] + pipe['PIPE_TOP'].get_width() > 0]

        for birdIndex, bird in enumerate(birds):
            if bird['y'] + bird['image'].get_height() >= floor['y'] or bird['y'] < 0:
                birds.pop(birdIndex)
                networks.pop(birdIndex)
                genomeList.pop(birdIndex)

        windActive, windTimer = applyWindEffect(birds, pipes, windActive, windTimer)

        drawWindow(window, pipes, birds, floor, score, font, generation, windActive, highJumpActive, windIncoming)

# Function to ask for mode
def askMode():
    """
    Ask the user to select a mode: train or play.
    """
    pygame.init()
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    font = pygame.font.SysFont("comicsans", 30)
    clock = pygame.time.Clock()
    run = True
    mode = None

    while run:
        window.fill((0, 0, 0))
        text = font.render("Press 'T' to train or 'P' to play", 1, (255, 255, 255))
        window.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, WINDOW_HEIGHT // 2 - text.get_height() // 2))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    mode = 'train'
                    run = False
                elif event.key == pygame.K_p:
                    mode = 'play'
                    run = False

        clock.tick(30)

    return mode

# Function to play the game manually
def playGame():
    """
    Function to play the game manually.
    """
    pygame.init()
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    bird = createBird(230, 350)
    floor = createFloor(730)
    pipes = [createPipe(600)]
    score = 0
    font = pygame.font.SysFont("comicsans", 50)
    run = True

    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    birdJump(bird)

        birdMove(bird)
        moveFloor(floor)

        addPipe = False
        for pipe in pipes:
            movePipe(pipe)
            if pipeCollide(pipe, bird):
                run = False
            if not pipe['passed'] and pipe['x'] < bird['x']:
                pipe['passed'] = True
                score += 1
                addPipe = True

        if addPipe:
            pipes.append(createPipe(600))

        pipes = [pipe for pipe in pipes if pipe['x'] + pipe['PIPE_TOP'].get_width() > 0]

        if bird['y'] + bird['image'].get_height() >= floor['y'] or bird['y'] < 0:
            run = False

        drawWindow(window, pipes, [bird], floor, score, font, generation, False, False, False)

def run(configPath):
    """
    This function sets up and runs the NEAT evolutionary process.
    It uses the configuration file specified by 'configPath' to determine
    how networks are structured and evolved.
    """
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        configPath
    )

    population = neat.Population(config)

    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Run for up to 50 generations.
    winner = population.run(main, 300 )

    # 'winner' now holds the best genome found during the run. You could further analyze it or replay it.

if __name__ == "__main__":
    localDir = os.path.dirname(__file__)
    configPath = os.path.join(localDir, "ConfigFile.txt")

    mode = askMode()
    if mode == 'train':
        run(configPath)
    elif mode == 'play':
        playGame()
    else:
        print("Invalid mode selected. Please enter 'train' or 'play'.")