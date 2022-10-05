import pygame
import neat
import time
import os
import random


pygame.font.init()


WIN_WIDTH = 550
WIN_HEIGHT = 800

VELOCITY = 5
DISTANCE = 550 # space between pipes

STAT_FONT = pygame.font.SysFont("helvetica", 45)

bird_imgs = [pygame.transform.scale2x(pygame.image.load('fun_projects/flappy bird/images/bird1.png')),
            pygame.transform.scale2x(pygame.image.load('fun_projects/flappy bird/images/bird2.png')),
            pygame.transform.scale2x(pygame.image.load('fun_projects/flappy bird/images/bird3.png'))]
pipe_img = pygame.transform.scale2x(pygame.image.load('fun_projects/flappy bird/images/pipe.png'))
bg_img = pygame.transform.scale2x(pygame.image.load('fun_projects/flappy bird/images/bg.png'))
base_img = pygame.transform.scale2x(pygame.image.load('fun_projects/flappy bird/images/base.png'))

class Bird:
    imgs = bird_imgs
    max_rotation = 25
    rot_vel = 20
    animation_time = 5
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.imgs[0]
    
    def jump(self):
        self.vel = -7
        self.tick_count = 0
        self.height = self.y
        
    def move(self):
        self.tick_count += 1
        
        d = self.vel*self.tick_count + .8*self.tick_count**2 # math for jump physics
        
        if d >= 18: # terminal velocity
            d = 14
        if d < 0:
            d -= 2
            
        self.y = self.y + d
        
        if d < -10 or self.y < self.height + 50:
            if self.tilt < self.max_rotation:
                self.tilt = self.max_rotation
        else:
            if self.tilt > -90:
                self.tilt -= self.rot_vel
    
    def draw(self, win):
        self.img_count += 1
        
        if self.img_count < self.animation_time:
            self.img = self.imgs[0]
        elif self.img_count < self.animation_time*2:
            self.img = self.imgs[1]
        elif self.img_count < self.animation_time*3:
            self.img = self.imgs[2]
        elif self.img_count < self.animation_time*4:
            self.img = self.imgs[1]
        elif self.img_count == self.animation_time*4 + 1:
            self.img = self.imgs[0]
            self.img_count = 0
            
        if self.tilt <= -80:
            self.img = self.imgs[1]
            self.img_count = self.animation_time*2
            
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center= self.img.get_rect(topleft =(self.x,self.y)).center)
        win.blit(rotated_image, new_rect.topleft)
    
    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    gap = 200 # space between pipes
    vel = VELOCITY   
    def __init__(self,x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.pipe_top = pygame.transform.flip(pipe_img, False, True)
        self.pipe_bottom = pipe_img
        
        self.passed = False
        self.set_height()
        
    def set_height(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.pipe_top.get_height()
        self.bottom = self.height + self.gap
        
    def move(self):
        self.x -= self.vel
    
    def draw(self, win):
        win.blit(self.pipe_top, (self.x, self.top))
        win.blit(self.pipe_bottom, (self.x, self.bottom))
        
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.pipe_top)
        bottom_mask = pygame.mask.from_surface(self.pipe_bottom) # get masks for pipes and bird

        top_offset = (self.x - bird.x, self.top-round(bird.y))
        bottom_offset = self.x - bird.x, self.bottom - round(bird.y)
        
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset) # checks if they overlap, else None
        
        if t_point or b_point:
            return True # if there is a collision
        
        return False


class Base:
    width = base_img.get_width()
    img = base_img
    vel = VELOCITY
            
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.width

        
    def move(self):
        self.x1 -= self.vel
        self.x2 -= self.vel
        
        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width # if image moves off screen, move back behind other image
        
        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width
    
    def draw(self, win):
        win.blit(self.img, (self.x1, self.y))
        win.blit(self.img, (self.x2, self.y))







def draw_window(win, birds, pipes, base, score):
    win.blit(bg_img,(0,0))
    
    for pipe in pipes:
        pipe.draw(win)
    
    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10)) 
    base.draw(win)
    if isinstance(birds,list):
        for bird in birds:
            bird.draw(win)
    else:
        birds.draw(win)
    pygame.display.update()

def main():
    bird = Bird(230,350)
    base = Base(730)
    pipes = [Pipe(DISTANCE)]
    win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0
    
    
    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()
        bird.move()
        add_pipe = False
        rem = [] # list of moved pipes
        for pipe in pipes:
            if pipe.collide(bird):
                main()
            
            if pipe.x + pipe.pipe_top.get_width() < 0: # if pipe goes off screen
                rem.append(pipe)
            
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True
                
                
                
            pipe.move()
            
        if add_pipe:
            score += 1
            pipes.append(Pipe(DISTANCE))
        
        for r in rem:
            pipes.remove(r)
        
        if bird.y + bird.img.get_height() >= 730: # if bird hits the floor
            main()  
            
        base.move()
        
        draw_window(win,bird, pipes, base, score)
    pygame.quit()
    quit()
                
def train_ai(genomes, config):
    nets = []
    ge = []
    birds = []
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230,350))
        g.fitness = 0
        ge.append(g)
        
    

    base = Base(730)
    pipes = [Pipe(DISTANCE)]
    win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0
    
    
    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        add_pipe = False
        rem = [] # list of moved pipes
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                    
            
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            
            if pipe.x + pipe.pipe_top.get_width() < 0: # if pipe goes off screen
                rem.append(pipe)    
                
            pipe.move()
         
        pipe_ind = 0 
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].pipe_top.get_width(): # figure out which pipe is closest
                pipe_ind = 1
        else:
            print(score)
            run = False
            break
        
        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += .1
            
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            if output[0] > 0.5:
                bird.jump()
        
        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(DISTANCE))
        
        for r in rem:
            pipes.remove(r)
        
        for x, bird in enumerate(birds):
                if bird.y + bird.img.get_height() >= 730 or bird.y < 0: # if bird hits the floor
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                
            
        base.move()
        
        draw_window(win, birds, pipes, base, score)



def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    
    winner = p.run(train_ai,50)
    
#main()

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    run(config_path)
    
