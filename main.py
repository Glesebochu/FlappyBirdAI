import pygame
class pipe:
    #Constant to keep track of the gap between our pipes
    PIPE_GAP = 200
    #The birds we have are stationary only the pipes move backwards below
    #we are defining the speed at which the pipes move backwards
    PIPE_VEL = 5

    #Below is a method to initialize the pipes on the screen

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0

        #Here we are simply creating a vertically flipped image of the pipe that we 
        #have in our images folder
        self.TOP_PIPE = pygame.transform.flip(PIPE_IMG,False,True) 
        self.BOTTOM_PIPE = PIPE_IMG

        #This is a class variable that helps us track collisions with pipes
        self.passed = False
        self.set_height()

    #Below is a method that randomly assigns the heights of our pipes
    def pipe_height(self):

        self.height = random.randrange(50,450)
        #Here we are defining exactly where the top pipe should be on the screen
        self.top = self.height - self.TOP_PIPE.get_height()
        #Here we are defining where the bottom pipe should be on our screen
        self.bottom = self.height + self.gap