import pygame
import random
import os
import neat
import pickle

# Constants defining the window size.
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 800

#constants to keep track of fitness threshold
FITNESS_THRESHOLD = 10000

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
        'displacement': 0,  # Initialize displacement
        'windDisplacement': 0,  # Initialize wind displacement
        'windActive': False,  # Initialize wind active
        'windTimer': 0,  # Initialize wind timer
        'highJumpActive': False  # Initialize high jump active
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
    bird['highJumpActive'] = True
    if bird['windActive']:
        # bird['velocity'] = 0  # Stop the downward displacement
        bird['windActive'] = False

    else:
        bird['velocity'] -= 20  # Higher upward velocity
    # bird['tickCount'] = 0
    # bird['height'] = bird['y']

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
    height = random.randint(80, 200) if random.random() < 0.5 else random.randint(350, 550)
    return {
        'x': x,
        'height': height,
        'top': height - PIPE_IMAGE.get_height(),
        'bottom': height + 200,  # Pipe.GAP is 200
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
def applyWindEffect(birds):
    """
    Apply the wind effect to each bird individually.
    """
    for bird in birds:
        if not bird['windActive']:
            if (not bird['highJumpActive']) and random.random() < 0.1:
                bird['windActive'] = True
                bird['windTimer'] = random.randint(12, 30)
        if bird['windActive']:
            bird['velocity'] += 20  # Modify wind displacement
            bird['windTimer'] -= 1
            if bird['windTimer'] <= 0:
                bird['windActive'] = False

# Drawing function
def drawWindow(window, pipes, birds, floor, score, font, windActiveGenomes=None, highJumpActiveGenomes=None, windIncomingGenomes=None, generation=None):
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

    if generation is not None:
        generationText = font.render(f"Gen: {generation}", 1, (255, 255, 255))
        window.blit(generationText, (10, 10))

    if windActiveGenomes:
        windText = font.render(f"Wind Active for genomes: {', '.join(map(str, windActiveGenomes))}", 1, (255, 0, 0))
        windText = pygame.transform.scale(windText, (windText.get_width() // 2, windText.get_height() // 2))
        windTextRect = windText.get_rect(center=(WINDOW_WIDTH // 3, 100))
        window.blit(windText, windTextRect)
    if windIncomingGenomes:
        windIncomingText = font.render(f"Wind Incoming for genomes: {', '.join(map(str, windIncomingGenomes))}", 1, (0, 255, 0))
        windIncomingText = pygame.transform.scale(windIncomingText, (windIncomingText.get_width() // 2, windIncomingText.get_height() // 2))
        windIncomingTextRect = windIncomingText.get_rect(center=(WINDOW_WIDTH // 3, 150))
        window.blit(windIncomingText, windIncomingTextRect)
    if highJumpActiveGenomes:
        highJumpText = font.render(f"High Jump Active for genomes: {', '.join(map(str, highJumpActiveGenomes))}", 1, (0, 0, 255))
        highJumpText = pygame.transform.scale(highJumpText, (highJumpText.get_width() // 2, highJumpText.get_height() // 2))
        highJumpTextRect = highJumpText.get_rect(center=(WINDOW_WIDTH // 3, 200))
        window.blit(highJumpText, highJumpTextRect)
        
    for particle in particles[:]:
        particle.update()
        particle.draw(window)
        if particle.lifespan <= 0:
            particles.remove(particle)

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
    stop_training = False
    
    while run:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:  # Press 'Q' to quit after the current generation
                    stop_training = True
                    run = False
                    break

        if stop_training:
            break

        pipeIndex = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0]['x'] > pipes[0]['x'] + pipes[0]['PIPE_TOP'].get_width():
                pipeIndex = 1
        else:
            run = False
            break

        for birdIndex, bird in enumerate(birds):
            birdMove(bird)
            genomeList[birdIndex].fitness += 0.6  # Reward for staying alive

            windIncoming = 1 if bird['windTimer'] > 12 else 0  # Wind incoming in approximately 0.4 seconds
            inputs = (bird['y'], abs(bird['y'] - pipes[pipeIndex]['height']), abs(bird['y'] - pipes[pipeIndex]['bottom']), pipes[pipeIndex]['height'], windIncoming, int(bird['windActive']))
            output = networks[birdIndex].activate(inputs)

            highJumpOutput = output[1]
            jumpOutput = output[0]

            if highJumpOutput > 0.5:
                birdHighJump(bird, bird['windActive'])
                genomeList[birdIndex].fitness += 0.2

                if bird['x'] > pipes[pipeIndex]['x'] and bird['x'] < pipes[pipeIndex]['x'] + pipes[pipeIndex]['PIPE_TOP'].get_width():
                    if bird['y'] > pipes[pipeIndex]['top'] and bird['y'] < pipes[pipeIndex]['bottom']:
                        genomeList[birdIndex].fitness -= 0  # Punishment for using high jump inside the pipes
            else:
                bird['highJumpActive'] = False


            if jumpOutput > 0.5:
                birdJump(bird)

        moveFloor(floor)

        addPipe = False
        for pipe in pipes:
            for birdIndex, bird in enumerate(birds):
                if pipeCollide(pipe, bird):
                    genomeList[birdIndex].fitness -= 5
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

                #Punish the birds that fly off into the sky.
                if bird['y'] < 0 or bird['y'] + bird['image'].get_height() >= floor['y']:
                    genomeList[birdIndex].fitness -= 5
                    birds.pop(birdIndex)
                    networks.pop(birdIndex)
                    genomeList.pop(birdIndex)
                    continue

            movePipe(pipe)

        if addPipe:
            pipes.append(createPipe(pipes[-1]['x'] + 400))  # Fixed gap between pipes

        pipes = [pipe for pipe in pipes if pipe['x'] + pipe['PIPE_TOP'].get_width() > 0]

        for birdIndex, bird in enumerate(birds):
            if bird['y'] + bird['image'].get_height() >= floor['y'] or bird['y'] < 0:
                birds.pop(birdIndex)
                networks.pop(birdIndex)
                genomeList.pop(birdIndex)

        applyWindEffect(birds)

        # Collect indices of genomes with active states
        windActiveGenomes = [i for i, bird in enumerate(birds) if bird['windActive']]
        highJumpActiveGenomes = [i for i, bird in enumerate(birds) if bird['highJumpActive']]
        windIncomingGenomes = [i for i, bird in enumerate(birds) if bird['windTimer'] > 12]

        # Call drawWindow with the collected indices
        drawWindow(window, pipes, birds, floor, score, font, windActiveGenomes=windActiveGenomes, highJumpActiveGenomes=highJumpActiveGenomes, windIncomingGenomes=windIncomingGenomes, generation=generation)

    # Save the best genome to a file
    if stop_training:
        winner = max(genomes, key=lambda g: g[1].fitness)
        if winner[1].fitness >= FITNESS_THRESHOLD:
            with open('winner.pkl', 'wb') as output:
                pickle.dump(winner[1], output, 1)
            print("Best genome saved to winner.pkl")

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
        text = font.render("Press 'T' to train, 'P' to play yourself or 'B' to play best genome", 1, (255, 255, 255))
        text = pygame.transform.scale(text, (text.get_width() // 2, text.get_height() // 2))
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
                elif event.key == pygame.K_b:
                    mode = 'play_best'
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
                elif event.key == pygame.K_h:  # Assuming 'H' key is used for high jump
                    birdHighJump(bird,bird['windActive'])

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
            pipes.append(createPipe(pipes[-1]['x'] + 400))  # Fixed gap between pipes

        pipes = [pipe for pipe in pipes if pipe['x'] + pipe['PIPE_TOP'].get_width() > 0]

        if bird['y'] + bird['image'].get_height() >= floor['y'] or bird['y'] < 0:
            run = False

        applyWindEffect([bird])

        windActiveGenomes = [0] if bird['windActive'] else []
        highJumpActiveGenomes = [0] if bird['highJumpActive'] else []
        windIncomingGenomes = [0] if bird['windTimer'] > 12 else []

        drawWindow(window, pipes, [bird], floor, score, font, windActiveGenomes=windActiveGenomes, highJumpActiveGenomes=highJumpActiveGenomes, windIncomingGenomes=windIncomingGenomes)          

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

    # Run for up to 300 generations.
    winner = population.run(main, 300 )

    # 'winner' now holds the best genome found during the run. 
    # save the winner to a file
    with open('winner.pkl', 'wb') as output:
        pickle.dump(winner, output, 1)

    print("Best genome saved to winner.pkl")

#Function to play the game using the best genome
def playBestGenome(configPath):
    """
    Load the best genome from a file and use it to play the game.
    """
    try:
        # Load the best genome from the file
        with open("winner.pkl", "rb") as f:
            best_genome = pickle.load(f)
    except FileNotFoundError:
        print("Best genome file not found. Please run the training first.")
        return

    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        configPath
    )

    # Create a neural network from the best genome
    net = neat.nn.FeedForwardNetwork.create(best_genome, config)

    # Initialize the game
    pygame.init()
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    bird = createBird(230, 350)
    floor = createFloor(730)
    pipes = [createPipe(600)]
    clock = pygame.time.Clock()
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
        
        if bird['windActive']:
            createWindParticles(bird)
        if bird['highJumpActive']:
            createHighJumpParticles(bird)

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
            pipes.append(createPipe(pipes[-1]['x'] + 400))  # Fixed gap between pipes

        pipes = [pipe for pipe in pipes if pipe['x'] + pipe['PIPE_TOP'].get_width() > 0]

        if bird['y'] + bird['image'].get_height() >= floor['y'] or bird['y'] < 0:
            run = False

        applyWindEffect([bird])

        windActiveGenomes = [0] if bird['windActive'] else []
        highJumpActiveGenomes = [0] if bird['highJumpActive'] else []
        windIncomingGenomes = [0] if bird['windTimer'] > 12 else []

        # Use the neural network to control the bird
        if len(pipes) > 1 and bird['x'] > pipes[0]['x'] + pipes[0]['PIPE_TOP'].get_width():
            pipeIndex = 1
        else:
            pipeIndex = 0

        windIncoming = 1 if bird['windTimer'] > 12 else 0  # Wind incoming in approximately 0.4 seconds
        inputs = (bird['y'], abs(bird['y'] - pipes[pipeIndex]['height']), abs(bird['y'] - pipes[pipeIndex]['bottom']), pipes[pipeIndex]['height'], windIncoming, int(bird['windActive']))
        output = net.activate(inputs)
        highJumpOutput = output[1]
        jumpOutput = output[0]

        if highJumpOutput > 0.5:
            birdHighJump(bird, bird['windActive'])
        else:
            bird['highJumpActive']  = False

        if jumpOutput > 0.5:
            birdJump(bird)

        drawWindow(window, pipes, [bird], floor, score, font, windActiveGenomes=windActiveGenomes, highJumpActiveGenomes=highJumpActiveGenomes, windIncomingGenomes=windIncomingGenomes)

if __name__ == "__main__":
    localDir = os.path.dirname(__file__)
    configPath = os.path.join(localDir, "ConfigFile.txt")

    mode = askMode()
    if mode == 'train':
        run(configPath)
    elif mode == 'play':
        playGame()
    elif mode == 'play_best':
        playBestGenome(configPath)
    else:
        print("Invalid mode selected. Please enter 'train' or 'play'.")