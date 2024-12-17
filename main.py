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

def draw_window(win, pipes, bird, floor):
    win.blit(BG_IMG, (0, 0))  # Draw background first
        # Draw pipes
    for pipe in pipes:
        pipe.draw(win)

    # Draw the floor
    floor.draw(win)

    # Draw the bird
    bird.draw(win)

    pygame.display.update()
    
def main():
    pygame.init()
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    bird = Bird(230, 350)  # Initialize bird at a specific position
    floor = Floor(730)  # Initialize the floor
    pipes = [Pipe(600)]  # Initialize with one pipe
    clock = pygame.time.Clock()  # Control the frame rate
    run = True

    
    while run:
        clock.tick(30)  # Set frame rate to 30 FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()


        # Move the floor
        floor.move()
       
        # Move pipes
        for pipe in pipes:
            pipe.move_pipe()
            
        # # Move bird
        bird.move()

        # Add a new pipe if the last one moves left enough
        if pipes[-1].x < 300:
            pipes.append(Pipe(600))

        # Remove pipes that go off-screen
        pipes = [pipe for pipe in pipes if pipe.x + pipe.TOP_PIPE.get_width() > 0]

        # Check if bird collides with the floor
        if bird.y + bird.img.get_height() >= floor.y:
            run = False  # End game if bird hits the floor

        # Draw everything
        draw_window(win, pipes, bird, floor)

    pygame.quit()
    quit()


#Calling Main
main()