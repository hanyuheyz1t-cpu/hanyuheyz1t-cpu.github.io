import turtle
from collections import deque
import random

# --- 1. 初始化屏幕与游戏变量 ---
screen = turtle.Screen()
screen.setup(480, 520) 
screen.bgcolor("#111111") # 终关暗黑背景
screen.title("The Final Gate: Hell Mode")
screen.tracer(0) 

tile_size = 28
game_over = False
player_hp = 100       
freeze_duration = 0
portal_cooldown = False
trap_active = True

# 核心机制变量
room3_light_mode = 0    
has_pickaxe = False     
has_key = False         
gate_unlocked = False   
switches_activated = 0  
total_switches = 3      
last_direction = (1, 0) 

# 【终关专属】红块多目标管理（支持分裂）
enemies = [{"row": 13, "col": 13}] 

# 终极硬核 15x15 地图
original_map = [
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1"],
    ["1","0","K","0","0","1","B","0","0","1","1","G","S","T","1"], 
    ["1","0","0","0","0","0","1","1","0","1","1","1","1","1","1"], 
    ["1","F","0","0","0","0","F","1","0","1","1","F","1","0","1"], 
    ["1","0","0","0","0","0","1","1","0","1","1","0","1","0","1"], 
    ["1","M","0","0","0","0","1","0","0","0","0","0","0","0","1"], 
    ["1","D","D","D","D","D","1","1","G","1","1","1","1","0","1"], 
    ["1","0","0","0","0","0","0","0","X","1","1","S","0","T","1"], 
    ["1","0","0","0","0","0","0","0","0","1","1","0","1","1","1"], 
    ["P","0","0","0","0","-0","0","0","0","1","1","W","W","W","1"], 
    ["1","0","0","0","0","1","1","1","0","1","1","0","0","0","1"], 
    ["1","0","0","0","0","1","1","0","0","1","S","T","T","T","1"], 
    ["1","0","0","0","0","1","1","P","0","1","0","T","T","T","T"], 
    ["1","0","0","0","0","0","0","0","0","1","0","T","T","0","2"], 
    ["1","0","0","0","0","1","1","1","1","1","1","1","1","1","0"]
]

maze_map = [row[:] for row in original_map]
portal1_row, portal1_col = 9, 0
portal2_row, portal2_col = 12, 7

drawer = turtle.Turtle()
drawer.hideturtle()
drawer.speed(0)

text_drawer = turtle.Turtle()
text_drawer.hideturtle()
text_drawer.speed(0)

player_row, player_col = 1, 1

# --- 2. 核心判定与随机陷阱刷新 ---
def get_current_room(col):
    if col <= 4: return 1
    elif 5 <= col <= 9: return 2
    else: return 3

def grid_to_screen(col, row):
    return -210 + (col * tile_size), 210 - (row * tile_size)

def draw_square(col, row, color):
    sx, sy = grid_to_screen(col, row)
    drawer.penup()
    drawer.goto(sx, sy)
    drawer.setheading(0) 
    drawer.color(color)
    drawer.begin_fill()
    for _ in range(4):
        drawer.forward(tile_size - 1)
        drawer.right(90)
    drawer.end_fill()

def randomize_hazards():
    """硬核：每次行动动态搅乱地图陷阱"""
    global maze_map
    for r in range(1, 14):
        for c in range(1, 14):
            if original_map[r][c] in ("T", "X") and maze_map[r][c] in ("0", "T", "X"):
                maze_map[r][c] = random.choice(["T", "X", "0"])

def draw_game():
    drawer.clear()
    for r in range(15):
        for c in range(15):
            tile_room = get_current_room(c)
            distance = abs(r - player_row) + abs(c - player_col)
            
            if tile_room == 2 and distance > 2:
                draw_square(c, r, "#111111")
                continue
            if tile_room == 3:
                if room3_light_mode == 0:
                    draw_square(c, r, "#111111")
                    continue
                elif room3_light_mode == 1 and distance > 2:
                    draw_square(c, r, "#111111")
                    continue

            tile = maze_map[r][c]
            if tile == "1": draw_square(c, r, "#2c3e50")       
            elif tile == "2": draw_square(c, r, "#f1c40f")     
            elif tile == "X": draw_square(c, r, "#d35400" if trap_active else "#7f8c8d")   
            elif tile == "F": draw_square(c, r, "#74b9ff")     
            elif tile == "P": draw_square(c, r, "#a29bfe")     
            elif tile == "B": draw_square(c, r, "#00cec9")     
            elif tile == "M": draw_square(c, r, "#ffeaa7")     
            elif tile == "K": draw_square(c, r, "#fdcb6e")     
            elif tile == "D": draw_square(c, r, "#6c5ce7")     
            elif tile == "S": draw_square(c, r, "#0984e3")     
            elif tile == "G": draw_square(c, r, "#00b894" if gate_unlocked else "#ff7675") 
            elif tile == "T": draw_square(c, r, "#e17055")     
            elif tile == "W": draw_square(c, r, "#2d3436")     
            elif tile == "0": draw_square(c, r, "#222222")     

            # 渲染所有存活的红块
            for en in enemies:
                if r == en["row"] and c == en["col"]:
                    visible = (tile_room != 3) or (room3_light_mode == 2) or (room3_light_mode == 1 and distance <= 2)
                    if tile_room == 2 and abs(r - player_row) + abs(c - player_col) > 2:
                        visible = False
                    if visible:
                        draw_square(c, r, "#d63031" if freeze_duration == 0 else "#0984e3")
        
    draw_square(player_col, player_row, "#00b894")
    screen.update()

def update_status_text(custom_msg=""):
    text_drawer.clear()
    text_drawer.penup()
    text_drawer.goto(0, 185)
    hp_text = f"HP: {max(0, player_hp)}/100"
    items = f" ⛏️" if has_pickaxe else ""
    items += f" 🔑" if has_key else ""
    
    if custom_msg:
        status_msg = f"{hp_text}{items} | {custom_msg}"
    else:
        status_msg = f"{hp_text}{items} | ENEMIES: {len(enemies)} | [WASD] Move | [E] Smash | [Q] Knockback & SPLIT!"
        
    text_drawer.color("#ffffff")
    text_drawer.write(status_msg, align="center", font=("Arial", 10, "bold"))

def can_move_to(row, col, is_player=True):
    if 0 <= row < 15 and 0 <= col < 15:
        tile = maze_map[row][col]
        if tile == "1": return False
        if tile == "W": return not is_player 
        if tile == "D":
            if is_player and has_key:
                maze_map[row][col] = "0"
                return True
            return False 
        if tile == "G" and not gate_unlocked:
            if is_player:
                global player_hp, game_over
                player_hp -= 99
                update_status_text("⚡ INSTANT KILL FORCE! Gate Zapped! -99 HP")
                if player_hp <= 0: game_over = True
            return False
        return True
    return False

# --- 3. 游戏事件判定 ---
def check_game_status():
    global game_over, player_row, player_col, player_hp, freeze_duration, portal_cooldown, room3_light_mode, has_pickaxe, has_key, switches_activated, gate_unlocked
    if game_over: return
    
    tile = maze_map[player_row][player_col]

    if tile == "M":
        has_pickaxe = True; maze_map[player_row][player_col] = "0"
    elif tile == "K":
        has_key = True; maze_map[player_row][player_col] = "0"
    elif tile == "B":
        if room3_light_mode == 0: room3_light_mode = 1
        maze_map[player_row][player_col] = "0"
    elif tile == "S":
        switches_activated += 1; maze_map[player_row][player_col] = "0"
        if switches_activated == total_switches:
            room3_light_mode = 2; gate_unlocked = True
            update_status_text("⚡ ENERGY FULL! GATE OPENED!")
    elif tile == "T":
        player_hp -= 25; maze_map[player_row][player_col] = "0"
        update_status_text("🩸 Spiked! -25 HP!")
    elif tile == "P":
        if not portal_cooldown:
            if player_row == portal1_row and player_col == portal1_col:
                player_row, player_col = portal2_row, portal2_col
            else:
                player_row, player_col = portal1_row, portal1_col
            portal_cooldown = True; return
    else: portal_cooldown = False

    if tile == "F":
        freeze_duration = 3; maze_map[player_row][player_col] = "0"
    if tile == "2":
        game_over = True; update_status_text("🏆 GODLIKE! HELL MODE CONQUERED!"); return

    # 检查所有红块伤害
    for en in enemies:
        if player_row == en["row"] and player_col == en["col"]:
            player_hp -= 0.1
            update_status_text("💥 Shredded by Enemy! -0.1+ HP")

    if tile == "X" and trap_active:
        player_hp -= 15
        player_row, player_col = 1, 1
        update_status_text("💥 Mine Exploded! Respawned!")

    if player_hp <= 0:
        game_over = True; update_status_text("💀 WASTED! Hell claimed your soul. [R]")

def move_enemy():
    global freeze_duration, game_over
    if game_over: return
    if freeze_duration > 0:
        freeze_duration -= 1; return

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for en in enemies:
        if en["row"] == player_row and en["col"] == player_col: continue
        start = (en["row"], en["col"])
        queue = deque([start])
        parent = {start: None}
        found = False

        while queue:
            curr_row, curr_col = queue.popleft()
            if curr_row == player_row and curr_col == player_col:
                found = True; break
            for dr, dc in directions:
                nr, nc = curr_row + dr, curr_col + dc
                if can_move_to(nr, nc, is_player=False) and (nr, nc) not in parent:
                    parent[(nr, nc)] = (curr_row, curr_col)
                    queue.append((nr, nc))
        if found:
            curr = (player_row, player_col)
            while parent[curr] != start: curr = parent[curr]
            en["row"], en["col"] = curr[0], curr[1]

# --- 4. 行动交互（带分裂红块的Q击退） ---
def execute_game_step(next_row, next_col, d_row, d_col):
    global player_row, player_col, trap_active, last_direction
    if game_over: return
    last_direction = (d_row, d_col)
    
    if can_move_to(next_row, next_col, is_player=True):
        player_row = next_row
        player_col = next_col
        trap_active = not trap_active
        randomize_hazards()
        check_game_status()
        move_enemy()
        check_game_status()
        if not game_over: draw_game(); update_status_text()
    screen.listen()

def use_pickaxe():
    if game_over or not has_pickaxe: return
    front_row, front_col = player_row + last_direction[0], player_col + last_direction[1]
    if 0 <= front_row < 15 and 0 <= front_col < 15:
        if maze_map[front_row][front_col] in ("1", "W") and not (front_row in (0,14) or front_col in (0,14)):
            maze_map[front_row][front_col] = "0"
            randomize_hazards(); move_enemy(); check_game_status(); draw_game()
    screen.listen()

def place_wall_or_knockback():
    global freeze_duration
    if game_over: return
    front_row, front_col = player_row + last_direction[0], player_col + last_direction[1]

    # 检测前方是否有任何红块
    hit_enemy = None
    for en in enemies:
        if en["row"] == front_row and en["col"] == front_col:
            hit_enemy = en; break

    if hit_enemy:
        # 击退逻辑
        kb_row = hit_enemy["row"] + last_direction[0] * 2
        kb_col = hit_enemy["col"] + last_direction[1] * 2
        if not can_move_to(kb_row, kb_col, is_player=False):
            kb_row = hit_enemy["row"] + last_direction[0]
            kb_col = hit_enemy["col"] + last_direction[1]
        
        # 产生分裂：克隆一个新的红块在原位置
        if len(enemies) < 4: # 最多限制分裂成4个
            enemies.append({"row": hit_enemy["row"], "col": hit_enemy["col"]})
            update_status_text("⚠️ WARNING: Enemy KNOCKED BACK but IT MITOSIS-SPLIT!")
        else:
            update_status_text("🛡️ Shield Slammed!")

        hit_enemy["row"], hit_enemy["col"] = kb_row, kb_col
        freeze_duration = 1 
        check_game_status(); draw_game(); return

    # 放墙逻辑
    if 0 <= front_row < 15 and 0 <= front_col < 15 and maze_map[front_row][front_col] == "0":
        maze_map[front_row][front_col] = "1"
        randomize_hazards(); move_enemy(); check_game_status(); draw_game()
    screen.listen()

def move_up():    execute_game_step(player_row - 1, player_col, -1, 0)
def move_down():  execute_game_step(player_row + 1, player_col, 1, 0)
def move_left():  execute_game_step(player_row, player_col - 1, 0, -1)
def move_right(): execute_game_step(player_row, player_col + 1, 0, 1)

def reset_game():
    global game_over, player_hp, freeze_duration, player_row, player_col, enemies, maze_map, trap_active, portal_cooldown, room3_light_mode, has_pickaxe, has_key, switches_activated, gate_unlocked
    game_over = False; player_hp = 100; freeze_duration = 0; room3_light_mode = 0
    has_pickaxe = False; has_key = False; gate_unlocked = False; switches_activated = 0
    player_row, player_col = 1, 1
    enemies = [{"row": 13, "col": 13}]
    maze_map = [row[:] for row in original_map]
    draw_game(); update_status_text(); screen.listen()

screen.listen()
screen.onkey(move_up, "w"); screen.onkey(move_down, "s")
screen.onkey(move_left, "a"); screen.onkey(move_right, "d")
screen.onkey(use_pickaxe, "e"); screen.onkey(place_wall_or_knockback, "q")
screen.onkey(reset_game, "r")
def check_final_epiphany():
    if game_over and player_hp > 50:
        print("Green Block 不再寻找出口。")
        print("他明白，自己并没有被困在这里。")
        print("他成为了出口的一部分。")
        unlock_ending("Upload")
        background.fade_to("memory_fragments")
        play_music("forgotten_network")
draw_game(); update_status_text(); turtle.done()