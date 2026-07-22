import turtle
from collections import deque

# --- 1. 初始化屏幕与游戏变量 ---
screen = turtle.Screen()
screen.setup(480, 520) 
screen.bgcolor("#f0f0f0") 
screen.title("Three Chambers: Power Grid Connection Plus")
screen.tracer(0) 

tile_size = 28
game_over = False

# 【修改：初始血量调整为 30】
player_hp = 30 

freeze_duration = 0
portal_cooldown = False
trap_active = False

room3_light_mode = 0  # 0: 全黑 | 1: 电箱B激活 | 2: 3个蓝电箱S全清
has_key = False
switches_activated = 0
total_switches = 3

# 15x15 的宏大世界地图
# 1 = 墙壁 | 0 = 通路 | 2 = 终极金块 | X = 闪烁陷阱 | O = 冰冻球 | P = 传送门 
# B = 第2房间的总电箱 | K = 钥匙 | D = 带锁的门 | S = 蓝电箱
# T = 地刺陷阱 | G = 电能门
original_map = [
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1"],
    ["1","0","K","0","1","1","0","0","0","D","0","0","0","2","1"], 
    ["1","S","1","0","1","1","0","1","0","1","1","0","1","G","1"], 
    ["1","O","1","0","1","1","O","1","0","1","1","O","1","0","1"], 
    ["1","1","1","0","1","1","1","1","0","1","1","1","1","D","1"], 
    ["1","0","T","0","1","1","S","0","0","0","0","0","0","0","1"], 
    ["1","0","1","1","1","1","0","1","1","1","1","1","1","0","1"], 
    ["1","0","0","0","P","1","0","0","X","1","1","0","T","0","1"], 
    ["1","1","1","0","1","1","1","0","1","1","1","0","1","1","1"], 
    ["1","S","0","0","1","1","K","0","0","1","1","K","0","0","1"], 
    ["1","0","1","1","1","1","1","B","1","1","1","1","1","0","K"], 
    ["1","0","0","0","0","1","1","0","1","1","0","0","0","0","1"], 
    ["1","1","1","1","D","1","1","0","1","1","0","1","1","1","1"], 
    ["1","1","1","1","0","0","0","0","0","0","0","0","0","0","1"], 
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1"]
]

maze_map = [row[:] for row in original_map]
portal1_row, portal1_col = 7, 4
portal2_row, portal2_col = 11, 12

drawer = turtle.Turtle()
drawer.hideturtle()
drawer.speed(0)

text_drawer = turtle.Turtle()
text_drawer.hideturtle()
text_drawer.speed(0)

player_row, player_col = 1, 1
enemy_row, enemy_col = 13, 13

# --- 2. 区域判定算法 ---
def get_current_room(col):
    if col <= 4:
        return 1 
    elif 5 <= col <= 9:
        return 2 
    else:
        return 3 

# --- 3. 坐标转换与核心绘制 ---
def grid_to_screen(col, row):
    screen_x = -210 + (col * tile_size)
    screen_y = 210 - (row * tile_size)
    return screen_x, screen_y

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

def draw_game():
    drawer.clear()
    
    for r in range(15):
        for c in range(15):
            tile_room = get_current_room(c)
            distance = abs(r - player_row) + abs(c - player_col)
            
            if tile_room == 2 and distance > 2:
                draw_square(c, r, "#1a1a1a")
                continue
            
            if tile_room == 3:
                if room3_light_mode == 0:
                    draw_square(c, r, "#1a1a1a") 
                    continue
                elif room3_light_mode == 1 and distance > 2:
                    draw_square(c, r, "#1a1a1a") 
                    continue

            tile = maze_map[r][c]
            if tile == "1": draw_square(c, r, "#34495e")       
            elif tile == "2": draw_square(c, r, "#f1c40f")     
            elif tile == "X":
                if trap_active: draw_square(c, r, "#e67e22")   
                else: draw_square(c, r, "#bdc3c7")
            elif tile == "O": draw_square(c, r, "#5dade2")     
            elif tile == "P": draw_square(c, r, "#9b59b6")     
            elif tile == "B": draw_square(c, r, "#1abc9c")     
            elif tile == "K": draw_square(c, r, "#f39c12")     
            elif tile == "D": draw_square(c, r, "#8e44ad")     
            elif tile == "S": draw_square(c, r, "#3498db")     
            elif tile == "T": draw_square(c, r, "#7f8c8d")     
            elif tile == "G": draw_square(c, r, "#e74c3c")     
            elif tile == "0": draw_square(c, r, "#e5e7e9")     

            if r == enemy_row and c == enemy_col:
                visible = (tile_room != 3) or (room3_light_mode == 2) or (room3_light_mode == 1 and distance <= 2)
                if tile_room == 2 and abs(r - player_row) + abs(c - player_col) > 2:
                    visible = False
                if visible:
                    if freeze_duration > 0: draw_square(enemy_col, enemy_row, "#2980b9")
                    else: draw_square(enemy_col, enemy_row, "#c0392b")
        
    draw_square(player_col, player_row, "#2ecc71") 
    screen.update()

def update_status_text(custom_msg=""):
    text_drawer.clear()
    text_drawer.penup()
    text_drawer.goto(0, 185)
    
    # 显示当前的数值型血量
    hp_text = f"{player_hp}" if player_hp > 0 else "0"
    key_text = "🔑" if has_key else "❌"
    
    if custom_msg:
        status_msg = f"💚 HP: {hp_text}/30 | Key: {key_text} | {custom_msg}"
        text_drawer.color("#e74c3c")
    else:
        current_p_room = get_current_room(player_col)
        text_drawer.color("#333333")
        if current_p_room == 1:
            status_msg = f"💚 HP: {hp_text}/30 | Key: {key_text} | Room 1: Get Key for Door(D)"
        elif current_p_room == 2 and room3_light_mode == 0:
            status_msg = f"💚 HP: {hp_text}/30 | Room 2: Find Master Box (B)"
        elif room3_light_mode == 1:
            status_msg = f"💚 HP: {hp_text}/30 | Room 3 Connected! Clear Blue Boxes (S): {switches_activated}/{total_switches}"
        elif room3_light_mode == 2:
            status_msg = f"💚 HP: {hp_text}/30 | GRID FULLY LIGHT UP! ALL GATES OPENED!"
        else:
            status_msg = f"💚 HP: {hp_text}/30 | WASD to Move"
        
    text_drawer.write(status_msg, align="center", font=("Arial", 10, "bold"))

def can_move_to(row, col, is_player=True):
    global player_hp
    if 0 <= row < 15 and 0 <= col < 15:
        tile = maze_map[row][col]
        if tile == "1": 
            return False
        
        if not is_player:
            if tile in ["K", "B", "S", "2", "P", "G"]:
                return False

        # 【平衡微调：碰 G 电能门扣 10 HP】
        if tile == "G":
            if is_player:
                player_hp -= 10  
                if player_hp <= 0: player_hp = 0
                update_status_text("💥 Hit Electric Gate (G)! -10 HP!")
                return False  
            else:
                return False

        if tile == "D":
            if is_player:
                global has_key
                if has_key:
                    maze_map[row][col] = "0" 
                    has_key = False
                    update_status_text("🔓 Door unlocked successfully!")
                    return True
                else:
                    update_status_text("🔒 Locked! Need Key (K) from Room 1!")
                    return False
            else:
                return False 
                
        return True
    return False

# --- 4. 游戏核心状态判定 ---
def check_game_status():
    global game_over, player_row, player_col, player_hp, freeze_duration, portal_cooldown, room3_light_mode, has_key, switches_activated
    
    tile = maze_map[player_row][player_col]

    if tile == "K":
        has_key = True
        maze_map[player_row][player_col] = "0"
        update_status_text("🔑 Got the Room 1 Key!")

    elif tile == "B":
        if room3_light_mode == 0:
            room3_light_mode = 1 
        maze_map[player_row][player_col] = "0"
        update_status_text("🔋 Master Grid On! Room 3 Fog Vision Active!")

    elif tile == "S":
        switches_activated += 1
        maze_map[player_row][player_col] = "0"
        if switches_activated == total_switches:
            room3_light_mode = 2 
            for r in range(15):
                for c in range(15):
                    if maze_map[r][c] == "G":
                        maze_map[r][c] = "0"
            update_status_text("⚡ ALL POWER CONNECTED! Electric Gates (G) Opened!")
        else:
            update_status_text(f"⚡ Activated Box ({switches_activated}/{total_switches})")

    elif tile == "P":
        if not portal_cooldown:
            if player_row == portal1_row and player_col == portal1_col:
                player_row, player_col = portal2_row, portal2_col
            else:
                player_row, player_col = portal1_row, portal1_col
            portal_cooldown = True 
            return
    else:
        portal_cooldown = False

    # 【平衡微调：踩中地刺 T 扣 5 HP】
    if tile == "T":
        player_hp -= 5
        maze_map[player_row][player_col] = "0" 
        if player_hp <= 0:
            player_hp = 0
            game_over = True
            update_status_text("💀 No HP Left! Game Over! [R]")
            return
        else:
            update_status_text("🩹 Stepped on Spikes (T)! -5 HP!")

    if tile == "O":
        freeze_duration = 4 
        maze_map[player_row][player_col] = "0"
        update_status_text("❄️ Enemy frozen for 4 turns!")
        
    if maze_map[player_row][player_col] == "2":
        game_over = True
        update_status_text("🏆 CHAMPION! Cleared to Next Stage!")
        return
        
    if player_row == enemy_row and player_col == enemy_col:
        game_over = True
        update_status_text("💀 Wasted! Caught by enemy. Press R.")
        return

    # 【平衡微调：踩中地雷 X 扣 15 HP 并遣返】
    if maze_map[player_row][player_col] == "X" and trap_active:
        player_hp -= 15
        if player_hp <= 0:
            player_hp = 0
            game_over = True
            update_status_text("💀 No HP Left! Game Over! [R]")
        else:
            player_row, player_col = 1, 1 
            portal_cooldown = False
            update_status_text("💥 Boom! Trap exploded! -15 HP and Respawned!")
        return

def move_enemy():
    global enemy_row, enemy_col, freeze_duration
    if game_over or freeze_duration > 0:
        if freeze_duration > 0: freeze_duration -= 1
        return
    if enemy_row == player_row and enemy_col == player_col: return

    start = (enemy_row, enemy_col)
    queue = deque([start])
    parent = {start: None}
    found = False
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while queue:
        curr_row, curr_col = queue.popleft()
        if curr_row == player_row and curr_col == player_col:
            found = True
            break
        for dr, dc in directions:
            nr, nc = curr_row + dr, curr_col + dc
            if can_move_to(nr, nc, is_player=False) and (nr, nc) not in parent:
                parent[(nr, nc)] = (curr_row, curr_col)
                queue.append((nr, nc))

    if found:
        curr = (player_row, player_col)
        while parent[curr] != start: 
            curr = parent[curr]
        enemy_row, enemy_col = curr 

# --- 5. 键盘事件与同步回合驱动机制 ---
def execute_game_step(next_row, next_col):
    global player_row, player_col, trap_active
    if game_over: return
    
    if can_move_to(next_row, next_col, is_player=True):
        player_row = next_row
        player_col = next_col
        trap_active = not trap_active 
        
        check_game_status()
        move_enemy() 
        if not game_over:
            check_game_status()
            update_status_text()
            draw_game() 
    else:
        if not game_over:
            update_status_text()
            draw_game()
            
    screen.listen()

def move_up():    execute_game_step(player_row - 1, player_col)
def move_down():  execute_game_step(player_row + 1, player_col)
def move_left():  execute_game_step(player_row, player_col - 1)
def move_right(): execute_game_step(player_row, player_col + 1)

def reset_game():
    global game_over, player_hp, freeze_duration, player_row, player_col, enemy_row, enemy_col, maze_map, trap_active, portal_cooldown, room3_light_mode, has_key, switches_activated
    game_over = False
    player_hp = 30  # 重置时恢复 30 HP
    freeze_duration = 0
    trap_active = False
    portal_cooldown = False
    room3_light_mode = 0 
    has_key = False
    switches_activated = 0
    player_row, player_col = 1, 1
    enemy_row, enemy_col = 13, 13
    maze_map = [row[:] for row in original_map]
    draw_game()
    update_status_text()
    screen.listen()

# --- 6. 注册按键监控 ---
screen.listen()
screen.onkey(move_up, "w")
screen.onkey(move_down, "s")
screen.onkey(move_left, "a")
screen.onkey(move_right, "d")
screen.onkey(reset_game, "r")

draw_game()
update_status_text()
turtle.done()