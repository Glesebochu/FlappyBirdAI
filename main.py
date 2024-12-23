import pygame
import random
import os
import neat

# Constants defining the window size.
# The width generally matches the background image width for a seamless look.
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 800

#Global variable to keep track of the generations
GEN = -1

# Load bird images and scale them up.
BIRD_IMGS = [
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))
]

# Load and scale other game images: Pipe, Base (floor), and Background.
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG   = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

class Bird:
    # Bird animation and physics constants
    MAX_ROTATION = 25
    ROTATION_VELOCITY = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.velocity = 0
        self.height = self.y
        self.img_count = 0
        self.img = BIRD_IMGS[0]

    def jump(self):
        # Give the bird an upward velocity and reset tick_count
        self.velocity = -8
        self.tick_count = 0
        self.height = self.y

    def move(self):
        # Calculate displacement for this frame based on tick_count and gravity
        self.tick_count += 1
        displacement = self.velocity * self.tick_count + 1.5 * (self.tick_count**2)

        # Limit downward displacement
        if displacement >= 16:
            displacement = 16
        # Make upward movement a bit snappier
        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        # Tilt the bird: tilt up when going up, tilt down when falling
        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROTATION_VELOCITY

    def draw(self, win):
        self.img_count += 1

        # Cycle through bird images for a wing-flapping animation
        if self.img_count < self.ANIMATION_TIME:
            self.img = BIRD_IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = BIRD_IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = BIRD_IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = BIRD_IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = BIRD_IMGS[0]
            self.img_count = 0

        # If the bird is heavily tilted downward, show a static image
        if self.tilt <= -80:
            self.img = BIRD_IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        # Rotate the bird image around its center
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        # For pixel-perfect collision detection
        return pygame.mask.from_surface(self.img)


class Pipe:
    # Vertical gap between the top and bottom pipe.
    PIPE_GAP = 110
    PIPE_VEL = 5  # Speed at which pipes move to the left (bird is effectively moving forward)

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0

        # Create a flipped image of the pipe for the top portion
        self.TOP_PIPE = pygame.transform.flip(PIPE_IMG, False, True)
        self.BOTTOM_PIPE = PIPE_IMG

        self.passed = False
        self.pipe_height()

    def pipe_height(self):
        # Randomly set the height of pipes to provide varying challenges
        self.height = random.randrange(50, 450)
        self.top = self.height - self.TOP_PIPE.get_height()
        self.bottom = self.height + self.PIPE_GAP

    def move_pipe(self):
        # Move pipe to the left each frame
        self.x -= self.PIPE_VEL

    def draw(self, win):
        # Draw top and bottom pipes at their respective positions
        win.blit(self.TOP_PIPE, (self.x, self.top))
        win.blit(self.BOTTOM_PIPE, (self.x, self.bottom))

    def collide(self, bird):
        # Check if the bird collides with either the top or bottom pipe using masks
        bird_rect = pygame.Rect(bird.x, bird.y, bird.img.get_width(), bird.img.get_height())
        top_pipe_rect = pygame.Rect(self.x, self.top, self.TOP_PIPE.get_width(), self.TOP_PIPE.get_height())
        bottom_pipe_rect = pygame.Rect(self.x, self.bottom, self.BOTTOM_PIPE.get_width(), self.BOTTOM_PIPE.get_height())

        # Quick bounding box check
        if not (bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect)):
            return False

        # Pixel-perfect collision check using masks
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.TOP_PIPE)
        bottom_mask = pygame.mask.from_surface(self.BOTTOM_PIPE)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        top_collision = bird_mask.overlap(top_mask, top_offset)
        bottom_collision = bird_mask.overlap(bottom_mask, bottom_offset)

        return top_collision or bottom_collision


class Floor:
    FLOOR_VEL = 5  # Speed at which the ground moves to create a looping effect

    def __init__(self, y):
        self.y = y
        self.width = BASE_IMG.get_width()
        self.x1 = 0
        self.x2 = self.width

    def move(self):
        # Move both floor images to the left
        self.x1 -= self.FLOOR_VEL
        self.x2 -= self.FLOOR_VEL

        # If one image goes off-screen, recycle it to the right
        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width
        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width

    def draw(self, win):
        # Draw the two floor images next to each other to create the illusion of infinite ground
        win.blit(BASE_IMG, (self.x1, self.y))
        win.blit(BASE_IMG, (self.x2, self.y))


def draw_window(win, pipes, birds, floor, score, font, generations):
    win.blit(BG_IMG, (0, 0))  # Draw background first

    # Draw pipes
    for pipe in pipes:
        pipe.draw(win)

    # Draw the moving floor
    floor.draw(win)

    # Draw each bird
    for bird in birds:
        bird.draw(win)

    # Display current score on screen
    score_text = font.render(f"Score: {score}", 1, (255, 255, 255))
    win.blit(score_text, (WINDOW_WIDTH - score_text.get_width() - 10, 10))

    # Display current generation on screen
    GenerationsText = font.render(f"Gen: {GEN}", 1, (255, 255, 255))
    win.blit(GenerationsText, (10, 10))

    # Display current score on screen
    # score_text = font.render(f"Score: {score}", 1, (255, 255, 255))
    # win.blit(score_text, (WINDOW_WIDTH - score_text.get_width() - 10, 10))

    pygame.display.update()

def apply_wind_effect(birds, pipes, wind_active):
    # Check if any bird is between pipes
    for bird in birds:
        for pipe in pipes:
            if pipe.x < bird.x < pipe.x + pipe.TOP_PIPE.get_width():
                return wind_active  # Bird is entering or inside a pipe, no wind effect

    # If no bird is between pipes, apply wind effect
    if not wind_active:
        wind_active = random.random() < 0.1  # 10% chance to start wind effect

    if wind_active:
        for bird in birds:
            bird.y += 10  # Push the bird down by 10 pixels each frame
        return True  # Wind effect is active

    return False  # Wind effect is not active

def draw_wind_effect(win, wind_active):
    if wind_active:
        wind_text = pygame.font.SysFont("comicsans", 50).render("Wind Effect!", 1, (255, 0, 0))
        win.blit(wind_text, (WINDOW_WIDTH // 2 - wind_text.get_width() // 2, 10))

def main(genomes, config):
    """
    This function is used by NEAT to evaluate the fitness of genomes.
    'genomes' is a list of tuples (genome_id, genome_object).
    'config' is the NEAT configuration object.
    """
    global GEN 
    GEN = GEN + 1

    pygame.init()
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    # For each genome, we create a neural network, track the bird it controls, and track the genome itself.
    birds = []
    networks = []
    genome_list = []

    for _, genome in genomes:
        # Create a neural network for this genome using the chosen NEAT configuration.
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        networks.append(net)
        
        # Initialize the bird controlled by this genome at a fixed starting position.
        birds.append(Bird(230, 350))
        
        # Initialize the genome's fitness. Higher fitness means better performance.
        genome.fitness = 0
        genome_list.append(genome)

    floor = Floor(730)
    pipes = [Pipe(600)]
    clock = pygame.time.Clock()
    score = 0
    font = pygame.font.SysFont("comicsans", 50)

    run = True
    wind_active = False  # Initialize wind_active before the game loop
    
    while run:
        clock.tick(30)  # 30 FPS cap

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        # Determine which pipe to consider for deciding whether to jump.
        # If the bird has passed the first pipe, focus on the next one.
        pipe_index = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].TOP_PIPE.get_width():
                pipe_index = 1
        else:
            # No birds left, end simulation for this generation.
            run = False
            break

        # For each bird, get input from the game state and feed it into the neural network.
        for bird_index, bird in enumerate(birds):
            bird.move()
            # Give a small reward each frame for staying alive.
            genome_list[bird_index].fitness += 0.1

            # Inputs: bird's vertical position and the vertical distance to the bottom of the closest pipe.
            # This helps the network decide whether to jump.
            # Corrected input: pipes[pipe_index].bottom is an integer, we compare bird.y to that.
            inputs = (bird.y, abs(bird.y - pipes[pipe_index].height),abs(bird.y - pipes[pipe_index].bottom))
            output = networks[bird_index].activate(inputs)

            # If output > 0.5, make the bird jump
            if output[0] > 0.5:
                bird.jump()

        # Move the floor to create continuous scrolling
        floor.move()

        add_pipe = False
        # Move pipes and check collisions or passing events
        for pipe in pipes:
            # Check collision with each bird
            for bird_index, bird in enumerate(birds):
                if pipe.collide(bird):
                    # If bird hits a pipe, penalize its genome and remove it
                    genome_list[bird_index].fitness -= 1
                    birds.pop(bird_index)
                    networks.pop(bird_index)
                    genome_list.pop(bird_index)
                    continue  # Move on to next bird

                # If the bird passed the pipe successfully, increase score and give a reward
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    score += 1
                    for genome_obj in genome_list:
                        genome_obj.fitness += 5
                    add_pipe = True

            pipe.move_pipe()

        # If a pipe was passed, add a new one ahead
        if add_pipe:
            pipes.append(Pipe(600))

        # Remove off-screen pipes
        pipes = [pipe for pipe in pipes if pipe.x + pipe.TOP_PIPE.get_width() > 0]

        # Remove birds that hit the floor or fly too high
        for bird_index, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= floor.y or bird.y < 0:
                # Bird crashed or flew out of bounds
                birds.pop(bird_index)
                networks.pop(bird_index)
                genome_list.pop(bird_index)

        # Apply wind effect
        wind_active = apply_wind_effect(birds, pipes, wind_active)

        draw_window(win, pipes, birds, floor, score, font, GEN)


def run(config_path):
    """
    This function sets up and runs the NEAT evolutionary process.
    It uses the configuration file specified by 'config_path' to determine
    how networks are structured and evolved.
    """
    # Create a NEAT configuration object by reading parameters from the config file.
    # The chosen classes define how genomes, reproduction, species, and stagnation are handled.
    config = neat.config.Config(
        neat.DefaultGenome,       # Defines how a single neural network (genome) is represented
        neat.DefaultReproduction, # Defines how genomes are reproduced (crossover/mutation)
        neat.DefaultSpeciesSet,   # Defines how genomes are grouped into species
        neat.DefaultStagnation,   # Defines how to remove species that are not improving
        config_path               # The path to the NEAT configuration file with evolutionary parameters
    )

    # Initialize a NEAT Population with the configuration, which creates an initial population of genomes.
    population = neat.Population(config)

    # Add reporters to provide information during the run:
    # StdOutReporter prints progress and statistics to the console.
    population.add_reporter(neat.StdOutReporter(True))

    # StatisticsReporter keeps track of data like best fitness per generation, species diversity, etc.
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Run the evolutionary process, using the 'main' function as the fitness evaluation function.
    # We'll run up to 50 generations. If a genome reaches the defined fitness goal, evolution stops early.
    winner = population.run(main, 50)

    # 'winner' now holds the best genome found during the run. You could further analyze it or replay it.


if __name__ == "__main__":
    # Determine the path to the NEAT config file.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "ConfigFile.txt")

    # Run NEAT with the specified configuration file.
    run(config_path)
