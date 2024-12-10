import pygame
import random
import os

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

def draw_window(win, pipes):
    win.blit(BG_IMG, (0, 0))  # Draw background first
    for pipe in pipes:  # Draw all pipes
        pipe.draw(win)
    pygame.display.update()

    
def main():
    pygame.init()
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pipes = [Pipe(600)]  # Initialize with one pipe
    clock = pygame.time.Clock()  # Control the frame rate
    run = True

    while run:
        clock.tick(30)  # Set frame rate to 30 FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Move pipes
        for pipe in pipes:
            pipe.move_pipe()

        # Add a new pipe if the last one moves left enough
        if pipes[-1].x < 300:
            pipes.append(Pipe(600))

        # Remove pipes that go off-screen
        pipes = [pipe for pipe in pipes if pipe.x + pipe.TOP_PIPE.get_width() > 0]

        # Draw everything
        draw_window(win, pipes)

    pygame.quit()
    quit()


#Calling Main
main()