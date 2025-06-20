import pygame
import sys
import os
import random

pygame.init()
pygame.mixer.init()


WIDTH, HEIGHT = 1340, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Забытый ключ")
clock = pygame.time.Clock()


WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 150, 255)


BASE_DIR = os.path.dirname(__file__)
IMAGE_DIR = os.path.join(BASE_DIR, "images")
SOUND_DIR = os.path.join(BASE_DIR, "sounds")


floor_tex = pygame.image.load(os.path.join(IMAGE_DIR, "floor.png")).convert()
wall_tex = pygame.image.load(os.path.join(IMAGE_DIR, "wall.png")).convert()
wall_tex2 = pygame.image.load(os.path.join(IMAGE_DIR, "wall2.png")).convert()
door_tex = pygame.image.load(os.path.join(IMAGE_DIR, "door.png")).convert_alpha()
door_tex2 = pygame.image.load(os.path.join(IMAGE_DIR, "door2.png")).convert_alpha()
door_tex3 = pygame.image.load(os.path.join(IMAGE_DIR, "door3.png")).convert_alpha()
player_img = pygame.image.load(os.path.join(IMAGE_DIR, "player.png")).convert_alpha()
key_img = pygame.image.load(os.path.join(IMAGE_DIR, "key.png")).convert_alpha()
cross_img = pygame.image.load(os.path.join(IMAGE_DIR, "cross.png")).convert_alpha()
money_img = pygame.image.load(os.path.join(IMAGE_DIR, "money.png")).convert_alpha()  


sofa_img = pygame.image.load(os.path.join(IMAGE_DIR, "sofa.png")).convert_alpha()
table_img = pygame.image.load(os.path.join(IMAGE_DIR, "table.png")).convert_alpha()
wardrobe_img = pygame.image.load(os.path.join(IMAGE_DIR, "wardrobe.png")).convert_alpha()
dresser_img = pygame.image.load(os.path.join(IMAGE_DIR, "dresser.png")).convert_alpha()
fridge_img = pygame.image.load(os.path.join(IMAGE_DIR, "fridge.png")).convert_alpha()
plant_img = pygame.image.load(os.path.join(IMAGE_DIR, "plant.png")).convert_alpha()
carpet_img = pygame.image.load(os.path.join(IMAGE_DIR, "carpet.png")).convert()


title_font = pygame.font.SysFont("Arial", 72)
subtitle_font = pygame.font.SysFont("Arial", 36)
menu_font = pygame.font.SysFont("Arial", 48)


try:
    background_music = os.path.join(SOUND_DIR, "background_music.mp3")
    key_found_sound = os.path.join(SOUND_DIR, "key_found_sound.wav")
    win_sound_path = os.path.join(SOUND_DIR, "win_sound.mp3") 
    pygame.mixer.music.load(background_music)
    pygame.mixer.music.play(-1)
    key_sound = pygame.mixer.Sound(key_found_sound)
    win_sound = pygame.mixer.Sound(win_sound_path)
    sound_ready = True
except Exception as e:
    print(f"Ошибка загрузки звука: {e}")
    sound_ready = False
    win_sound = None


ROOM_X, ROOM_Y = 100, 100
ROOM_W, ROOM_H = 1100, 600
WALL_THICKNESS = 10
DOOR_HEIGHT = 120
DOOR_WIDTH = WALL_THICKNESS
door_top = ROOM_Y + ROOM_H // 2 - DOOR_HEIGHT // 2
door_rect = pygame.Rect(ROOM_X + ROOM_W - WALL_THICKNESS, door_top, DOOR_WIDTH, DOOR_HEIGHT)


ROOM4_X, ROOM4_Y = 100, 100
ROOM4_W, ROOM4_H = 1100, 600
room4_walls = []
room4_doors = []


door_count = 4
space_between = (ROOM4_H - door_count * DOOR_HEIGHT) // (door_count + 1)
for i in range(door_count):
    door_y = ROOM4_Y + space_between * (i + 1) + DOOR_HEIGHT * i
    door_rect_new = pygame.Rect(ROOM4_X + ROOM4_W - WALL_THICKNESS, door_y, DOOR_WIDTH, DOOR_HEIGHT)
    room4_doors.append(door_rect_new)


for x in range(ROOM4_X, ROOM4_X + ROOM4_W, 64):
    room4_walls.append(pygame.Rect(x, ROOM4_Y, 64, WALL_THICKNESS))
    room4_walls.append(pygame.Rect(x, ROOM4_Y + ROOM4_H - WALL_THICKNESS, 64, WALL_THICKNESS))
for y in range(ROOM4_Y, ROOM4_Y + ROOM4_H, 64):
    room4_walls.append(pygame.Rect(ROOM4_X, y, WALL_THICKNESS, 64))
    room4_walls.append(pygame.Rect(ROOM4_X + ROOM4_W - WALL_THICKNESS, y, WALL_THICKNESS, 64))


class Button:
    def __init__(self, text, x, y, w, h, action=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = GRAY
        self.hover_color = (100, 100, 100)
        self.action = action

    def draw(self, surface):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        color = self.hover_color if self.rect.collidepoint(mouse) else self.color
        pygame.draw.rect(surface, color, self.rect)
        text_surf = menu_font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        if self.rect.collidepoint(mouse) and click[0]:
            return self.action
        return None


PLAYER_SPEED = 5
player_size = (60, 100)
player_x = ROOM_X + 200
player_y = ROOM_Y + 300
player_rect = pygame.Rect(player_x, player_y, player_size[0], player_size[1])


key_found = False
possible_hide_spots = ["Шкаф", "Комод", "Холодильник", "Цветок"]
key_hidden_in = random.choice(possible_hide_spots)
show_hint = False
hint_type = None
hint_timer = 0


key2_found = False
possible_hide_spots_room2 = ["Шкаф", "Комод", "Холодильник", "Цветок"]
key2_hidden_in = random.choice(possible_hide_spots_room2)


sofa_rect = None
table_rect = None
wardrobe_rect = None
fridge_rect = None
plant_rect = None
dresser_rect = None
carpet_rect = None


sofa_rect2 = None
table_rect2 = None
wardrobe_rect2 = None
fridge_rect2 = None
plant_rect2 = None
dresser_rect2 = None
carpet_rect2 = None

CELL_SIZE = 64
maze_data = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1],
    [1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 2],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 2],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]
ROWS = len(maze_data)
COLS = len(maze_data[0])
maze_walls = []
exit_door_rect = None
for row_idx, row in enumerate(maze_data):
    for col_idx, cell in enumerate(row):
        x = col_idx * CELL_SIZE
        y = row_idx * CELL_SIZE
        if cell == 1:
            maze_walls.append(pygame.Rect(x, y, CELL_SIZE, CELL_SIZE))
        elif cell == 2:
            exit_door_rect = pygame.Rect(1280, 630, 64, 64)
if exit_door_rect is None:
    exit_door_rect = pygame.Rect(1280, 630, 64, 64)


free_cells = []
for row_idx in range(ROWS):
    for col_idx in range(COLS):
        if maze_data[row_idx][col_idx] == 0:
            x = col_idx * CELL_SIZE
            y = row_idx * CELL_SIZE
            free_cells.append((x, y))


key_in_room3_found = False
key3_rect = None
if free_cells:
    key3_x, key3_y = random.choice(free_cells)
    key3_rect = pygame.Rect(key3_x + 10, key3_y + 10, CELL_SIZE - 20, CELL_SIZE - 20)
else:
    key3_rect = pygame.Rect(WIDTH - 200, HEIGHT // 2, 30, 30)


key4_found = False
key4_rect = None
correct_door_index = None  


GAME_MENU = "menu"
GAME_RUNNING = "running"
GAME_PAUSED = "paused"
game_state = GAME_MENU


def draw_room():
    for x in range(ROOM_X + WALL_THICKNESS, ROOM_X + ROOM_W - WALL_THICKNESS, 64):
        for y in range(ROOM_Y + WALL_THICKNESS, ROOM_Y + ROOM_H - WALL_THICKNESS, 64):
            screen.blit(floor_tex, (x, y))
    for x in range(ROOM_X, ROOM_X + ROOM_W, 64):
        screen.blit(wall_tex, (x, ROOM_Y))
        screen.blit(wall_tex, (x, ROOM_Y + ROOM_H - WALL_THICKNESS))
    for y in range(ROOM_Y, ROOM_Y + ROOM_H, 64):
        screen.blit(wall_tex, (ROOM_X, y))
    for y in range(ROOM_Y, door_top, 64):
        screen.blit(wall_tex, (ROOM_X + ROOM_W - WALL_THICKNESS, y))
    for y in range(door_top + DOOR_HEIGHT, ROOM_Y + ROOM_H, 64):
        screen.blit(wall_tex, (ROOM_X + ROOM_W - WALL_THICKNESS, y))
    screen.blit(wall_tex, (ROOM_X + ROOM_W - WALL_THICKNESS, ROOM_Y + ROOM_H - WALL_THICKNESS))
    screen.blit(door_tex, door_rect.topleft)

def draw_furniture():
    global sofa_rect, table_rect, wardrobe_rect, fridge_rect, plant_rect, dresser_rect, carpet_rect
    offset_x = -60

    sofa_size = (int(400), int(165))
    sofa_x = ROOM_X + ROOM_W // 2 - sofa_size[0] // 2 + offset_x
    sofa_y = ROOM_Y + 40
    scaled_sofa = pygame.transform.scale(sofa_img, sofa_size)
    screen.blit(scaled_sofa, (sofa_x, sofa_y))
    sofa_mask = pygame.mask.from_surface(scaled_sofa)
    if len(sofa_mask.get_bounding_rects()) > 0:
        sofa_rect = sofa_mask.get_bounding_rects()[0].move(sofa_x, sofa_y)
    else:
        sofa_rect = None

    carpet_size = (300, 150)
    carpet_x = sofa_x + (sofa_size[0] - carpet_size[0]) // 2
    carpet_y = sofa_y + sofa_size[1] + 10
    scaled_carpet = pygame.transform.scale(carpet_img, carpet_size)
    screen.blit(scaled_carpet, (carpet_x, carpet_y))
    carpet_mask = pygame.mask.from_surface(scaled_carpet)
    if len(carpet_mask.get_bounding_rects()) > 0:
        carpet_rect = carpet_mask.get_bounding_rects()[0].move(carpet_x, carpet_y)
    else:
        carpet_rect = None

    table_size = (int(264), int(148))
    table_x = ROOM_X + ROOM_W - table_size[0] - 50 + offset_x
    table_y = ROOM_Y + ROOM_H // 2 - table_size[1] // 2 + 180
    scaled_table = pygame.transform.scale(table_img, table_size)
    screen.blit(scaled_table, (table_x, table_y))
    table_mask = pygame.mask.from_surface(scaled_table)
    if len(table_mask.get_bounding_rects()) > 0:
        table_rect = table_mask.get_bounding_rects()[0].move(table_x, table_y)
    else:
        table_rect = None

    fridge_size = (int(102), int(237))
    fridge_x = ROOM_X + ROOM_W - fridge_size[0] - 20
    fridge_y = ROOM_Y + 20
    scaled_fridge = pygame.transform.scale(fridge_img, fridge_size)
    screen.blit(scaled_fridge, (fridge_x, fridge_y))
    fridge_mask = pygame.mask.from_surface(scaled_fridge)
    if len(fridge_mask.get_bounding_rects()) > 0:
        fridge_rect = fridge_mask.get_bounding_rects()[0].move(fridge_x, fridge_y)
    else:
        fridge_rect = None

    plant_size = (int(75), int(95))
    plant_x = sofa_x + sofa_size[0] - 20
    plant_y = sofa_y + sofa_size[1] - plant_size[1]
    scaled_plant = pygame.transform.scale(plant_img, plant_size)
    screen.blit(scaled_plant, (plant_x, plant_y))
    plant_mask = pygame.mask.from_surface(scaled_plant)
    if len(plant_mask.get_bounding_rects()) > 0:
        plant_rect = plant_mask.get_bounding_rects()[0].move(plant_x, plant_y)
    else:
        plant_rect = None

    wardrobe_size = (int(166), int(237))
    wardrobe_x = ROOM_X + 100
    wardrobe_y = ROOM_Y + 20
    scaled_wardrobe = pygame.transform.scale(wardrobe_img, wardrobe_size)
    screen.blit(scaled_wardrobe, (wardrobe_x, wardrobe_y))
    wardrobe_mask = pygame.mask.from_surface(scaled_wardrobe)
    if len(wardrobe_mask.get_bounding_rects()) > 0:
        wardrobe_rect = wardrobe_mask.get_bounding_rects()[0].move(wardrobe_x, wardrobe_y)
    else:
        wardrobe_rect = None

    dresser_size = (int(188), int(105))
    dresser_x = sofa_x + sofa_size[0] // 2 - dresser_size[0] // 2
    dresser_y = sofa_y + sofa_size[1] + 200
    scaled_dresser = pygame.transform.scale(dresser_img, dresser_size)
    screen.blit(scaled_dresser, (dresser_x, dresser_y))
    dresser_mask = pygame.mask.from_surface(scaled_dresser)
    if len(dresser_mask.get_bounding_rects()) > 0:
        dresser_rect = dresser_mask.get_bounding_rects()[0].move(dresser_x, dresser_y)
    else:
        dresser_rect = None

def draw_furniture_room2():
    global sofa_rect2, table_rect2, wardrobe_rect2, fridge_rect2, plant_rect2, dresser_rect2, carpet_rect2
    offset_x = -60

    sofa_size2 = (int(400), int(165))
    sofa_x2 = ROOM_X + ROOM_W // 2 - sofa_size2[0] // 2 + offset_x
    sofa_y2 = ROOM_Y + 40
    scaled_sofa2 = pygame.transform.scale(sofa_img, sofa_size2)
    screen.blit(scaled_sofa2, (sofa_x2, sofa_y2))
    sofa_mask2 = pygame.mask.from_surface(scaled_sofa2)
    if len(sofa_mask2.get_bounding_rects()) > 0:
        sofa_rect2 = sofa_mask2.get_bounding_rects()[0].move(sofa_x2, sofa_y2)
    else:
        sofa_rect2 = None

    carpet_size2 = (300, 150)
    carpet_x2 = sofa_x2 + (sofa_size2[0] - carpet_size2[0]) // 2
    carpet_y2 = sofa_y2 + sofa_size2[1] + 10
    scaled_carpet2 = pygame.transform.scale(carpet_img, carpet_size2)
    screen.blit(scaled_carpet2, (carpet_x2, carpet_y2))
    carpet_mask2 = pygame.mask.from_surface(scaled_carpet2)
    if len(carpet_mask2.get_bounding_rects()) > 0:
        carpet_rect2 = carpet_mask2.get_bounding_rects()[0].move(carpet_x2, carpet_y2)
    else:
        carpet_rect2 = None

    table_size2 = (int(264), int(148))
    table_x2 = ROOM_X + ROOM_W - table_size2[0] - 50 + offset_x
    table_y2 = ROOM_Y + ROOM_H // 2 - table_size2[1] // 2 + 180
    scaled_table2 = pygame.transform.scale(table_img, table_size2)
    screen.blit(scaled_table2, (table_x2, table_y2))
    table_mask2 = pygame.mask.from_surface(scaled_table2)
    if len(table_mask2.get_bounding_rects()) > 0:
        table_rect2 = table_mask2.get_bounding_rects()[0].move(table_x2, table_y2)
    else:
        table_rect2 = None

    fridge_size2 = (int(102), int(237))
    fridge_x2 = ROOM_X + ROOM_W - fridge_size2[0] - 20
    fridge_y2 = ROOM_Y + 20
    scaled_fridge2 = pygame.transform.scale(fridge_img, fridge_size2)
    screen.blit(scaled_fridge2, (fridge_x2, fridge_y2))
    fridge_mask2 = pygame.mask.from_surface(scaled_fridge2)
    if len(fridge_mask2.get_bounding_rects()) > 0:
        fridge_rect2 = fridge_mask2.get_bounding_rects()[0].move(fridge_x2, fridge_y2)
    else:
        fridge_rect2 = None

    plant_size2 = (int(75), int(95))
    plant_x2 = sofa_x2 + sofa_size2[0] - 20
    plant_y2 = sofa_y2 + sofa_size2[1] - plant_size2[1]
    scaled_plant2 = pygame.transform.scale(plant_img, plant_size2)
    screen.blit(scaled_plant2, (plant_x2, plant_y2))
    plant_mask2 = pygame.mask.from_surface(scaled_plant2)
    if len(plant_mask2.get_bounding_rects()) > 0:
        plant_rect2 = plant_mask2.get_bounding_rects()[0].move(plant_x2, plant_y2)
    else:
        plant_rect2 = None

    wardrobe_size2 = (int(166), int(237))
    wardrobe_x2 = ROOM_X + 100
    wardrobe_y2 = ROOM_Y + 20
    scaled_wardrobe2 = pygame.transform.scale(wardrobe_img, wardrobe_size2)
    screen.blit(scaled_wardrobe2, (wardrobe_x2, wardrobe_y2))
    wardrobe_mask2 = pygame.mask.from_surface(scaled_wardrobe2)
    if len(wardrobe_mask2.get_bounding_rects()) > 0:
        wardrobe_rect2 = wardrobe_mask2.get_bounding_rects()[0].move(wardrobe_x2, wardrobe_y2)
    else:
        wardrobe_rect2 = None

    dresser_size2 = (int(188), int(105))
    dresser_x2 = sofa_x2 + sofa_size2[0] // 2 - dresser_size2[0] // 2
    dresser_y2 = sofa_y2 + sofa_size2[1] + 200
    scaled_dresser2 = pygame.transform.scale(dresser_img, dresser_size2)
    screen.blit(scaled_dresser2, (dresser_x2, dresser_y2))
    dresser_mask2 = pygame.mask.from_surface(scaled_dresser2)
    if len(dressers_mask := dresser_mask2.get_bounding_rects()):
        dresser_rect2 = dressers_mask[0].move(dresser_x2, dresser_y2)
    else:
        dresser_rect2 = None

def draw_room3():
    for x in range(0, WIDTH, 64):
        for y in range(0, HEIGHT, 64):
            screen.blit(floor_tex, (x, y))
    for wall in maze_walls:
        if wall.width > wall.height:
            for x in range(wall.left, wall.right, 64):
                screen.blit(wall_tex2, (x, wall.top))
        else:
            for y in range(wall.top, wall.bottom, 64):
                screen.blit(wall_tex2, (wall.left, y))
    if exit_door_rect:
        screen.blit(door_tex2, exit_door_rect.topleft)
    if key3_rect and not key_in_room3_found:
        screen.blit(key_img, key3_rect)

def draw_room4():
    for x in range(ROOM4_X + WALL_THICKNESS, ROOM4_X + ROOM4_W - WALL_THICKNESS, 64):
        for y in range(ROOM4_Y + WALL_THICKNESS, ROOM4_Y + ROOM4_H - WALL_THICKNESS, 64):
            screen.blit(floor_tex, (x, y))
    for wall in room4_walls:
        screen.blit(wall_tex, wall)
    for door_rect in room4_doors:
        screen.blit(door_tex3, door_rect.topleft)
    if key4_rect and not key4_found:
        screen.blit(key_img, key4_rect)

def draw_room5():
    for x in range(0, WIDTH, 64):
        for y in range(0, HEIGHT, 64):
            screen.blit(floor_tex, (x, y))

    for wall in room4_walls:
        screen.blit(wall_tex, wall)

    font = pygame.font.SysFont("Arial", 70)
    text = font.render("Вы выиграли!", True, (255, 215, 0))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 150)) 

    money_size = (170, 170)
    scaled_money = pygame.transform.scale(money_img, money_size)
    money_x = WIDTH // 2 - money_size[0] // 2
    money_y = HEIGHT // 2 - money_size[1] // 2
    screen.blit(scaled_money, (money_x, money_y))

def move_player(keys):
    global player_rect
    dx, dy = 0, 0
    if keys[pygame.K_w]:
        dy -= PLAYER_SPEED
    if keys[pygame.K_s]:
        dy += PLAYER_SPEED
    if keys[pygame.K_a]:
        dx -= PLAYER_SPEED
    if keys[pygame.K_d]:
        dx += PLAYER_SPEED
    new_rect = player_rect.move(dx, dy)
    if current_room == "room1":
        room_rect = pygame.Rect(ROOM_X + WALL_THICKNESS, ROOM_Y + WALL_THICKNESS,
                                ROOM_W - WALL_THICKNESS * 2, ROOM_H - WALL_THICKNESS * 2)
        left_wall_rect = pygame.Rect(ROOM_X, ROOM_Y, WALL_THICKNESS, ROOM_H)
        colliders = [sofa_rect, table_rect, fridge_rect, plant_rect, wardrobe_rect, dresser_rect, left_wall_rect]
        if not room_rect.contains(new_rect):
            return
        for collider in colliders:
            if collider and new_rect.colliderect(collider):
                return
        if door_rect and new_rect.colliderect(door_rect.inflate(20, 20)):
            return
    elif current_room == "room2":
        room_rect = pygame.Rect(ROOM_X + WALL_THICKNESS, ROOM_Y + WALL_THICKNESS,
                                ROOM_W - WALL_THICKNESS * 2, ROOM_H - WALL_THICKNESS * 2)
        left_wall_rect = pygame.Rect(ROOM_X, ROOM_Y, WALL_THICKNESS, ROOM_H)
        colliders = [sofa_rect2, table_rect2, fridge_rect2, plant_rect2, wardrobe_rect2, dresser_rect2, left_wall_rect]
        if not room_rect.contains(new_rect):
            return
        for collider in colliders:
            if collider and new_rect.colliderect(collider):
                return
        second_door_x = ROOM_X + ROOM_W - WALL_THICKNESS
        second_door_y = door_top
        door_rect2 = pygame.Rect(second_door_x, second_door_y, DOOR_WIDTH, DOOR_HEIGHT)
        if new_rect.colliderect(door_rect2.inflate(20, 20)):
            return
    elif current_room == "room3":
        if not screen.get_rect().contains(new_rect):
            return
        for wall in maze_walls:
            if new_rect.colliderect(wall):
                return
        if exit_door_rect and new_rect.colliderect(exit_door_rect.inflate(20, 20)):
            return
    elif current_room == "room4":
        if not screen.get_rect().contains(new_rect):
            return
        for wall in room4_walls:
            if new_rect.colliderect(wall):
                return
        for door in room4_doors:
            if new_rect.colliderect(door) and not door.contains(new_rect):
                return
    elif current_room == "room5":
        if not screen.get_rect().contains(new_rect):
            return
        for wall in room4_walls:
            if new_rect.colliderect(wall):
                return
    player_rect = new_rect


main_menu_buttons = [
    Button("Начать игру", WIDTH // 2 - 150, HEIGHT // 2 - 100, 300, 60, "start"),
    Button("Выйти", WIDTH // 2 - 150, HEIGHT // 2, 300, 60, "quit")
]

pause_menu_buttons = [
    Button("Продолжить", WIDTH // 2 - 150, HEIGHT // 2 - 100, 300, 60, "resume"),
    Button("Начать заново", WIDTH // 2 - 150, HEIGHT // 2, 300, 60, "restart"),
    Button("В главное меню", WIDTH // 2 - 150, HEIGHT // 2 + 100, 300, 60, "menu")
]


running = True
current_room = "room1"
key1_sound_played = False
key2_sound_played = False
won_game = False


while running:
    keys = pygame.key.get_pressed()
    move_player(keys)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == GAME_RUNNING:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game_state = GAME_PAUSED

            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                if current_room == "room1":
                    nearby_objs = {
                        'Холодильник': fridge_rect,
                        'Шкаф': wardrobe_rect,
                        'Цветок': plant_rect,
                        'Комод': dresser_rect,
                    }
                    interacted = False
                    for name, rect in nearby_objs.items():
                        if rect and player_rect.colliderect(rect.inflate(40, 40)):
                            if name == key_hidden_in:
                                show_hint = True
                                hint_type = "found"
                                hint_timer = 60
                                key_found = True
                                if sound_ready and not key1_sound_played:
                                    key_sound.play()
                                    key1_sound_played = True
                            else:
                                show_hint = True
                                hint_type = "not_found"
                                hint_timer = 60
                            interacted = True
                            break
                    if door_rect and player_rect.colliderect(door_rect.inflate(40, 40)):
                        if key_found:
                            current_room = "room2"
                            player_rect.topleft = (300, 400)
                            key_found = False
                            show_hint = True
                            hint_type = "door_open"
                            hint_timer = 60
                            key1_sound_played = False
                        else:
                            show_hint = True
                            hint_type = "door_no_key"
                            hint_timer = 60
                            interacted = True
                    if not interacted:
                        pass
                elif current_room == "room2":
                    nearby_objs_room2 = {
                        'Холодильник': fridge_rect2,
                        'Шкаф': wardrobe_rect2,
                        'Цветок': plant_rect2,
                        'Комод': dresser_rect2,
                    }
                    interacted = False
                    for name, rect in nearby_objs_room2.items():
                        if rect and player_rect.colliderect(rect.inflate(40, 40)):
                            if name == key2_hidden_in:
                                show_hint = True
                                hint_type = "found"
                                hint_timer = 60
                                key2_found = True
                                if sound_ready and not key2_sound_played:
                                    key_sound.play()
                                    key2_sound_played = True
                            else:
                                show_hint = True
                                hint_type = "not_found"
                                hint_timer = 60
                            interacted = True
                            break
                    second_door_x = ROOM_X + ROOM_W - WALL_THICKNESS
                    second_door_y = door_top
                    door_rect2 = pygame.Rect(second_door_x, second_door_y, DOOR_WIDTH, DOOR_HEIGHT)
                    if player_rect.colliderect(door_rect2.inflate(40, 40)):
                        if key2_found:
                            current_room = "room3"
                            player_rect.topleft = (70, 70)
                            key2_found = False
                            show_hint = True
                            hint_type = "door_open"
                            hint_timer = 60
                        else:
                            show_hint = True
                            hint_type = "door_no_key"
                            hint_timer = 60
                            interacted = True
                    if not interacted:
                        pass
                elif current_room == "room3":
                    if key3_rect and player_rect.colliderect(key3_rect.inflate(20, 20)):
                        key_in_room3_found = True
                        show_hint = True
                        hint_type = "found"
                        hint_timer = 60
                        if sound_ready:
                            key_sound.play()
                    if exit_door_rect and player_rect.colliderect(exit_door_rect.inflate(40, 40)):
                        if key_in_room3_found:
                            current_room = "room4"
                            player_rect.topleft = (ROOM4_X + 120, ROOM4_Y + ROOM4_H // 2 - player_size[1] // 2)
                            key_in_room3_found = False
                            key_found = False
                            key2_found = False
                            key4_rect = pygame.Rect(ROOM4_X + ROOM4_W // 2 - 15, ROOM4_Y + ROOM4_H // 2 - 15, 30, 30)
                            key4_found = False
                            correct_door_index = random.randint(0, 3)
                            show_hint = True
                            hint_type = "door_open"
                            hint_timer = 60
                        else:
                            show_hint = True
                            hint_type = "door_no_key"
                            hint_timer = 60
                elif current_room == "room4":
                    if key4_rect and not key4_found and player_rect.colliderect(key4_rect.inflate(20, 20)):
                        key4_found = True
                        show_hint = True
                        hint_type = "found"
                        hint_timer = 60
                        if sound_ready:
                            key_sound.play()
                    for i, door_rect in enumerate(room4_doors):
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                            if player_rect.colliderect(door_rect.inflate(50, 50)): 
                                if key4_found: 
                                    if i == correct_door_index:  
                                        current_room = "room5"
                                        player_rect.topleft = (WIDTH // 2 - 20, HEIGHT - 300)
                                        key4_found = False 
                                        if sound_ready:
                                            win_sound.play()
                                            played_win_sound = True
                                    else:
                                        show_hint = True
                                        hint_type = "not_found"  
                                        hint_timer = 60
                                else:
                                    show_hint = True
                                    hint_type = "door_no_key"
                                    hint_timer = 60
                elif current_room == "room5":
                    if event.key == pygame.K_ESCAPE:
                        running = False

        elif game_state == GAME_PAUSED:
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                for button in pause_menu_buttons:
                    result = button.draw(screen)
                    if result == "resume":
                        game_state = GAME_RUNNING
                    elif result == "restart":
                        current_room = "room1"
                        player_rect.topleft = (300, 400)
                        key_found = False
                        key2_found = False
                        key_in_room3_found = False
                        key4_found = False
                        key1_sound_played = False
                        key2_sound_played = False
                        played_win_sound = False
                        game_state = GAME_RUNNING
                    elif result == "menu":
                        game_state = GAME_MENU

    screen.fill((40, 40, 40))

    if game_state == GAME_MENU:
        screen.fill((0, 0, 0))
        title_text = title_font.render("Потерянный ключ", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 250))
        screen.blit(title_text, title_rect)

        subtitle_text = subtitle_font.render("Найди все ключи и дойди до золота", True, GRAY)
        subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 170))
        screen.blit(subtitle_text, subtitle_rect)

        for button in main_menu_buttons:
            result = button.draw(screen)
            if result == "start":
                game_state = GAME_RUNNING
                current_room = "room1"
                player_rect.topleft = (300, 400)
                key_found = False
                key2_found = False
                key_in_room3_found = False
                key4_found = False
                key1_sound_played = False
                key2_sound_played = False
                played_win_sound = False
            elif result == "quit":
                running = False

    elif game_state == GAME_RUNNING:
        if current_room == "room1":
            draw_room()
            draw_furniture()
        elif current_room == "room2":
            draw_room()
            draw_furniture_room2()
            wall_left_rect = pygame.Rect(0, 0, WALL_THICKNESS, HEIGHT)
            wall_right_rect = pygame.Rect(WIDTH - WALL_THICKNESS, 0, WALL_THICKNESS, HEIGHT)
            screen.blit(wall_tex, wall_left_rect.topleft)
            screen.blit(wall_tex, wall_right_rect.topleft)
            second_door_x = ROOM_X + ROOM_W - WALL_THICKNESS
            second_door_y = door_top
            screen.blit(door_tex, (second_door_x, second_door_y))
        elif current_room == "room3":
            draw_room3()
        elif current_room == "room4":
            draw_room4()
        elif current_room == "room5":
            draw_room5()

    
        if current_room in ("room2", "room3"):
            light_mask = pygame.Surface((WIDTH, HEIGHT))
            light_mask.fill((255, 255, 255))
            light_mask.set_colorkey((255, 255, 255))
            pygame.draw.circle(light_mask, (0, 0, 0), player_rect.center, 150)
            screen.blit(light_mask, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

      
        screen.blit(pygame.transform.scale(player_img, player_size), player_rect.topleft)

    
        if current_room != "room5" and (key_found or key2_found or key_in_room3_found or key4_found):
            screen.blit(pygame.transform.scale(key_img, (40, 40)), (20, 20))

    
        if show_hint and hint_timer > 0:
            hint_x = player_rect.centerx - 50
            hint_y = player_rect.y - 60
            if hint_type == "not_found":
                screen.blit(pygame.transform.scale(cross_img, (40, 40)), (hint_x, hint_y))
            elif hint_type == "found":
                screen.blit(pygame.transform.scale(key_img, (40, 40)), (hint_x, hint_y))
            elif hint_type == "door_no_key":
                screen.blit(pygame.transform.scale(cross_img, (40, 40)), (hint_x, hint_y))
            elif hint_type == "door_open":
                screen.blit(pygame.transform.scale(key_img, (40, 40)), (hint_x, hint_y))
            hint_timer -= 1.5
        else:
            show_hint = False

    elif game_state == GAME_PAUSED:
        screen.fill((0, 0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        for button in pause_menu_buttons:
            button.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()