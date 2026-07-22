import turtle
from collections import deque

# --- 1. 初始化屏幕与游戏变量 ---
screen = turtle.Screen()
screen.setup(480, 520) 
screen.bgcolor("#f0f0f0") 
screen.title("Three Chambers: Shield Knockback & Code Gate Edition")
screen.tracer(0) 

tile_size = 28
game_over = False
player_hp = 100       
freeze_duration = 0
portal_cooldown = False
trap_active = False

# 联动机制核心变量
room3_light_mode = 0    # 0:全黑 | 1:总电箱激活 | 2:蓝电箱全清(电门开)
has_key = False         
gate_unlocked = False   
switches_activated = 0  
total_switches = 3      
last_direction = (1, 0) # 记录玩家方向

# 密码门与纸张变量
paper_code = "8542"     # 设定的密码
read_paper = False      # 是否读过纸张

# 15x15 宏大世界地图
original_map = [
    ["1","P","1","1","1","1","1","1","1","1","1","1","1","1","1"],
    ["1","0","K","0","1","1","B","T","0","1","1","S","G","2","1"], 
    ["1","0","1","0","1","1","0","1","0","1","1","0","1","1","1"], 
    ["1","F","1","D","1","1","F","1","0","1","1","F","1","0","1"], 
    ["1","1","1","X","1","1","1","1","0","1","1","0","1","0","1"], 
    ["1","0","0","0","1","1","0","0","0","0","0","0","0","0","1"], 
    ["1","0","1","1","1","1","0","0","1","1","1","1","1","0","1"], 
    ["1","I","0","0","K","1","X","X","X","1","1","S","0","T","1"], 
    ["1","1","0","C","1","1","0","0","1","1","1","0","1","1","1"], 
    ["P","0","0","0","1","1","0","0","0","1","1","0","0","0","1"], 
    ["1","T","1","1","1","1","1","0","1","1","1","0","0","0","1"], 
    ["1","0","0","0","0","1","1","0","1","1","S","0","0","0","1"], 
    ["1","1","1","1","T","1","1","P","1","1","0","1","1","1","1"], 
    ["1","1","1","1","0","0","0","0","0","D","0","0","0","0","1"], 
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1"]
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
enemy_row, enemy_col = 13, 13

# --- 2. 区域判定与物理碰撞判定 ---
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
            elif tile == "F": draw_square(c, r, "#5dade2")     
            elif tile == "P": draw_square(c, r, "#9b59b6")     
            elif tile == "B": draw_square(c, r, "#1abc9c")     
            elif tile == "K": draw_square(c, r, "#f39c12")     
            elif tile == "D": draw_square(c, r, "#8e44ad")     
            elif tile == "S": draw_square(c, r, "#3498db")     
            elif tile == "G": draw_square(c, r, "#16a085" if gate_unlocked else "#d35400") 
            elif tile == "T": draw_square(c, r, "#7f8c8d")     
            elif tile == "I": draw_square(c, r, "#fffde7")     
            elif tile == "C": draw_square(c, r, "#d35400")     
            elif tile == "0": draw_square(c, r, "#e5e7e9")     

            if r == enemy_row and c == enemy_col:
                visible = (tile_room != 3) or (room3_light_mode == 2) or (room3_light_mode == 1 and distance <= 2)
                if tile_room == 2 and abs(r - player_row) + abs(c - player_col) > 2:
                    visible = False
                if visible:
                    if freeze_duration > 0: draw_square(enemy_col, enemy_row, "#2980b9")
                    else: draw_square(enemy_col, enemy_row, "#e74c3c")
        
    draw_square(player_col, player_row, "#2ecc71")
    screen.update()

def update_status_text(custom_msg=""):
    text_drawer.clear()
    text_drawer.penup()
    text_drawer.goto(0, 185)
    hp_text = f"HP: {max(0, player_hp)}/100"
    items_status = ""
    if has_key: items_status += " 🔑"
    if read_paper: items_status += f" 📜({paper_code})" 
    
    if custom_msg:
        status_msg = f"{hp_text}{items_status} | {custom_msg}"
    else:
        status_msg = f"{hp_text}{items_status} | [WASD]: Move | [Q]: Shield Knockback"
        
    text_drawer.color("#333333")
    text_drawer.write(status_msg, align="center", font=("Arial", 10, "bold"))

def can_move_to(row, col, is_player=True):
    if 0 <= row < 15 and 0 <= col < 15:
        tile = maze_map[row][col]
        if tile == "1": return False

        # 【核心修改点 1】玩家碰到密码门（C）触发输入弹窗
        if tile == "C":
            if is_player:
                draw_game()
                user_input = screen.textinput("Code Gate", "Enter the 4-digit security code:")
                screen.listen() # 输入完后重新让主窗口获得焦点
                
                if user_input == paper_code:
                    maze_map[row][col] = "0" # 密码正确开门
                    update_status_text("🔓 ACCESS GRANTED! Code gate opened!")
                    return True 
                else:
                    update_status_text("❌ INVALID CODE! Check the paper (📜)!")
                    return False 
            return False 

        if tile == "D":
            if is_player:
                global has_key
                if has_key:
                    maze_map[row][col] = "0"
                    has_key = False
                    update_status_text("🔓 Door unlocked with key!")
                    return True
                else:
                    update_status_text("🔒 Locked! Need Key (K)!")
                    return False
            return False 
            
        if tile == "G" and not gate_unlocked:
            if is_player:
                global player_hp, game_over
                player_hp -= 25
                update_status_text("⚡ ZAP! Touched electric gate! -25 HP")
                if player_hp <= 0:
                    game_over = True
                    update_status_text("💀 Shocked to death! Game Over! [R]")
            return False
        return True
    return False

# --- 3. 游戏机制状态判定 ---
def check_game_status():
    global game_over, player_row, player_col, player_hp, freeze_duration, portal_cooldown, room3_light_mode, has_key, switches_activated, gate_unlocked, read_paper
    if game_over: return
    
    tile = maze_map[player_row][player_col]

    # 【新增逻辑】走到纸条上可以拾取/查看密码
    if tile == "I":
        read_paper = True
        update_status_text(f"📜 Discarded note: 'Security Code is {paper_code}'")
        return 

    elif tile == "K":
        has_key = True
        maze_map[player_row][player_col] = "0"
        update_status_text("🔑 Key collected! Open Door (D) ahead.")
    elif tile == "B":
        if room3_light_mode == 0: room3_light_mode = 1
        maze_map[player_row][player_col] = "0"
        update_status_text("🔋 Master Box Active! Room 3 Fog Mode enabled.")
    elif tile == "S":
        switches_activated += 1
        maze_map[player_row][player_col] = "0"
        if switches_activated == total_switches:
            room3_light_mode = 2
            gate_unlocked = True
            update_status_text("⚡ FULL POWER! Electric gate opened!")
        else:
            update_status_text(f"⚡ Activated Switch ({switches_activated}/{total_switches})")
    elif tile == "T":
        player_hp -= 10
        maze_map[player_row][player_col] = "0" 
        if player_hp <= 0:
            game_over = True
            update_status_text("💀 Slain by spikes! Game Over! [R]")
        else:
            update_status_text("🩸 Spike Trap! -15 HP!")
    elif tile == "P":
        # 【核心修改点 2】修复原代码中 `player_row, portal1_col` 这一行未完成赋值导致崩溃的 Bug
        if not portal_cooldown:
            if player_row == portal1_row and player_col == portal1_col:
                player_row, player_col = portal2_row, portal2_col
            else:
                player_row, player_col = portal1_row, portal1_col
            portal_cooldown = True 
            return
    else:
        portal_cooldown = False

    if tile == "F":
        freeze_duration = 10 
        maze_map[player_row][player_col] = "0"
        update_status_text("❄️ Blizzard! Enemy frozen for 4 turns!")
        
    if tile == "2":
        game_over = True
        update_status_text("🏆 CHAMPION! All Chambers Conquered!")
        return
        
    if player_row == enemy_row and player_col == enemy_col:
        player_hp -= 0.1
        update_status_text("💥 Hit by Enemy! -0.1+. HP")
        if player_hp <= 0:
            game_over = True
            update_status_text("💀 Game Over! Press R to restart.")
        return

    if tile == "X" and trap_active:
        player_hp -= 30
        if player_hp <= 0:
            game_over = True
            update_status_text("💀 Game Over! [R]")
        else:
            player_row, player_col = 1, 3 
            portal_cooldown = False
            update_status_text("💥 Exploded! Respawned at start! -30 HP")
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
        while parent[curr] != start: curr = parent[curr]
        enemy_row, enemy_col = curr[0], curr[1]

# --- 4. 交互式动作引擎 ---
def execute_game_step(next_row, next_col, d_row, d_col):
    global player_row, player_col, trap_active, last_direction
    if game_over: return
    
    last_direction = (d_row, d_col)
    
    if can_move_to(next_row, next_col, is_player=True):
        player_row = next_row
        player_col = next_col
        trap_active = not trap_active
        
        check_game_status()
        if not game_over:
            move_enemy()
            check_game_status()
            update_status_text()
            draw_game() 
    else:
        update_status_text()
        draw_game()
    screen.listen()

def shield_knockback():
    global enemy_row, enemy_col, freeze_duration
    if game_over: return
    
    front_row = player_row + last_direction[0]
    front_col = player_col + last_direction[1]

    if front_row == enemy_row and front_col == enemy_col:
        kb_row = enemy_row + last_direction[0] * 2
        kb_col = enemy_col + last_direction[1] * 2
        
        if not can_move_to(kb_row, kb_col, is_player=False):
            kb_row = enemy_row + last_direction[0]
            kb_col = enemy_col + last_direction[1]
            
        enemy_row, enemy_col = kb_row, kb_col
        freeze_duration = 1  
        update_status_text("🛡️ SHIELD SLAM! Enemy knocked back and STUNNED!")
        check_game_status()
        draw_game()
    else:
        update_status_text("💨 Shield swung but missed! (Use [Q] when enemy is directly ahead)")
    screen.listen()

def move_up():    execute_game_step(player_row - 1, player_col, -1, 0)
def move_down():  execute_game_step(player_row + 1, player_col, 1, 0)
def move_left():  execute_game_step(player_row, player_col - 1, 0, -1)
def move_right(): execute_game_step(player_row, player_col + 1, 0, 1)

def reset_game():
    global game_over, player_hp, freeze_duration, player_row, player_col, enemy_row, enemy_col, maze_map, trap_active, portal_cooldown, room3_light_mode, has_key, switches_activated, gate_unlocked, last_direction, read_paper
    game_over = False
    player_hp = 100
    freeze_duration = 0
    trap_active = False
    portal_cooldown = False
    room3_light_mode = 0
    has_key = False
    gate_unlocked = False
    switches_activated = 0
    last_direction = (1, 0)
    read_paper = False
    player_row, player_col = 1, 1
    enemy_row, enemy_col = 13, 13
    maze_map = [row[:] for row in original_map]
    draw_game()
    update_status_text()
    screen.listen()

# --- 5. 事件绑定与启动 ---
screen.listen()
screen.onkey(move_up, "w")
screen.onkey(move_down, "s")
screen.onkey(move_left, "a")
screen.onkey(move_right, "d")
screen.onkey(shield_knockback, "q") 
screen.onkey(reset_game, "r")

draw_game()
update_status_text()
turtle.done()