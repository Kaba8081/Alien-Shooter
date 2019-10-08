from ast import literal_eval
from network import *
import pickle
import pygame
import os

pygame.init()

net = Network()

WIDTH, HEIGHT = 608, 416 
RESOLUTION = (WIDTH, HEIGHT)
RESOLUTION_LIST = ["600;400","800;600","1024;720"]
TILESIZE = 32
BACKGROUND = (0,0,0)
OFFSET = [9, 6]
MAP_OFFSET = [0, 0]
FULL_OFFSET = [0, 0]
PLAYER_POS = [0, 0]
PLAYER_SPEED = 1
SPEED_DIVIDE = 2
FPS = 60
OTHER_PLAYERS = 1
OTHER_PLAYERS_LIST = []

screen = pygame.display.set_mode(RESOLUTION)
pygame.display.set_caption("Alien Shooter 2D")
clock = pygame.time.Clock()

done = False
img_dir = os.path.join(os.path.join(os.path.dirname(__file__), "data"),"img")
level_dir = os.path.join(os.path.join(os.path.dirname(__file__), "data"),"levels")
player_img = pygame.transform.scale(pygame.image.load(os.path.join(img_dir,'player.png')).convert_alpha(),(32,32))
tile_textures = []

Tiles = ['-','-','-','dirt1','dirt2']

for tile in Tiles:
    try:
        tile_textures.append(pygame.transform.scale(pygame.image.load(os.path.join(img_dir,'{0}.png'.format(tile))).convert_alpha(),(TILESIZE,TILESIZE)))
    except pygame.error:
        tile_textures.append('None')
        print('texture "{0}" is missing!'.format(tile))

OtherPlayers = pygame.sprite.Group()
allSprites = pygame.sprite.Group()
allTiles = pygame.sprite.Group()
Font = pygame.font.Font(os.path.join(os.path.join(os.path.dirname(__file__), "data"), "Arial.ttf"), 25)

try:
    Font3 = pygame.font.SysFont("Arial", 30, bold=False, italic=False)
except:
    Font3 = pygame.font.SysFont(os.path.join(os.path.join(os.path.dirname(__file__), "data"), "Arial.ttf"), 30, bold=False, italic=False)
 
class Tile(pygame.sprite.Sprite):  # tilesprite class
    def __init__(self, x, y, id, image):
        pygame.sprite.Sprite.__init__(self)
         
        self.image = image
        self.id = id

        self.x, self.y = x, y

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = (x + OFFSET[0]) * TILESIZE, (y + OFFSET[1]) * TILESIZE

    def update(self, x, y):
        self.rect.x += x
        self.rect.y += y

class OtherPlayer(pygame.sprite.Sprite):
    def __init__(self, x, y, nickname):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((32, 32))
        self.image.fill((60, 130, 255))

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x + MAP_OFFSET[0] + (OFFSET[0] * TILESIZE), y + MAP_OFFSET[1] + (OFFSET[1] * TILESIZE)
        self.x, self.y = x + OFFSET[1], y + OFFSET[1]

        self.label = Font.render(nickname, 1 ,(255, 255, 255))
        self.label_dimensions = self.label.get_width(), self.label.get_height()
        self.label_pos = self.rect.centerx - self.label_dimensions[0]/2 , self.rect.centery + self.label_dimensions[1]/2
        self.nickname = nickname

    def update(self, r, offset):
        self.rect.x, self.rect.y = -r[1][2][r[1][1].index(self.nickname)][0] + (OFFSET[0] * TILESIZE), -r[1][2][r[1][1].index(self.nickname)][1] + (OFFSET[1] * TILESIZE)

        self.rect.x += offset[0]
        self.rect.y += offset[1]

    def draw_label(self, offset):
        self.label_pos = self.rect.centerx - self.label_dimensions[0]/2 , self.rect.centery + self.label_dimensions[1]/2

        screen.blit(self.label, (self.label_pos[0], self.label_pos[1]))

class Player(pygame.sprite.Sprite):  # main player class
    def __init__(self, x, y, player_img):
        pygame.sprite.Sprite.__init__(self)
        self.x, self.y = x, y
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = WIDTH/2, HEIGHT/2
    
    def move(self, speedx, speedy, allTiles, MAP_OFFSET):
        speedx = speedx / SPEED_DIVIDE
        speedy = speedy / SPEED_DIVIDE
        
        if speedx != 0:
            for tile in allTiles:
                #if tile.rect.left == self.rect.right + speedx or tile.rect.left == self.rect.right + speedx:
                #    pass
                if self.rect.colliderect(tile.rect):
                    #if speedx > 0: # Going right
                    #    pass
                    #if speedx < 0: # Going left
                    #    self.rect.left = tile.rect.right
                else:
                    MAP_OFFSET[0] += speedx
                    PLAYER_POS[0] += speedx
            
        if speedy != 0:
            for tile in allTiles:
                #if tile.rect.top == self.rect.bottom + speedy or tile.rect.bottom == self.rect.top + speedy:
                #    pass
                if self.rect.colliderect(tile.rect):
                    #if speedy > 0: # Going up
                    #    self.rect.top = tile.rect.bottom
                    #if speedy < 0: # Going down
                    #    self.rect.bottom = tile.rect.top
                else:
                    MAP_OFFSET[1] += speedy
                    PLAYER_POS[1] += speedy

class Button():  # menu button class
    def __init__(self, x, y, text, text_x, text_y, color, font, return_value, width=140, height=60):
        self.font, self.text, self.color, self.return_value = font, text, color, return_value
        self.x, self.y, self.text_x, self.text_y = x, y, x+text_x, y+text_y
        self.width, self.height = width, height
        self.label = self.font.render(self.text, 1, (255,255,255))
    
    def update(self):
        pygame.draw.rect(screen, self.color, pygame.Rect(self.x, self.y, self.width, self.height))
        screen.blit(self.label, (self.text_x, self.text_y))

        x, y = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()
        if pressed[0]:
            if (x > self.x and y > self.y) and (x < (self.x + self.width) and y < (self.y + self.height)):
                return self.return_value
            else:
                return 0
        else:
            return 0

def make_pos(x,y):
    return "{0},{1}".format(x,y)

def get_pos(pos):
    pos = pos.split(",")
    return round(float(pos[0]), 2), round(float(pos[1]), 2)

def check_for_new_players(req, OTHER_PLAYERS, OTHER_PLAYERS_LIST, nickname):

    print("[debug] req: {0}".format(req))
    print("[debug] req[1]: {0}".format(req[1]))

    while True:
        if req[1][0] > OTHER_PLAYERS:
            for player in req[1][1]:
                if player != nickname and player not in OTHER_PLAYERS_LIST:
                    OTHER_PLAYERS_LIST.append(player)
                    OTHER_PLAYERS += 1

                    index = req[1][1].index(player)
                    pos = req[1][2][index]

                    op = OtherPlayer(pos[0], pos[1], player)
                    OtherPlayers.add(op)

                    break
            return
        else:
            return

def game_loop(n, nickname, MAP_OFFSET):

    # TODO:
    # player movement
    # player textures and animations

    req1 = n.send("REQUEST_LOAD_CHARACTER-{0};0,0".format(nickname))
    req2 = literal_eval(n.send("REQUEST_LOAD_LEVEL;0,0"))

    with open(os.path.join(level_dir,str(req2[0][0])), 'rb') as file:
        level = pickle.load(file)
        print("level {0} loaded".format(req2[0][0]))

    global start_x, start_y
    for row_num, row in enumerate(level):
        for col_num, col in enumerate(row):
            if col == 0:
                pass
            elif col == 1: # Player spawn
                start_x, start_y = row_num, col_num
            elif col == 2: # Enemy
                pass
            else:
                t = Tile(row_num, col_num, col, tile_textures[col])
                allTiles.add(t)

    p = Player(start_x, start_y, player_img)
    allSprites.add(p)

    while not done:
        request = []
        reply = ""

        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                n.send("REQUEST_LOGOUT;"+make_pos(p.x, p.y))
                pygame.quit()
                return
        
        try:
            print("request: '{0}', pos: '{1}'".format(request, make_pos(PLAYER_POS[0], PLAYER_POS[1])))
            reply =  literal_eval(n.send(str(request)+";"+make_pos(PLAYER_POS[0], PLAYER_POS[1])))
        except:
            label = Font3.render("Connection Lost!", 1, (255,255,255))
            screen.blit(label, (10,10))

        # update
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            p.move(PLAYER_SPEED, 0, allTiles, MAP_OFFSET)
        if keys[pygame.K_d]:
            p.move(-PLAYER_SPEED, 0, allTiles, MAP_OFFSET)
        if keys[pygame.K_w]:
            p.move(0, PLAYER_SPEED, allTiles, MAP_OFFSET)
        if keys[pygame.K_s]:
            p.move(0, -PLAYER_SPEED, allTiles, MAP_OFFSET)

        check_for_new_players(reply, OTHER_PLAYERS, OTHER_PLAYERS_LIST, nickname)

        allSprites.update()
        allTiles.update(MAP_OFFSET[0], MAP_OFFSET[1])
        FULL_OFFSET[0] += MAP_OFFSET[0]
        FULL_OFFSET[1] += MAP_OFFSET[1]
        OtherPlayers.update(reply, FULL_OFFSET)
        MAP_OFFSET = [0, 0]

        # draw
        screen.fill(BACKGROUND)
        allTiles.draw(screen)
        OtherPlayers.draw(screen)
        for pl in OtherPlayers:
            pl.draw_label()
        allSprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def search_for_a_game(MAP_OFFSET):
    n = Network()
    def search(n):
        index = 1
        tick = 0
        label = Font3.render("Szukanie gry.", 1, (255,255,255))
        
        while True:
            tick += 1
            screen.fill((0, 0, 0))
            screen.blit(label, (10, 10))
            connected = int(n.connect())
            if connected:
                return
            pygame.display.flip()
            clock.tick(60)
            if tick == 60:
                tick = 0
                
                if index == 1:
                    label = Font3.render("Szukanie gry..",1,(255,255,255))
                    index += 1
                elif index == 2:
                    label = Font3.render("Szukanie gry...",1,(255,255,255))
                    index += 1
                elif index == 3:
                    label = Font3.render("Szukanie gry.",1,(255,255,255))
                    index = 1 
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return 0

    def player_input():
        input_box = Font3.render("Podaj swój pseudonim:", 1, (255,255,255))
        text = ''
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return 0
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        print("player nickname: {0}".format(text))
                        return text
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
            
            screen.fill((0, 0, 0))
            txt = Font3.render(text, 1, (255,255,255))
            screen.blit(input_box, (10, 10))
            screen.blit(txt, (320, 10))
            pygame.display.flip()
            clock.tick(FPS)
    
    nickname = player_input()
    search(n)
    game_loop(n, nickname, MAP_OFFSET)

def options():
    while True:
        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.exit()
                return
        
        # update
        
        # draw
        screen.fill(BACKGROUND)
        clock.tick(60)
        pygame.display.flip()

def menu():
    mouse_buttons = pygame.mouse.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    buttons = []

    b = Button((WIDTH/2-70), (HEIGHT/2-120), "Start", 43, 13, (100, 245, 65), Font, 1)
    buttons.append(b)
    b = Button((WIDTH/2-70), (HEIGHT/2), "Opcje", 36, 13, (100, 245, 65), Font, 2)
    buttons.append(b)
    b = Button((WIDTH/2-70), (HEIGHT/2+120), "Wyjście", 26, 14, (200,40,30), Font, 3)
    buttons.append(b)

    while True:
        # pygame event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        # draw & button update
        for button in buttons:
            result = button.update()
                
            if result == 1:  # Start Game
                search_for_a_game(MAP_OFFSET)
            elif result == 2:  # Options
                options()
            elif result == 3:  # Exit
                done = True
                return

        # pygame draw
        pygame.display.flip()
        clock.tick(60)
        screen.fill(BACKGROUND)

if __name__ == "__main__":
    menu()