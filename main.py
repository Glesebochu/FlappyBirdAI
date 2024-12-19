import pygame
import random
import os
import neat

#Constants to define the window we will be working with.
#Ideally the width should be the same as the background for the flappy bird we will use.
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 800

#Define the bird images as a list 
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))),
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))),
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]

#Define the pipe image using the os library and pygame to load those images
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))

#Define the background and base images
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bg.png")))

class Bird:
    # Constants for bird animation and physics
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
        self.velocity = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        displacement = self.velocity * self.tick_count + 1.5 * self.tick_count**2

        if displacement >= 16:
            displacement = 16
        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROTATION_VELOCITY

    def draw(self, win):
        self.img_count += 1

        # Cycle through images for animation
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

        # Don't flap wings if falling
        if self.tilt <= -80:
            self.img = BIRD_IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    #Constant to keep track of the gap between our pipes
    PIPE_GAP = 200
    #The birds we have are stationary only the pipes move backwards below
    #we are defining the speed at which the pipes move backwards
    PIPE_VEL = 5

    #Below is a method to initialize the pipes on the screen

    def __init__(self, x):
        #The variable x here defines where on the x axis our pipe is
        self.x = x
        #The height of our pipes is determined randomly using the method pipe_height()
        self.height = 0

        self.top = 0
        self.bottom = 0

        #Here we are simply creating a vertically flipped image of the pipe that we 
        #have in our images folder
        self.TOP_PIPE = pygame.transform.flip(PIPE_IMG,False,True) 
        self.BOTTOM_PIPE = PIPE_IMG

        #This is a class variable that helps us track collisions with pipes
        self.passed = False
        self.pipe_height()

    #Below is a method that randomly assigns the heights of our pipes
    def pipe_height(self):

        self.height = random.randrange(50,450)
        #Here we are defining exactly where the top pipe should start to be drawn
        self.top = self.height - self.TOP_PIPE.get_height()
        #Here we are defining where the bottom pipe should be on our screen
        self.bottom = self.height + self.PIPE_GAP
    
    #Below is the method that we use to actually move our pipes based on the
    #frame velocity
    def move_pipe(self):
        self.x -= self.PIPE_VEL

    def draw(self,win):
        win.blit(self.TOP_PIPE,(self.x,self.top))
        win.blit(self.BOTTOM_PIPE,(self.x,self.bottom))
    def collide(self, bird):
            # Rectangle Collision Detection
            bird_rect = pygame.Rect(bird.x, bird.y, bird.img.get_width(), bird.img.get_height())
            top_pipe_rect = pygame.Rect(self.x, self.top, self.TOP_PIPE.get_width(), self.TOP_PIPE.get_height())
            bottom_pipe_rect = pygame.Rect(self.x, self.bottom, self.BOTTOM_PIPE.get_width(), self.BOTTOM_PIPE.get_height())

            if not (bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect)):
                return False

            # Pixel-Perfect Collision Detection
            bird_mask = bird.get_mask()
            top_mask = pygame.mask.from_surface(self.TOP_PIPE)
            bottom_mask = pygame.mask.from_surface(self.BOTTOM_PIPE)

            top_offset = (self.x - bird.x, self.top - round(bird.y))
            bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

            top_collision = bird_mask.overlap(top_mask, top_offset)
            bottom_collision = bird_mask.overlap(bottom_mask, bottom_offset)

            return top_collision or bottom_collision

def draw_window(win, pipes, bird):
    win.blit(BG_IMG, (0, 0))  # Draw background first
    for pipe in pipes:  # Draw all pipes
        pipe.draw(win)
    bird.draw(win) # draw the bird
    pygame.display.update()


class Floor:

    FLOOR_VEL = 5  # Speed at which the ground moves

    def __init__(self, y):
 
        self.y = y
        self.width = BASE_IMG.get_width()  # Width of the floor image
        self.x1 = 0  # First image starts at position 0
        self.x2 = self.width  # Second image starts right after the first image

    def move(self):
 
        self.x1 -= self.FLOOR_VEL
        self.x2 -= self.FLOOR_VEL

        # Reset positions to create looping effect
        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width
        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width

    def draw(self, win):

        win.blit(BASE_IMG, (self.x1, self.y))  # First image
        win.blit(BASE_IMG, (self.x2, self.y))  # Second image

def draw_window(win, pipes, bird, floor, score, font):
    win.blit(BG_IMG, (0, 0))  # Draw background first
        # Draw pipes
    for pipe in pipes:
        pipe.draw(win)

    # Draw the floor
    floor.draw(win)

    # Draw the bird
    bird.draw(win)

    # Display the score
    score_text = font.render(f"Score: {score}", 1, (255, 255, 255))
    win.blit(score_text, (WINDOW_WIDTH - score_text.get_width() - 10, 10))  # Top-right corner

    pygame.display.update()
    
def main():
    pygame.init()
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    bird = Bird(230, 350)  # Initialize bird at a specific position
    floor = Floor(730)  # Initialize the floor
    pipes = [Pipe(600)]  # Initialize with one pipe
    clock = pygame.time.Clock()  # Control the frame rate
    score = 0                     # Track the player's score
    font = pygame.font.SysFont("comicsans", 50)  # Font for the score display
    
    run = True

    
    while run:
        clock.tick(30)  # Maintain a frame rate of 30 FPS

        # Handle user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False  # Quit the game if the window is closed
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bird.jump()  # Make the bird jump if SPACE is pressed

        # Move the floor
        floor.move()

        # Move pipes and check if the bird passes a pipe (increase score)
        add_pipe = False
        for pipe in pipes:
            pipe.move_pipe()  # Move the pipe to the left

            # Check for collisions with pipes
            if pipe.collide(bird):  # Pixel-perfect collision detection
                run = False  # End the game if bird hits a pipe

            # Check if the bird passes the pipe
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                score += 1  # Increment score when bird passes a pipe
                add_pipe = True

        # Add a new pipe when the last pipe passes a certain point
        if add_pipe:
            pipes.append(Pipe(600))

        # Remove pipes that have moved off-screen
        pipes = [pipe for pipe in pipes if pipe.x + pipe.TOP_PIPE.get_width() > 0]

        # Move the bird
        bird.move()

        # Check if the bird hits the floor
        if bird.y + bird.img.get_height() >= floor.y:
            run = False  # End the game if bird hits the floor

        # Draw all game elements
        draw_window(win, pipes, bird, floor, score, font)

    # Quit pygame when the game loop ends
    pygame.quit()
    quit()


#Calling Main
main()
def run(config_path):
    # Create a NEAT configuration object by reading parameters from the config file.
    # This sets up the rules for how genomes are initialized, mutated, and evolved.
    config = neat.config.Config(
        neat.DefaultGenome,       # The type of genome class to use
        neat.DefaultReproduction, # How to reproduce and mutate genomes
        neat.DefaultSpeciesSet,   # How to group similar genomes into species
        neat.DefaultStagnation,   # How to handle species that stop improving
        config_path               # Path to the NEAT configuration file
    )

    # Initialize a NEAT Population with the given configuration.
    # This creates the initial set of genomes and sets the stage for evolution.
    population = neat.Population(config)

    # Add a StdOutReporter to the population. This reporter prints information
    # about each generation to the console, such as the best genome’s fitness.
    # Setting True means we will see more detailed output during the run.
    population.add_reporter(neat.StdOutReporter(True))

    # Create a StatisticsReporter to keep track of various statistics during evolution.
    # This object can record the fitness of each generation and help with post-run analysis.
    stats = neat.StatisticsReporter()

    # Add the statistics reporter to the population. This ensures that as NEAT runs,
    # it logs and stores data (like the best fitness each generation) for later examination.
    population.add_reporter(stats)

    # Run the NEAT algorithm using the main function as the fitness evaluation callback.
    # Here, 'main' is the function that runs our Flappy Bird game loop and evaluates
    # the performance of a genome. The second argument, 50, is the number of generations
    # to run before giving up if no solution meets the fitness_threshold.
    winner = population.run(main, 50)

    # After evolution completes (either because we reached the fitness goal or hit the
    # max generation limit), 'winner' will contain the best genome found. You can use it
    # to analyze or visualize the final solution.


if __name__ == "__main__":
    # Get the directory where this script is located.
    local_dir = os.path.dirname(__file__)

    # Construct the full path to the NEAT config file by joining the local directory
    # with the filename of the configuration file. This ensures that no matter where
    # the script is run from, it can find the config file as long as it's in the same folder.
    config_path = os.path.join(local_dir, "ConfigFile.txt")

    # Start the NEAT run using the specified configuration.
    # This initiates the whole evolutionary process for the Flappy Bird agent.
    run(config_path)
