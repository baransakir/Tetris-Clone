import pygame, random, sys

# Screen variables -> 800x600
WIN_WIDTH = 800
WIN_HEIGTH = 600
FPS = 60
GAME_WIDTH = 10   # 10*25 = 250
GAME_HEIGTH = 20  # 20*25 = 500

# Sounds
pygame.mixer.init()
game_theme = pygame.mixer.Sound("sounds\\theme.ogg")
move_sfx = pygame.mixer.Sound("sounds\\move.wav")
rotate_sfx = pygame.mixer.Sound("sounds\\rotate.wav")
space_sfx = pygame.mixer.Sound("sounds\\space.wav")
clear_sfx = pygame.mixer.Sound("sounds\\clear.wav")
maxclear_sfx = pygame.mixer.Sound("sounds\\maxclear.wav")
menu_sfx = pygame.mixer.Sound("sounds\\menu.wav")
gameover_sfx = pygame.mixer.Sound("sounds\\gameover.wav")
sound = True # sound on
sounds = [game_theme, move_sfx, rotate_sfx, space_sfx, clear_sfx, maxclear_sfx, menu_sfx, gameover_sfx]

# Colors -> (RED,GREEN,BLUE) 0-255
BLACK = (0,0,0)         # Background
GRAY = (105,105,105)    # Frame blocks
D_GRAY = (50,50,50)     # Game over, Menu
WHITE = (255,245,238)   # Texts
CYAN = (0,255,255)      # I-block
BLUE = (0,0,255)        # J-block
ORANGE = (255,128,0)    # L-block
YELLOW = (255,255,0)    # O-block
GREEN = (0,255,0)       # Z-block
PURPLE = (128,0,255)    # T-block
RED = (255,0,0)         # S-block

# Blocks -> 4x4 coordinates
'''
0     1     2     3
4     5     6     7
8     9     10    11
12    13    14    15
'''
I = [[4,5,6,7],[2,6,10,14]]                                 # 2 rotation
J = [[1,5,6,7],[2,3,6,10],[5,6,7,11],[2,6,9,10]]            # 4 rotation
L = [[3,5,6,7],[2,6,10,11],[5,6,7,9],[1,2,6,10]]            # 4 rotation
O = [[1,2,5,6]]                                             # 1 rotation
Z = [[1,2,6,7],[3,6,7,10]]                                  # 2 rotation
T = [[2,5,6,7],[2,6,7,10],[5,6,7,10],[2,5,6,10]]            # 4 rotation
S = [[2,3,5,6],[1,5,6,10]]                                  # 2 Rotation

blocks = [I, J, L, O, Z, T, S]
colors = [CYAN, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED]

class Block:      # Block Object
      def __init__(self, x, y):
            self.x = x
            self.y = y
            self.shape = blocks[random.randint(0, len(blocks)-1)] # blocks[0] - blocks[6]
            self.color_index = blocks.index(self.shape) # 0 - 6
            self.rotation = 0 # default self.shape[0]

      def get_block(self): # return current shape
            return self.shape[self.rotation]

      def rotate_block(self): # rotation limit -> 0 - len(blocks[i])
            self.rotation = (self.rotation + 1) % len(self.shape) 

class Game:
      # Variable initialization
      lines_cleared = 0
      score = 0
      score_mul = 125 # score multiplier
      game_over = False # start value
      pause = False # P key
      music_sound = True # initially ON
      # Menu button colors
      on_color = WHITE
      off_color = GRAY

      def __init__(self, width, height):
            self.width = width
            self.height = height
            self.block = None
            self.next_block = Block(3, 0)
            self.grid_bg = self.create_grid()
            self.statistic = [0,0,0,0,0,0,0]
            self.music = self.create_music()
            self.mute_sound(sound) # unmute

      def create_grid(self):
            grid_bg = []
            for y in range(self.height + 2):
                  new_line = []
                  for x in range(self.width):
                        new_line.append(-1) # -1 -> dummy color index (empty)
                  grid_bg.append(new_line)
            return grid_bg # 10x20 field, 200 grids (-1)

      def create_music(self):
            if self.music_sound:
                  game_theme.play(-1) # start game music

      def spawn_block(self):        # random block is spawned from 4th grid
            self.block = self.next_block
            self.next_block = Block(3, 0)

      def is_colliding(self):       # boolean value of block collision
            collision = False
            for y in range(4): # gets block coordinates -> 4 numbers
                  for x in range(4):
                        if y * 4 + x in self.block.get_block():
                              # first 3 lines: check bot, right, left boundaries
                              # last line: checks location is filled or not
                              if (y + self.block.y) > (self.height - 1) or \
                                    (x + self.block.x) > (self.width - 1) or\
                                    (x + self.block.x) < 0 or\
                                    self.grid_bg[y + self.block.y][x + self.block.x] > -1:
                                    collision = True
            return collision

      def fix_block(self):    # make blocks immutable
            for y in range(4): # get block coordinates -> 4 numbers
                  for x in range(4):
                        if y * 4 + x in self.block.get_block():
                              self.grid_bg[self.block.y + y][self.block.x + x] = self.block.color_index
            self.statistic[self.block.color_index] += 1
            self.clear_lines() # check completed rows after fixing, clear if there any

            self.spawn_block()
            if self.is_colliding(): # if new block is colliding initially stop the game. game is over
                  self.game_over = True
                  self.block.y -= 1 # end game bug fix
                  gameover_sfx.play()
                  game_theme.stop()

      def clear_lines(self):        # delete completed lines
            completed_lines = 0
            for y in range(self.height):
                  is_completed = True
                  for x in range(self.width):
                        if self.grid_bg[y][x] == -1: # -1 -> empty space (no colors index), incompleted row
                              is_completed = False
                              break
                  if is_completed: # rebuilt rows -> y = y-1
                        completed_lines += 1
                        for new_y in range(y,1,-1):
                              for x in range(self.width):
                                    self.grid_bg[new_y][x] = self.grid_bg[new_y-1][x]
                        clear_sfx.play() # clear sound

            # Score calculation -> expotential
            if(completed_lines == 4):
                  self.score += 2000
                  maxclear_sfx.play()
            else:
                  self.score += (completed_lines ** 2) * self.score_mul
            self.lines_cleared += completed_lines

      # Key actions
      def move_down(self, press_down):    # move 1 unit down, Down arrow key
            self.block.y += 1
            if self.is_colliding(): # if collides, fix 1 unit up
                  self.block.y -= 1
                  self.fix_block()
                  space_sfx.play()
            if press_down:
                  move_sfx.play()

      def move_horizontal(self, x):       # move 1 unit right or left, Right and Left arrow keys
            prev_x = self.block.x # hold current x pos
            self.block.x += x
            if self.is_colliding(): # if collides, return previous position
                  self.block.x = prev_x
            else:
                  move_sfx.play()

      def rotate(self):       # rotate 90 degree right
            prev_rotation = self.block.rotation # hold current rotation
            self.block.rotate_block()
            if self.is_colliding(): # if collides, return previous rotation
                  self.block.rotation = prev_rotation
            else:
                  rotate_sfx.play()

      def place_block(self):        # lock block
            while not self.is_colliding():
                  self.block.y += 1
            self.block.y -= 1
            self.fix_block()
            space_sfx.play()

      def pause_music(self):        # mute/unmute game theme
            if self.music_sound and not self.pause: # mute
                  self.music_sound = False
                  self.pause = True
                  pygame.mixer.pause()
                  menu_sfx.play()
            elif not self.music_sound and self.pause: # unmute
                  self.music_sound = True
                  self.pause = False
                  pygame.mixer.unpause()

      def set_volumes(self):
            game_theme.set_volume(0.05)
            move_sfx.set_volume(0.1)
            rotate_sfx.set_volume(0.05)
            space_sfx.set_volume(0.1)
            menu_sfx.set_volume(0.2)
            clear_sfx.set_volume(0.1)
            maxclear_sfx.set_volume(0.1)
            gameover_sfx.set_volume(0.05)

      def mute_sound(self, sound):        # mute all sounds
            if sound:
                  self.on_color = WHITE
                  self.off_color = GRAY
                  self.set_volumes()
            else:
                  self.on_color = GRAY
                  self.off_color = WHITE 
                  for i in range(0, len(sounds)):
                        sounds[i].set_volume(0)
            return sound

def main():
      global WIN_WIDTH,WIN_HEIGTH,GAME_WIDTH,GAME_HEIGTH,FPS,sound
      box_scale = 25
      x_pos = (WIN_WIDTH - GAME_WIDTH * box_scale) // 2
      y_pos = WIN_HEIGTH - GAME_HEIGTH * box_scale - 1 # -1 for gridline
      speed_limit = 25
      counter = 0 # setting game speed
      press_down = False # Down arrow key
      run = True

      pygame.display.set_caption("NOT TETRIS") # Window name
      main_screen = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGTH))
      game = Game(GAME_WIDTH,GAME_HEIGTH)
      clock = pygame.time.Clock()

      pygame.font.init() # font
      # Fonts -> font type, font size
      font = pygame.font.Font("fonts\\ARCADE_N.ttf", 16)
      font2 = pygame.font.Font("fonts\\ARCADE_N.ttf", 32)
      # Texts -> text, antialias (smooth edges), color
      text_stat = font.render("STATISTICS", False, WHITE)
      text_blocks = ["","","","","","",""]      
      text_lines = font.render("LINES", False, WHITE)
      text_score = font.render("SCORE", False, WHITE)
      text_next = font.render("NEXT", False, WHITE)
      text_pause = font2.render("PAUSE", False, WHITE)
      text_p = font.render("RESUME -> PRESS P", False, WHITE)
      text_r = font.render("RESET -> PRESS R", False, WHITE)
      text_esc = font.render("QUIT -> PRESS ESC", False, WHITE)
      text_sound = font.render("SOUND -> PRESS M", False, WHITE)
      text_gameover = font2.render("GAME OVER", False, WHITE)

      pygame.init()
      while run:
            if game.block is None:
                  game.spawn_block()

            if press_down: # Down arrow key delay - 60ms
                  pygame.time.delay(60)

            counter += 1 # Fall speed limitation
            if counter == speed_limit or press_down:
                  if not game.game_over and not game.pause:
                        game.move_down(press_down)
                  counter = 0

            # Key assignments
            for event in pygame.event.get():
                  if event.type == pygame.KEYDOWN: # pressing key
                        if event.key == pygame.K_ESCAPE: # ESC key
                              pygame.quit()
                              sys.exit()
                        elif event.key == pygame.K_p and not game.game_over: # pause key
                              game.pause_music()                        
                        elif event.key == pygame.K_r and (game.game_over or game.pause): # restart key
                              game_theme.stop()
                              game = Game(GAME_WIDTH, GAME_HEIGTH)
                              pygame.time.delay(60)
                        elif event.key == pygame.K_m and game.pause: # mute key
                              if game.pause and sound:
                                    sound = False
                              elif game.pause and not sound:
                                    sound = True
                                    rotate_sfx.play() # ON button sound
                              sound = game.mute_sound(sound)
                        elif not game.game_over and not game.pause: # game screen
                              if event.key == pygame.K_UP:
                                    game.rotate()
                              elif event.key == pygame.K_RIGHT:
                                    game.move_horizontal(1)
                              elif event.key == pygame.K_LEFT:
                                    game.move_horizontal(-1)
                              elif event.key == pygame.K_DOWN:
                                    press_down = True
                              elif event.key == pygame.K_SPACE:
                                    game.place_block()
                  elif event.type == pygame.KEYUP: # releasing key
                        if event.key == pygame.K_DOWN:
                              press_down = False
                  elif event.type == pygame.QUIT: # X window button
                        pygame.quit()
                        run = False
                        sys.exit()

            # Block visualization
            main_screen.fill(BLACK)
            if game.block is not None:
                  for y in range(4): # drawing currently falling blocks
                        for x in range(4):
                              if y * 4 + x in game.block.get_block():
                                    pygame.draw.rect(main_screen, colors[game.block.color_index], \
                                          pygame.Rect(x_pos + box_scale * (x + game.block.x) + 1, y_pos + box_scale * (y + game.block.y) + 1, box_scale - 1, box_scale - 1)) # fills grids

            for y in range(GAME_HEIGTH):
                  pygame.draw.rect(main_screen, GRAY, pygame.Rect(x_pos - box_scale + 1, y_pos + y * box_scale + 1, box_scale - 1, box_scale - 1)) # left frame
                  pygame.draw.rect(main_screen, GRAY, pygame.Rect(x_pos + GAME_WIDTH * box_scale + 1, y_pos + y * box_scale + 1, box_scale - 1, box_scale - 1)) # right frame
                  for x in range(GAME_WIDTH):
                        pygame.draw.rect(main_screen, BLACK, pygame.Rect(x_pos + box_scale * x + 1, y_pos - box_scale * 2+ 1, box_scale - 1, 2 * box_scale - 1)) # top frame
                        # pygame.draw.rect(main_screen, D_GRAY, pygame.Rect(x_pos + x * box_scale, y_pos + y * box_scale, box_scale + 1, box_scale + 1), 1) # drawing gridlines
                        if game.grid_bg[y][x] > -1: # drawing fixed blocks
                              pygame.draw.rect(main_screen, colors[game.grid_bg[y][x]], \
                                    pygame.Rect(x_pos + x * box_scale + 1, y_pos + y * box_scale + 1, box_scale - 1, box_scale - 1))

            # UI Elements
            # Statistics
            stat_box = box_scale * 0.8
            y_distance = 0
            main_screen.blit(text_stat, [50, 100 + box_scale])
            for n in range(7): # each block
                  for y in range(4):
                        for x in range(4):
                              if y * 4 + x in blocks[n][0]:
                                    pygame.draw.rect(main_screen, colors[n], \
                                          pygame.Rect(55 + x * stat_box, 150 + y * stat_box + y_distance, stat_box - 1, stat_box - 1))
                  text_blocks[n] = font.render(str("{:03}".format(game.statistic[n])), False, WHITE)    # block statictics in 000 format
                  main_screen.blit(text_blocks[n], [155, 112.5 + y * stat_box + y_distance])
                  y_distance += stat_box * 3

            # Completed lines
            text_line_counter = font.render(str("{:03}").format(game.lines_cleared), False, WHITE)
            main_screen.blit(text_lines, [x_pos + box_scale * 2, y_pos - box_scale * 2])
            main_screen.blit(text_line_counter, [x_pos + box_scale * 6, y_pos - box_scale * 2])

            # Score texts
            text_score_counter = font.render(str("{:06}").format(game.score), False, WHITE)
            main_screen.blit(text_score, [x_pos + (GAME_WIDTH + 2.5) * box_scale, y_pos + box_scale])
            main_screen.blit(text_score_counter, [x_pos + (GAME_WIDTH + 2.5) * box_scale, y_pos + box_scale * 2])

            # Next shape
            main_screen.blit(text_next, [x_pos + (GAME_WIDTH + 2.5) * box_scale, y_pos + box_scale * 4])
            for y in range(4):
                  for x in range(4):
                        if y * 4 + x in game.next_block.get_block():
                              pygame.draw.rect(main_screen, colors[game.next_block.color_index], \
                                    pygame.Rect(x_pos + (GAME_WIDTH + 2.5 + x) * box_scale + 1, y_pos + box_scale * (6 + y), box_scale - 1, box_scale - 1))

            # Menu
            text_on = font.render("ON", False, game.on_color)
            text_off = font.render("OFF", False, game.off_color)
            if game.pause:
                  pygame.draw.rect(main_screen, D_GRAY, pygame.Rect(WIN_WIDTH//2 - box_scale * 6 + 1, WIN_HEIGTH//2 - box_scale * 5, box_scale * 12 - 1, box_scale * 10))
                  pygame.draw.rect(main_screen, WHITE, pygame.Rect(WIN_WIDTH//2 - box_scale * 6 + 1, WIN_HEIGTH//2 - box_scale * 5, box_scale * 12 - 1, box_scale * 10), 3)
                  main_screen.blit(text_pause, [WIN_WIDTH//2 - 75, y_pos + box_scale * 4])
                  main_screen.blit(text_p, [265, WIN_HEIGTH//2 - 50])
                  main_screen.blit(text_r, [265, WIN_HEIGTH//2 - 20])
                  main_screen.blit(text_esc, [265, WIN_HEIGTH//2 + 10])
                  main_screen.blit(text_sound, [265, WIN_HEIGTH//2 + 50])
                  main_screen.blit(text_on, [350, WIN_HEIGTH//2 + 80])
                  main_screen.blit(text_off, [400, WIN_HEIGTH//2 + 80])

            # Game over
            if game.game_over:
                  pygame.draw.rect(main_screen, D_GRAY, pygame.Rect(WIN_WIDTH//2 - box_scale * 6 + 1, WIN_HEIGTH//2 - box_scale * 4, box_scale * 12 - 1, box_scale * 6))
                  pygame.draw.rect(main_screen, WHITE, pygame.Rect(WIN_WIDTH//2 - box_scale * 6 + 1, WIN_HEIGTH//2 - box_scale * 4, box_scale * 12 - 1, box_scale * 6), 3)
                  main_screen.blit(text_gameover, [WIN_WIDTH//2 - 137.5, y_pos + box_scale * 5])
                  main_screen.blit(text_r, [265, WIN_HEIGTH//2 - 25])
                  main_screen.blit(text_esc, [265, WIN_HEIGTH//2 + 5])

            pygame.display.update()
            clock.tick(FPS)

if __name__ == "__main__": # for import
    main()