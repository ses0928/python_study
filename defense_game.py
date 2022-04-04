from matplotlib.pyplot import yscale
import pygame
import sys                          # for game exit

import random                       # random spawn (initial setup)

from tkinter import filedialog      # file load / save

# initialize the game engine
pygame.init()

# Define the colors (RGB)
WHITE = (255,255,255)
BLACK = (0,0,0)
BLUE = (0,0,255)
GREEN = (0,255,0)
RED = (255,0,0)
YELLOW = (255,255,0)
BROWN = (139,69,19)

# define the system font (font, size, bold, italic)
myFont = pygame.font.SysFont("timesnewroman",20,True)
my_sFont = pygame.font.SysFont("timesnewroman",15,True)

# setup : clock, size of window, title, ...
clock = pygame.time.Clock()
world_width = 1200
world_height = 675
worldsize =[world_width,world_height]       # size of window
world = pygame.display.set_mode(worldsize)
pygame.display.set_caption("Defense game (temporary name)")
world.fill(WHITE)

# player setup : permanent resources // stage resourses
gold = 0        # money for upgrade units
diamond = 0     # ????

my_level = 1    # level
stage = 1       # maximum stage that we can try

silver = 0      # summmon resources for unit : stage resource
max_silver = 100
mana = 0.0      # mana for spells
max_mana = 100.0

# buttons for main page
button_my = pygame.Rect(10,world_height/8,world_width/4-20,world_height/2)
button_stage = pygame.Rect(world_width/4+10,world_height/8,world_width/4-20,world_height/2)
button_unit = pygame.Rect(world_width/2+10,world_height/8,world_width/4-20,world_height/2)
button_shop = pygame.Rect(world_width*3/4+10,world_height/8,world_width/4-20,world_height/2)

# buttons for other pages
button_back = pygame.Rect(10,10,world_height/8-20,world_height/8-20)

# class for units
class units():
    # x, y positions and width(sx), height(sy)
    def __init__(self,x,y,sx,sy,speed):
        self.x = x
        self.y = y
        self.sx = sx
        self.sy = sy
        self.speed = speed

        self.isCrossed = False
        self.rect = pygame.Rect(0,0,self.sx,self.sy)

    def move(self):
        if self.isCrossed == False:
            self.x += self.speed
            self.rect.center = [self.x,self.y]
    
    def crosscheck(self,rect):
        if self.rect.colliderect(rect):
            self.isCrossed = True
        else: self.isCrossed = False
    
    

class my_unit(units):
    # HP, MP ,shield, strength, range, defensive power, shield defensive power
    # magic (mag), attack cooldown, movement speed
    # name, positions, width (sx), height (sy), image(img), cost
    def __init__(self,HP,MP,shield,strength,attack_range,defense,s_def,mag,cooldown,speed,name,x,y,sx,sy,img,cost):
        self.HP = HP
        self.MP = MP
        self.shield = shield
        self.strength = strength
        self.attack_range = attack_range
        self.defense =  defense
        self.s_def = s_def
        self.mag = mag      # dictionary type : spell, cost
        self.cooldown = cooldown
        self.speed = speed
        self.name = name
        self.x = x
        self.y = y
        self.sx = sx
        self.sy = sy
        self.img = img
        self.cost = cost

        self.isCrossed = False
        self.rect = pygame.Rect(0,0,self.sx,self.sy)

# our team unit list, position data
team_list = []
team_position = []
team_num = 0

class enemy(units):
    # HP, MP ,shield, strength, range, defensive power, shield defensive power
    # magic (mag), attack cooldown, movement speed
    # name, positions, width (sx), height (sy), image (img)
    def __init__(self,HP,MP,shield,strength,attack_range,defense,s_def,mag,cooldown,speed,name,x,y,sx,sy,img):
        self.HP = HP
        self.MP = MP
        self.shield = shield
        self.strength = strength
        self.attack_range = attack_range
        self.defense =  defense
        self.s_def = s_def
        self.mag = mag      # dictionary type : spell, cost
        self.cooldown = cooldown
        self.speed = speed
        self.name = name
        self.x = x
        self.y = y
        self.sx = sx
        self.sy = sy
        self.img = img

        self.isCrossed = False
        self.rect = pygame.Rect(world_width-self.sx,world_height/2-self.sy,self.sx,self.sy)
    

# images for enemies
img_zombie = pygame.image.load("defense_game\zombie.png")
img_zombie = pygame.transform.scale(img_zombie,(40,40))

# enemy dictionary for all stages
zombie = enemy(20,0,0,8,5,0,0,"none",60,-1,"zombie",0,0,40,40,img_zombie)
enemy_dict = [zombie]

# enemy list for single stage
enemy_list = []
enemy_position = []
enemy_num = 0

# class for stage information
class stages():
    global enemy_list

    # stage level, initial monsters, base HP, spawn time for monster, half burn (yes/no)
    def __init__(self,lv,init,base_HP,spawn,half_burn="yes"):
        self.lv = lv
        self.init = init
        self.base_HP = base_HP
        self.spawn = spawn
        self.half_burn = half_burn
    
    def setup(self):
        enemy_list.clear()

        for key in self.init:
            for i in range(self.init[key]):
                for mob in enemy_dict:
                    if key == mob.name:
                        pos_x = random.randrange(world_width*3/4,world_width-mob.sx)
                        pos_y = world_height/2-mob.sy/2
                        enemy_list.append(enemy(mob.HP,mob.MP,mob.shield,mob.strength,mob.attack_range,mob.defense,mob.s_def,mob.mag,mob.cooldown,mob.speed,mob.name,pos_x,pos_y,mob.sx,mob.sy,mob.img))
                        break
        
        for mob in enemy_list:
            world.blit(mob.img,mob.rect)

# stages
s1 = stages(1,{"zombie":3},1000,150)

# bases (our base + enemy base)
img_our_base = pygame.image.load("defense_game\our_base.png")
img_our_base = pygame.transform.scale(img_our_base,(int(world_width/8),int(world_height/4)))
rect_our_base = img_our_base.get_rect()
rect_our_base.center = [world_width/16+10,world_height*3/8]
base_HP = 5000

img_enemy_base = pygame.image.load("defense_game\enemy_base.png")
img_enemy_base = pygame.transform.scale(img_enemy_base,(int(world_width/8),int(world_height/4)))
rect_enemy_base = img_enemy_base.get_rect()
rect_enemy_base.center = [world_width*15/16-10,world_height*3/8]
tower_HP = s1.base_HP

# stage buttons
button_s1 = pygame.Rect(10,world_height/8+10,world_width/8-20,world_height/4-20)
button_s2 = pygame.Rect(world_width/8+10,world_height/8+10,world_width/8-20,world_height/4-20)
button_s3 = pygame.Rect(world_width/4+10,world_height/8+10,world_width/8-20,world_height/4-20)
button_s4 = pygame.Rect(world_width*3/8+10,world_height/8+10,world_width/8-20,world_height/4-20)
button_s5 = pygame.Rect(world_width/2+10,world_height/8+10,world_width/8-20,world_height/4-20)
button_s6 = pygame.Rect(world_width*5/8+10,world_height/8+10,world_width/8-20,world_height/4-20)
button_s7 = pygame.Rect(world_width*3/4+10,world_height/8+10,world_width/8-20,world_height/4-20)
button_s8 = pygame.Rect(world_width*7/8+10,world_height/8+10,world_width/8-20,world_height/4-20)

button_s9 = pygame.Rect(10,world_height*3/8+10,world_width/8-20,world_height/4-20)
button_s10 = pygame.Rect(world_width/8+10,world_height*3/8+10,world_width/8-20,world_height/4-20)
button_s11 = pygame.Rect(world_width/4+10,world_height*3/8+10,world_width/8-20,world_height/4-20)
button_s12 = pygame.Rect(world_width*3/8+10,world_height*3/8+10,world_width/8-20,world_height/4-20)
button_s13 = pygame.Rect(world_width/2+10,world_height*3/8+10,world_width/8-20,world_height/4-20)
button_s14 = pygame.Rect(world_width*5/8+10,world_height*3/8+10,world_width/8-20,world_height/4-20)
button_s15 = pygame.Rect(world_width*3/4+10,world_height*3/8+10,world_width/8-20,world_height/4-20)
button_s16 = pygame.Rect(world_width*7/8+10,world_height*3/8+10,world_width/8-20,world_height/4-20)

# text print wrapper fuction
class text_print():
    def __init__(self,sentence,x,y,color=BLACK,size="normal"):
        self.sentence = sentence
        self.x = x
        self.y = y
        self.color = color
        self.size = size

    def printout(self):
        if self.size == "small":
            myword = my_sFont.render(self.sentence,True,self.color)
        else:
            myword = myFont.render(self.sentence,True,self.color)
        
        rect_myword = myword.get_rect()
        rect_myword.center = [self.x, self.y]
        world.blit(myword,rect_myword)

main = True
page = "main"
map_page = "map1"
stage_now = s1      # current stage (default : s1, the first battle stage)
while main:
    # This limits the while loop to a max of (default:30) times per second.
    # Leave this out and we will use all CPU we can.    
    clock.tick(30)

    # main setup : text generation
    world.fill(WHITE)

    # main event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            try:
                sys.exit()
            finally:
                main = False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            if page == "main":
                if button_my.collidepoint(pos):
                    page = "character"
                
                elif button_stage.collidepoint(pos):
                    page = "stage"
                    map_page = "map1"
                
                elif button_unit.collidepoint(pos):
                    page = "unit_list"
                
                elif button_shop.collidepoint(pos):
                    page = "shop"
                
            elif page == "character":
                if button_back.collidepoint(pos):
                    page = "main"

            elif page == "stage":
                if button_back.collidepoint(pos):
                    page = "main"
                
                if map_page == "map1":
                    if button_s1.collidepoint(pos):
                        page = "battle"
                        stage_now = s1
                        stage_now.setup()
                        tower_HP = stage_now.base_HP
                        spawn_time = stage_now.spawn
            
            elif page == "unit_list":
                if button_back.collidepoint(pos):
                    page = "main"
            
            elif page == "shop":
                if button_back.collidepoint(pos):
                    page = "main"
    

    if page == "main":
        # my information : upgrade main character, equipments
        pygame.draw.rect(world,BLACK,[10,world_height/8,world_width/4-20,world_height/2],3,20)
        text_print("Main character",world_width/8,world_height*3/8).printout()

        # stage menu
        pygame.draw.rect(world,BLACK,[world_width/4+10,world_height/8,world_width/4-20,world_height/2],3,20)
        text_print("Stage",world_width*3/8,world_height*3/8).printout()

        # unit list : upgrade units in our team
        pygame.draw.rect(world,BLACK,[world_width/2+10,world_height/8,world_width/4-20,world_height/2],3,20)
        text_print("Unit list",world_width*5/8,world_height*3/8).printout()

        # diamond shop for other items
        pygame.draw.rect(world,BLACK,[world_width*3/4+10,world_height/8,world_width/4-20,world_height/2],3,20)
        text_print("Diamond shop",world_width*7/8,world_height*3/8).printout()

    elif page == "stage":
        # button : back to the main menu
        pygame.draw.rect(world,BLACK,[10,10,world_height/8-20,world_height/8-20],2,3)

        # buttons : move to fight
        pygame.draw.rect(world,BLACK,[10,world_height/8+10,world_width/8-20,world_height/4-20],2,3)
        pygame.draw.rect(world,BLACK,[world_width/8+10,world_height/8+10,world_width/8-20,world_height/4-20],2,3)
        pygame.draw.rect(world,BLACK,[world_width/4+10,world_height/8+10,world_width/8-20,world_height/4-20],2,3)
        pygame.draw.rect(world,BLACK,[world_width*3/8+10,world_height/8+10,world_width/8-20,world_height/4-20],2,3)
        pygame.draw.rect(world,BLACK,[world_width/2+10,world_height/8+10,world_width/8-20,world_height/4-20],2,3)
        pygame.draw.rect(world,BLACK,[world_width*5/8+10,world_height/8+10,world_width/8-20,world_height/4-20],2,3)
        pygame.draw.rect(world,BLACK,[world_width*3/4+10,world_height/8+10,world_width/8-20,world_height/4-20],2,3)
        pygame.draw.rect(world,BLACK,[world_width*7/8+10,world_height/8+10,world_width/8-20,world_height/4-20],2,3)

        pygame.draw.rect(world,BLACK,[10,world_height*3/8+10,world_width/8-20,world_height/4-20],2,3)
        pygame.draw.rect(world,BLACK,[world_width/8+10,world_height*3/8+10,world_width/8-20,world_height/4-20],2,3)
        pygame.draw.rect(world,BLACK,[world_width/4+10,world_height*3/8+10,world_width/8-20,world_height/4-20],2,3)
        pygame.draw.rect(world,BLACK,[world_width*3/8+10,world_height*3/8+10,world_width/8-20,world_height/4-20],2,3)
        pygame.draw.rect(world,BLACK,[world_width/2+10,world_height*3/8+10,world_width/8-20,world_height/4-20],2,3)
        pygame.draw.rect(world,BLACK,[world_width*5/8+10,world_height*3/8+10,world_width/8-20,world_height/4-20],2,3)
        pygame.draw.rect(world,BLACK,[world_width*3/4+10,world_height*3/8+10,world_width/8-20,world_height/4-20],2,3)
        pygame.draw.rect(world,BLACK,[world_width*7/8+10,world_height*3/8+10,world_width/8-20,world_height/4-20],2,3)
       
        text_print(f"stage {map_page[-1]}-1",world_width/16,world_height/4).printout()
        text_print(f"stage {map_page[-1]}-2",world_width*3/16,world_height/4).printout()
        text_print(f"stage {map_page[-1]}-3",world_width*5/16,world_height/4).printout()
        text_print(f"stage {map_page[-1]}-4",world_width*7/16,world_height/4).printout()
        text_print(f"stage {map_page[-1]}-5",world_width*9/16,world_height/4).printout()
        text_print(f"stage {map_page[-1]}-6",world_width*11/16,world_height/4).printout()
        text_print(f"stage {map_page[-1]}-7",world_width*13/16,world_height/4).printout()
        text_print(f"stage {map_page[-1]}-8",world_width*15/16,world_height/4).printout()

        text_print(f"stage {map_page[-1]}-9",world_width/16,world_height/2).printout()
        text_print(f"stage {map_page[-1]}-10",world_width*3/16,world_height/2).printout()
        text_print(f"stage {map_page[-1]}-11",world_width*5/16,world_height/2).printout()
        text_print(f"stage {map_page[-1]}-12",world_width*7/16,world_height/2).printout()
        text_print(f"stage {map_page[-1]}-13",world_width*9/16,world_height/2).printout()
        text_print(f"stage {map_page[-1]}-14",world_width*11/16,world_height/2).printout()
        text_print(f"stage {map_page[-1]}-15",world_width*13/16,world_height/2).printout()
        text_print(f"stage {map_page[-1]}-16",world_width*15/16,world_height/2).printout()

    elif page == "battle":
        # draw our base and enemy base
        world.blit(img_our_base,rect_our_base)
        world.blit(img_enemy_base,rect_enemy_base)

        # draw the field
        pygame.draw.rect(world,BROWN,[0,world_height/2,world_width,world_height/2+10])

        # draw unit selector
        pygame.draw.rect(world,BLACK,[10,world_height/2+80,world_width/10-20,world_width/10-20],2)
        pygame.draw.rect(world,BLACK,[world_width/10+10,world_height/2+80,world_width/10-20,world_width/10-20],2)
        pygame.draw.rect(world,BLACK,[world_width/5+10,world_height/2+80,world_width/10-20,world_width/10-20],2)
        pygame.draw.rect(world,BLACK,[world_width*3/10+10,world_height/2+80,world_width/10-20,world_width/10-20],2)
        pygame.draw.rect(world,BLACK,[world_width*2/5+10,world_height/2+80,world_width/10-20,world_width/10-20],2)
        pygame.draw.rect(world,BLACK,[world_width/2+10,world_height/2+80,world_width/10-20,world_width/10-20],2)
        pygame.draw.rect(world,BLACK,[world_width*3/5+10,world_height/2+80,world_width/10-20,world_width/10-20],2)
        pygame.draw.rect(world,BLACK,[world_width*7/10+10,world_height/2+80,world_width/10-20,world_width/10-20],2)
        pygame.draw.rect(world,BLACK,[world_width*4/5+10,world_height/2+80,world_width/10-20,world_width/10-20],2)

        # silver gauge
        pygame.draw.rect(world,RED,[10,world_height/2+20,world_width/3*silver/max_silver,40])
        pygame.draw.rect(world,BLACK,[10,world_height/2+20,world_width/3,40],2)
        if silver < max_silver: silver += 1
        if silver > max_silver: silver = max_silver
        text_print(f"silver : {silver}/{max_silver}",world_width/6+5,world_height/2+40).printout()

        # mana gauge
        pygame.draw.rect(world,BLUE,[world_width/2+10,world_height/2+20,world_width/3*mana/max_mana,40])
        pygame.draw.rect(world,BLACK,[world_width/2+10,world_height/2+20,world_width/3,40],2)
        if mana < max_mana : mana += 1.0
        if mana > max_mana : mana = max_mana
        text_print(f"mana : {mana}/{max_mana}",world_width*2/3+5,world_height/2+40).printout()

        # enemy spawn
        if spawn_time == 0:
            ball = []
            mob_name = "zombie"
            num_balls = 0
            for key in stage_now.init:
                if ball:
                    ball.append(stage_now.init[key]+ball[-1])
                else:
                    ball.append(stage_now.init[key])
            
            num_balls = ball[-1]
            picker = random.randrange(1,num_balls+1)
            num_check = 0

            for key in stage_now.init:
                if num_check == 0:
                    if picker <= stage_now.init[key]:
                        mob_name = key
                        break
                    else:
                        num_check += stage_now.init[key]
                
                else:
                    if picker <= stage_now.init[key]+num_check:
                        mob_name = key
                        break
                    else:
                        num_check += stage_now.init[key]
            
            for mob in enemy_dict:
                if mob.name == mob_name:
                    enemy_list.append(enemy(mob.HP,mob.MP,mob.shield,mob.strength,mob.attack_range,mob.defense,mob.s_def,mob.mag,mob.cooldown,mob.speed,mob.name,world_width*15/16,world_height/2-mob.sy/2,mob.sx,mob.sy,mob.img))

            spawn_time = stage_now.spawn
        
        else:
            spawn_time -= 1

        # rect cross check
        # find unit whose position is closest to enemy base
        vanguard_index = 0
        if team_num != len(team_list):
            if len(team_list) > team_num:
                for i in range(len(team_list)-team_num):
                    team_position.append(team_list[team_num+i].x+team_list[team_num+i].speed/abs(team_list[team_num+i].speed)*team_list[team_num+i].sx/2)
                
                vanguard_index = team_position.index(max(team_position))
            
            else:
                team_position.pop(vanguard_index)
                if team_position:
                    vanguard_index = team_position.index(max(team_position))
            
            team_num = len(team_list)

        # find enemy whose position is closest to our base
        pop_index = 0
        if enemy_num != len(enemy_list):
            if len(enemy_list) > enemy_num:
                for i in range(len(enemy_list)-enemy_num):
                    enemy_position.append(enemy_list[enemy_num+i].x+enemy_list[enemy_num+i].speed/abs(enemy_list[enemy_num+i].speed)*enemy_list[enemy_num+i].sx/2)
                
                pop_index = enemy_position.index(min(enemy_position))
            
            else:
                enemy_position.pop(pop_index)
                if enemy_position:
                    pop_index = enemy_position.index(min(enemy_position))

            enemy_num = len(enemy_list)
            
        # collision test for enemy
        for mob in enemy_list:
            if team_list:
                mob.crosscheck(team_list[vanguard_index].rect)
            
            mob.crosscheck(rect_our_base)
        
        # collision test for units
        for unit in team_list:
            if enemy_list:
                unit.crosscheck(enemy_list[pop_index].rect)
            
            unit.crosscheck(rect_enemy_base)

        # our unit, enemy move
        if team_list:
            for unit in team_list:
                unit.move()
                world.blit(unit.img,unit.rect)

        if enemy_list:
            for mob in enemy_list:
                mob.move()
                world.blit(mob.img,mob.rect)

    elif page == "character":
        # button : back to the main menu
        pygame.draw.rect(world,BLACK,[10,10,world_height/8-20,world_height/8-20],2,3)

    elif page == "unit_list":
        # button : back to the main menu
        pygame.draw.rect(world,BLACK,[10,10,world_height/8-20,world_height/8-20],2,3)

        # button : unit list
        pygame.draw.rect(world,BLACK,[10,world_height/8+10,world_width/6-20,world_width/6-30],2,3)
        pygame.draw.rect(world,BLACK,[world_width/6+10,world_height/8+10,world_width/6-20,world_width/6-30],2,3)
        pygame.draw.rect(world,BLACK,[world_width/3+10,world_height/8+10,world_width/6-20,world_width/6-30],2,3)
        pygame.draw.rect(world,BLACK,[10,world_height/8+world_width/6+10,world_width/6-20,world_width/6-30],2,3)
        pygame.draw.rect(world,BLACK,[world_width/6+10,world_height/8+world_width/6+10,world_width/6-20,world_width/6-30],2,3)
        pygame.draw.rect(world,BLACK,[world_width/3+10,world_height/8+world_width/6+10,world_width/6-20,world_width/6-30],2,3)
        pygame.draw.rect(world,BLACK,[10,world_height/8+world_width/3+10,world_width/6-20,world_width/6-30],2,3)
        pygame.draw.rect(world,BLACK,[world_width/6+10,world_height/8+world_width/3+10,world_width/6-20,world_width/6-30],2,3)
        pygame.draw.rect(world,BLACK,[world_width/3+10,world_height/8+world_width/3+10,world_width/6-20,world_width/6-30],2,3)


    elif page == "shop":
        # button : back to the main menu
        pygame.draw.rect(world,BLACK,[10,10,world_height/8-20,world_height/8-20],2,3)

    # update the screen with what we have done.
    # This MUST happen after all the other drawing commands
    pygame.display.flip()