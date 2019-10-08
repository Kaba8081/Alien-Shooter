# level editor for a game caller dungeon keeper
from tkinter import *
from tkinter import ttk
import pygame
import pickle
import os

class Tile(pygame.sprite.Sprite):
    def __init__(self,x,y,value,TILESIZE,texture):
        pygame.sprite.Sprite.__init__(self)

        self.value = value
        self.texture = texture
        
        if texture != 'None':
            self.image = pygame.transform.scale(texture,(TILESIZE,TILESIZE))
        else:
            img_dir = os.path.join(os.path.join(os.path.dirname(__file__),'data'),'textures')
            self.image = pygame.transform.scale(pygame.image.load(os.path.join(img_dir,'missing.png')).convert_alpha(),(TILESIZE,TILESIZE))
            self.texture = self.image

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.x, self.y = x, y

    def update(self,draw_offset,TILESIZE):
        self.rect.x = (self.x + draw_offset[0]) *TILESIZE
        self.rect.y = (self.y + draw_offset[1]) *TILESIZE

        self.image = pygame.transform.scale(self.texture,(TILESIZE,TILESIZE))

def input1():
    root = Tk()
    root.title("Configuration")

    mainframe = ttk.Frame(root, padding='3 3 12 12')
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(0, weight=1)

    width = StringVar()
    height = StringVar()
    fill = StringVar()
    
    width_entry = ttk.Entry(mainframe, width=4, textvariable=width)
    width_entry.grid(column=0, row=1, sticky=(W, E))

    height_entry = ttk.Entry(mainframe, width=4, textvariable=height)
    height_entry.grid(column=1, row=1, sticky=(W, E))

    fill_entry = ttk.Entry(mainframe, width=4, textvariable=fill)
    fill_entry.grid(column=2, row=1, sticky=(W,E))

    ttk.Label(mainframe, text="Szerokość").grid(column=0, row=0, sticky=W)
    ttk.Label(mainframe, text="Wysokość").grid(column=1, row=0, sticky=W)
    ttk.Label(mainframe, text="Wypełnienie").grid(column=2, row=0, sticky=W)
    ttk.Button(mainframe, text="Gotowe", command=root.destroy).grid(column=1, row=2, sticky=W)

    for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

    root.mainloop() 

    if fill.get() == '':
         return (int(width.get()), int(height.get())), 0
    return (int(width.get()), int(height.get())), int(fill.get())

def editor(level_size,fill):

    # pygame stuff init
    pygame.init()
    Font = pygame.font.SysFont("Arial", 10,bold=False,italic=False)
    screen = pygame.display.set_mode((640,640))
    pygame.display.set_caption("Level editor")
    clock = pygame.time.Clock()
    allSprites = pygame.sprite.Group()

    # variables
    level = []
    TILESIZE = 16
    LIGHTGREY = (145,145,145)
    draw_offset = [0,0]
    block_list = ['-','gracz','wrog','dirt1','dirt2']
    current_block_id = 0
    current_block_name = block_list[current_block_id]

    # loading textures
    img_dir = os.path.join(os.path.join(os.path.dirname(__file__),'data'),'textures')
    tile_textures = []
    #files = os.listdir(img_dir)
    #for texture in files:
    #    tile_textures.append(pygame.transform.scale(pygame.image.load(os.path.join(img_dir,texture)).convert_alpha(),(TILESIZE,TILESIZE)))
    
    for tile in block_list:
        try:
            tile_textures.append(pygame.transform.scale(pygame.image.load(os.path.join(img_dir,'{0}.png'.format(tile))).convert_alpha(),(TILESIZE,TILESIZE)))
        except pygame.error:
            tile_textures.append('None')
            print('texture "{0}" is missing!'.format(tile))
            
    for x in range(level_size[0]):
        empty_list = []
        for y in range(level_size[1]):
            empty_list.append(fill)
            if fill != 0 and fill < len(block_list):
                t = Tile(x,y,fill,TILESIZE,tile_textures[fill])
                allSprites.add(t)
        level.append(empty_list)
        
    def draw_grid():
        for x in range(level_size[0]+1):
            pygame.draw.line(screen,LIGHTGREY, ((x+draw_offset[0])*TILESIZE,draw_offset[1]*TILESIZE),((x+draw_offset[0])*TILESIZE,(draw_offset[1]+level_size[0])*TILESIZE))
        for y in range(level_size[1]+1):
            pygame.draw.line(screen,LIGHTGREY, (draw_offset[0]*TILESIZE,(y+draw_offset[1])*TILESIZE),((draw_offset[0]+level_size[1])*TILESIZE,(y+draw_offset[1])*TILESIZE))
                
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break
            
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                
                if keys[pygame.K_RIGHT]:
                    draw_offset[0] += 1
                elif keys[pygame.K_LEFT]:
                    draw_offset[0] -= 1
                elif keys[pygame.K_UP]:
                    draw_offset[1] -= 1
                elif keys[pygame.K_DOWN]:
                    draw_offset[1] += 1
                elif keys[pygame.K_EQUALS]:
                    TILESIZE += 8
                elif keys[pygame.K_MINUS]:
                    if TILESIZE > 8:
                        TILESIZE -= 8
                elif keys[pygame.K_s]: # saving
                    def save():
                        file = open(os.path.join(os.path.join(os.path.dirname(__file__),'levels'),nameVar.get()),'wb')
                        pickle.dump(level,file)
                        root.destroy()

                    root = Tk()
                    root.title("Saving")

                    mainframe = ttk.Frame(root, padding="3 3 12 12")
                    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
                    mainframe.columnconfigure(0, weight=1)
                    mainframe.rowconfigure(0, weight=1)

                    nameVar = StringVar()
                    nameEntry = ttk.Entry(mainframe, width=15, textvariable=nameVar)
                    nameEntry.grid(column=0, row=1, sticky=(W, E))

                    ttk.Button(mainframe, text="Zapisz", command=save).grid(column=0, row=2, sticky=W)

                    ttk.Label(mainframe, text="Nazwa pliku:").grid(column=0, row=0, sticky=W)

                    for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

                    nameEntry.focus()
                    root.bind('return', save)

                    root.mainloop()
                elif keys[pygame.K_h]: # help menu
                    pass
                elif keys[pygame.K_f]:
                    pass
                elif keys[pygame.K_z]:
                    if current_block_id > 0:
                        current_block_id -= 1
                        current_block_name = block_list[current_block_id]
                elif keys[pygame.K_x]:
                    if current_block_id+1 != len(block_list):
                        current_block_id += 1
                        current_block_name = block_list[current_block_id]
                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pressed = pygame.mouse.get_pressed()              
                if mouse_pressed[0]: # LMB
                    if (mouse_pos[0]-draw_offset[0]*TILESIZE)/TILESIZE <= level_size[0] and (mouse_pos[1]-draw_offset[1]*TILESIZE)/TILESIZE <= level_size[1] and (mouse_pos[0]-draw_offset[0]*TILESIZE)/TILESIZE >= 0 and (mouse_pos[1]-draw_offset[1]*TILESIZE)/TILESIZE >= 0:
                        coords = int((mouse_pos[0]-draw_offset[0]*TILESIZE)/TILESIZE), int((mouse_pos[1]-draw_offset[1]*TILESIZE)/TILESIZE)
                        level[coords[0]][coords[1]] = current_block_id

                        if current_block_id != 0:
                            t = Tile(coords[0],coords[1],current_block_id,TILESIZE,tile_textures[current_block_id])
                            allSprites.add(t)

                elif mouse_pressed[2]: # RMB
                    if mouse_pos[0]/TILESIZE <= level_size[0] + draw_offset[0] and mouse_pos[1]/TILESIZE <= level_size[1] + draw_offset[1]:
                        coords = int(mouse_pos[0]/TILESIZE), int(mouse_pos[1]/TILESIZE)
                        level[coords[0]-draw_offset[0]][coords[1]-draw_offset[1]] = 0
                        
                        for tile in allSprites:
                            if tile.x == coords[0] - draw_offset[0] and tile.y == coords[1] - draw_offset[1]:
                                tile.kill()
                                print("test")
                        
        # update
        allSprites.update(draw_offset, TILESIZE)
        
        # draw
        screen.fill((0,0,0))
        draw_grid()
        allSprites.draw(screen)

        label = Font.render("current_block_name: {0}".format(current_block_name), 1, (255,255,255))
        screen.blit(label,(5,10))

        label = Font.render("current_block_id: {0}".format(current_block_id), 1, (255,255,255))
        screen.blit(label,(5,20))

        coords = int(mouse_pos[0]/TILESIZE),int(mouse_pos[1]/TILESIZE)
        if coords[0] <= (level_size[0]-1) + draw_offset[0] and coords[1] <= (level_size[1]-1) + draw_offset[1]:
            for tile in allSprites:
                if tile.x == coords[0] - draw_offset[0] and tile.y == coords[1] - draw_offset[1]:
                    label = Font.render("current_block: {0}, {1}".format(block_list[tile.value], tile.value), 1, (255,255,255))
                    screen.blit(label,(5,30))
                    break

        label = Font.render("current_pos: {0},{1}".format(int((mouse_pos[0]-draw_offset[0]*TILESIZE)/TILESIZE),int((mouse_pos[1]-draw_offset[1]*TILESIZE)/TILESIZE)),1,(255,255,255))
        
        screen.blit(label,(5,40))
        pygame.display.flip()
        clock.tick(60)

level_size, fill = input1()
print(level_size,fill)
editor(level_size,fill)
