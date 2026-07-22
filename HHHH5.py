import turtle
from collections import deque

# --- 1. 初始化屏幕与游戏变量 ---
screen = turtle.Screen()
screen.setup(480, 520) 
screen.bgcolor("#f0f0f0") 
screen.title("Three Chambers: Shield Knockback & Barrier Edition")
screen.tracer(0) 

tile_size = 28
game_over = False
player_hp = 100       
freeze_duration = 0
portal_cooldown = False
trap_active = False

# 联动机制核心变量
room3_light_mode = 0    # 0:全黑 | 1:总电箱激活 | 2:蓝电箱全清(电门开)
has_pickaxe = False     
has_key = False         
has_code_key = False    # 6. Code Gate: 找到钥匙开启最终电门
gate_unlocked = False   
switches_activated = 0  
total_switches = 3      
last_direction = (1, 0) # 记录玩家方向

# 15x15 宏大世界地图
# 1:墙 | 0:路 | S:蓝电箱 | G:电门 | 2:金块 | T:突刺机关 | K:钥匙 | D:带锁的门 | F:冰冻球 | W:红块结界 | X:闪烁陷阱 | B:总电箱 | P:传送门 | C:Code Gate钥匙
original_map = [
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1"],
    ["1","0","K","0","1","1","B","0","0","1","1","G","S","C","1"],  # 金块2改为Code Gate钥匙C
    ["1","0","1","0","1","1","0","1","0","1","1","1","1","1","1"], 
    ["1","F","1","D","1","1","F","1","0","1","1","F","1","0","1"], 
    ["1","1","1","0","1","1","1","1","0","1","1","0","1","0","1"], 
    ["1","M","0","0","1","1","0","0","0","0","0","0","0","0","1"], 
    ["1","0","1","1","1","1","0","1","1","1","1","1","1","0","1"], 
    ["1","0","0","0","0","1","0","0","X","1","1","S","0","T","1"], 
    ["1","1","1","0","1","1","1","0","1","1","1","0","1","1","1"], 
    ["P","0","0","0","1","1","0","0","0","1","1","W","W","W","1"], # W 为红块专属结界区域
    ["1","0","1","1","1","1","1","1","1","1","1","0","0","0","1"], 
    ["1","0","0","0","0","1","1","0","1","1","S","0","0","0","1"], 
    ["1","1","1","1","0","1","1","P","1","1","0","1","1","1","1"], 
    ["1","1","1","1","0","0","0","0","1","1","0","0","0","0","1"], 
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
            elif tile == "F": draw_square(c, r, "#5dade2")     # 冰冻球
            elif tile == "P": draw_square(c, r, "#9b59b6")     
            elif tile == "B": draw_square(c, r, "#1abc9c")     
            elif tile == "M": draw_square(c, r, "#95a5a6")     
            elif tile == "K": draw_square(c, r, "#f39c12")     
            elif tile == "D": draw_square(c, r, "#8e44ad")     
            elif tile == "S": draw_square(c, r, "#3498db")     
            elif tile == "G": draw_square(c, r, "#16a085" if gate_unlocked else "#d35400") 
            elif tile == "T": draw_square(c, r, "#7f8c8d")     
            elif tile == "W": draw_square(c, r, "#e74c3c")     # 红块结界显示为红色镂空感（浅红）
            elif tile == "C": draw_square(c, r, "#f1c40f")     # Code Gate钥匙 (金色)
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
    if has_pickaxe: items_status += " ⛏️"
    if has_key: items_status += " 🔑"
    if has_code_key: items_status += " 🗝️"  # Code Gate钥匙标识
    
    if custom_msg:
        status_msg = f"{hp_text}{items_status} | {custom_msg}"
    else:
        status_msg = f"{hp_text}{items_status} | [WASD]: Move | [E]: Dig | [Q]: Shield Knockback / Place Wall"
        
    text_drawer.color("#333333")
    text_drawer.write(status_msg, align="center", font=("Arial", 10, "bold"))

def can_move_to(row, col, is_player=True):
    if 0 <= row < 15 and 0 <= col < 15:
        tile = maze_map[row][col]
        if tile == "1": return False
        
        # 红块结界 W 的特殊判定
        if tile == "W":
            return not is_player # 只有红块可以通过，玩家无法通过

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
            
        # --- 6. Code Gate: 最终电门需要 Code Key 开启 ---
        if tile == "G" and not gate_unlocked:
            if is_player:
                global player_hp, game_over
                player_hp -= 60
                update_status_text("⚡ ZAP! Touched electric gate! -60 HP")
                if player_hp <= 0:
                    game_over = True
                    update_status_text("💀 Shocked to death! Game Over! [R]")
            return False
        
        if tile == "G" and gate_unlocked and not has_code_key:
            if is_player:
                update_status_text("🔒 Gate powered but locked! Need Code Key (🗝️) to enter!")
            return False
            
        return True
    return False

# --- 3. 游戏机制状态判定 ---
def check_game_status():
    global game_over, player_row, player_col, player_hp, freeze_duration, portal_cooldown, room3_light_mode, has_pickaxe, has_key, has_code_key, switches_activated, gate_unlocked
    if game_over: return
    
    tile = maze_map[player_row][player_col]

    if tile == "M":
        has_pickaxe = True
        maze_map[player_row][player_col] = "0"
        update_status_text("⛏️ Pickaxe obtained! [E] to smash walls / barriers.")
    elif tile == "K":
        has_key = True
        maze_map[player_row][player_col] = "0"
        update_status_text("🔑 Key collected! Open Door (D) ahead.")
    # --- 6. Code Gate: 收集 Code Key ---
    elif tile == "C":
        has_code_key = True
        maze_map[player_row][player_col] = "0"
        update_status_text("🗝️ Code Key obtained! Now enter the Gate (G) to win!")
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
            update_status_text("⚡ FULL POWER! Electric gate powered! Now find the Code Key (🗝️)!")
        else:
            update_status_text(f"⚡ Activated Switch ({switches_activated}/{total_switches})")
    elif tile == "T":
        player_hp -= 15
        maze_map[player_row][player_col] = "0" 
        if player_hp <= 0:
            game_over = True
            update_status_text("💀 Slain by spikes! Game Over! [R]")
        else:
            update_status_text("🩸 Spike Trap! -15 HP!")
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

    if tile == "F":
        freeze_duration = 4 
        maze_map[player_row][player_col] = "0"
        update_status_text("❄️ Blizzard! Enemy frozen for 4 turns!")
        
    # --- 6. Code Gate: 通过已开启的电门获胜 ---
    if tile == "G" and gate_unlocked and has_code_key:
        game_over = True
        update_status_text("🏆 CHAMPION! Code Gate opened! All Chambers Conquered!")
        return
        
    if player_row == enemy_row and player_col == enemy_col:
        player_hp -= 20
        update_status_text("💥 Hit by Enemy! -20 HP")
        if player_hp <= 0:
            game_over = True
            update_status_text("💀 Game Over! Press R to restart.")
        return

    if tile == "X" and trap_active:
        player_hp -= 10
        if player_hp <= 0:
            game_over = True
            update_status_text("💀 Game Over! [R]")
        else:
            player_row, player_col = 1, 1 
            portal_cooldown = False
            update_status_text("💥 Exploded! Respawned at start! -10 HP")
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
            # 红块寻路判定（红块可以通过普通路、传送门和红块结界 W）
            if can_move_to(nr, nc, is_player=False) and (nr, nc) not in parent:
                parent[(nr, nc)] = (curr_row, curr_col)
                queue.append((nr, nc))

    if found:
        curr = (player_row, player_col)
        while parent[curr] != start: curr = parent[curr]
        enemy_row, enemy_col = curr[0], curr[1]

# --- 4. 交互式动作引擎（包含Q键完美击退与剥夺回合） ---
def execute_game_step(next_row, next_col, d_row, d_col):
    global player_row, player_col, trap_active, last_direction
    if game_over: return
    
    last_direction = (d_row, d_col)
    
    # 如果玩家直接走上红块格子，依然触发正常受伤判定
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
    screen.listen()

def use_pickaxe():
    global has_pickaxe
    if game_over: return
    if not has_pickaxe:
        update_status_text("❌ No pickaxe equipped!")
        return

    front_row = player_row + last_direction[0]
    front_col = player_col + last_direction[1]

    if 0 <= front_row < 15 and 0 <= front_col < 15:
        target_tile = maze_map[front_row][front_col]
        # 稿子现在可以砸碎墙壁(1)和红块结界(W)
        if target_tile in ("1", "W"):
            if front_row in (0, 14) or front_col in (0, 14):
                update_status_text("🚧 Boundary walls cannot be broken!")
                return
            maze_map[front_row][front_col] = "0"
            update_status_text("⛏️ Obstacle crushed into pathway!")
            move_enemy()
            check_game_status()
            draw_game()
        else:
            update_status_text("💨 Nothing to smash ahead.")
    screen.listen()

def place_wall_or_knockback():
    global enemy_row, enemy_col, freeze_duration
    if game_over: return
    
    front_row = player_row + last_direction[0]
    front_col = player_col + last_direction[1]

    # 【核心：Q键精准击退与定身逻辑】
    if front_row == enemy_row and front_col == enemy_col:
        # 计算击退 2 格的落点
        kb_row = enemy_row + last_direction[0] * 2
        kb_col = enemy_col + last_direction[1] * 2
        
        # 边缘与不可通行阻挡判定
        if not can_move_to(kb_row, kb_col, is_player=False):
            # 缩减为击退 1 格
            kb_row = enemy_row + last_direction[0]
            kb_col = enemy_col + last_direction[1]
            
        enemy_row, enemy_col = kb_row, kb_col
        freeze_duration = 1  # 强力一击！红块在本回合被击晕，无法追击回来
        update_status_text("🛡️ SHIELD SLAM! Enemy knocked back and STUNNED!")
        check_game_status()
        draw_game()
        return

    # 如果前面不是红块，则执行放墙块逻辑
    if 0 <= front_row < 15 and 0 <= front_col < 15:
        target_tile = maze_map[front_row][front_col]
        if target_tile == "0":
            maze_map[front_row][front_col] = "1"
            update_status_text("🧱 Block placed firmly!")
            move_enemy()
            check_game_status()
            draw_game()
        else:
            update_status_text("💨 Choose an empty space to place a block.")
    screen.listen()

def move_up():    execute_game_step(player_row - 1, player_col, -1, 0)
def move_down():  execute_game_step(player_row + 1, player_col, 1, 0)
def move_left():  execute_game_step(player_row, player_col - 1, 0, -1)
def move_right(): execute_game_step(player_row, player_col + 1, 0, 1)

# --- 5. 重置游戏 ---
def reset_game():
    global game_over, player_hp, freeze_duration, player_row, player_col, enemy_row, enemy_col, maze_map, trap_active, portal_cooldown, room3_light_mode, has_pickaxe, has_key, has_code_key, switches_activated, gate_unlocked, last_direction
    game_over = False
    player_hp = 100
    freeze_duration = 0
    trap_active = False
    portal_cooldown = False
    room3_light_mode = 0
    has_pickaxe = False
    has_key = False
    has_code_key = False
    gate_unlocked = False
    switches_activated = 0
    last_direction = (1, 0)
    player_row, player_col = 1, 1
    enemy_row, enemy_col = 13, 13
    maze_map = [row[:] for row in original_map]
    draw_game()
    update_status_text()
    screen.listen()

# --- 6. Code Gate: 找到 Code Key 开启最终电门 ---
# 玩家需要在房间3中：
#   1. 激活总电箱 (B) → 房间3半照明模式
#   2. 激活全部3个蓝电箱 (S) → 电门通电 (gate_unlocked = True)
#   3. 找到 Code Key (C) → 获得开门权限 (has_code_key = True)
#   4. 携带 Code Key 走入已通电的电门 (G) → 🏆 胜利！
#
# 相关修改：
#   - can_move_to(): 通电后的电门需要 Code Key 才能进入
#   - check_game_status(): 收集 C 设置 has_code_key；进入通电电门触发 victory
#   - update_status_text(): 显示 🗝️ Code Key 持有标识

# --- 7. 事件绑定与启动 ---
screen.listen()
screen.onkey(move_up, "w")
screen.onkey(move_down, "s")
screen.onkey(move_left, "a")
screen.onkey(move_right, "d")
screen.onkey(use_pickaxe, "e")
screen.onkey(place_wall_or_knockback, "q")
screen.onkey(reset_game, "r")

draw_game()
update_status_text()
import turtle
from collections import deque

# --- 1. 初始化屏幕与游戏变量 ---
screen = turtle.Screen()
screen.setup(480, 520) 
screen.bgcolor("#f0f0f0") 
screen.title("Three Chambers: Shield Knockback & Barrier Edition")
screen.tracer(0) 

tile_size = 28
game_over = False
player_hp = 100       
freeze_duration = 0
portal_cooldown = False
trap_active = False

# 联动机制核心变量
room3_light_mode = 0    
has_pickaxe = False     
has_key = False         
has_code_key = False    
gate_unlocked = False   
switches_activated = 0  
total_switches = 3      
last_direction = (1, 0) 

# 地图定义
original_map = [
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1"],
    ["1","0","K","0","1","1","B","0","0","1","1","G","S","C","1"], 
    ["1","0","1","0","1","1","0","1","0","1","1","1","1","1","1"], 
    ["1","F","1","D","1","1","F","1","0","1","1","F","1","0","1"], 
    ["1","1","1","0","1","1","1","1","0","1","1","0","1","0","1"], 
    ["1","M","0","0","1","1","0","0","0","0","0","0","0","0","1"], 
    ["1","0","1","1","1","1","0","1","1","1","1","1","1","0","1"], 
    ["1","0","0","0","0","1","0","0","X","1","1","S","0","T","1"], 
    ["1","1","1","0","1","1","1","0","1","1","1","0","1","1","1"], 
    ["P","0","0","0","1","1","0","0","0","1","1","W","W","W","1"], 
    ["1","0","1","1","1","1","1","1","1","1","1","0","0","0","1"], 
    ["1","0","0","0","0","1","1","0","1","1","S","0","0","0","1"], 
    ["1","1","1","1","0","1","1","P","1","1","0","1","1","1","1"], 
    ["1","1","1","1","0","0","0","0","1","1","0","0","0","0","1"], 
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

# --- 2. 核心逻辑与渲染 ---
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
            
            # 照明逻辑
            if tile_room == 2 and distance > 2:
                draw_square(c, r, "#1a1a1a"); continue
            if tile_room == 3:
                if room3_light_mode == 0: draw_square(c, r, "#1a1a1a"); continue
                elif room3_light_mode == 1 and distance > 2: draw_square(c, r, "#1a1a1a"); continue

            tile = maze_map[r][c]
            colors = {"1":"#34495e", "2":"#f1c40f", "F":"#5dade2", "P":"#9b59b6", "B":"#1abc9c", 
                      "M":"#95a5a6", "K":"#f39c12", "D":"#8e44ad", "S":"#3498db", "T":"#7f8c8d", 
                      "W":"#e74c3c", "C":"#f1c40f", "0":"#e5e7e9"}
            
            if tile == "X": draw_square(c, r, "#e67e22" if trap_active else "#bdc3c7")
            elif tile == "G": draw_square(c, r, "#16a085" if gate_unlocked else "#d35400")
            else: draw_square(c, r, colors.get(tile, "#e5e7e9"))

            # 敌人显示
            if r == enemy_row and c == enemy_col:
                visible = (tile_room != 3) or (room3_light_mode == 2) or (room3_light_mode == 1 and distance <= 2)
                if visible: draw_square(enemy_col, enemy_row, "#2980b9" if freeze_duration > 0 else "#e74c3c")
        
    draw_square(player_col, player_row, "#2ecc71")
    screen.update()

def update_status_text(custom_msg=""):
    text_drawer.clear()
    text_drawer.penup()
    text_drawer.goto(0, 185)
    items = (" ⛏️" if has_pickaxe else "") + (" 🔑" if has_key else "") + (" 🗝️" if has_code_key else "")
    msg = custom_msg if custom_msg else "[WASD]: Move | [E]: Dig | [Q]: Shield/Wall"
    text_drawer.color("#333333")
    text_drawer.write(f"HP: {max(0, player_hp)}/100{items} | {msg}", align="center", font=("Arial", 10, "bold"))

def can_move_to(row, col, is_player=True):
    if 0 <= row < 15 and 0 <= col < 15:
        tile = maze_map[row][col]
        if tile == "1": return False
        if tile == "W": return not is_player
        if tile == "D":
            if not is_player: return False
            if has_key: maze_map[row][col] = "0"; has_key = False; return True
            return False 
        if tile == "G":
            if not is_player: return False
            if not gate_unlocked: player_hp -= 60; update_status_text("⚡ ZAP! -60 HP"); return False
            if not has_code_key: update_status_text("🔒 Need Code Key (🗝️)!"); return False
            return True
        return True
    return False

def check_game_status():
    global game_over, player_hp, freeze_duration, portal_cooldown, room3_light_mode, has_pickaxe, has_key, has_code_key, switches_activated, gate_unlocked
    tile = maze_map[player_row][player_col]
    if tile == "M": has_pickaxe = True; maze_map[player_row][player_col] = "0"
    elif tile == "K": has_key = True; maze_map[player_row][player_col] = "0"
    elif tile == "C": has_code_key = True; maze_map[player_row][player_col] = "0"
    elif tile == "B": room3_light_mode = 1; maze_map[player_row][player_col] = "0"
    elif tile == "S": 
        switches_activated += 1; maze_map[player_row][player_col] = "0"
        if switches_activated == total_switches: room3_light_mode = 2; gate_unlocked = True
    elif tile == "T": player_hp -= 15; maze_map[player_row][player_col] = "0"
    elif tile == "F": freeze_duration = 4; maze_map[player_row][player_col] = "0"
    elif tile == "P":
        if not portal_cooldown:
            player_row, player_col = (portal2_row, portal2_col) if (player_row, player_col) == (portal1_row, portal1_col) else (portal1_row, portal1_col)
            portal_cooldown = True; return
    else: portal_cooldown = False

    if tile == "G" and gate_unlocked and has_code_key: game_over = True; update_status_text("🏆 CHAMPION!"); return
    if (player_row, player_col) == (enemy_row, enemy_col): player_hp -= 20
    if player_hp <= 0: game_over = True; update_status_text("💀 Game Over! [R]")

def move_enemy():
    global enemy_row, enemy_col, freeze_duration
    if game_over or freeze_duration > 0:
        if freeze_duration > 0: freeze_duration -= 1
        return
    start, target = (enemy_row, enemy_col), (player_row, player_col)
    queue = deque([start]); parent = {start: None}
    while queue:
        curr = queue.popleft()
        if curr == target:
            path = []
            while curr: path.append(curr); curr = parent[curr]
            enemy_row, enemy_col = path[-2] if len(path) > 1 else enemy_row, enemy_col; break
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = curr[0]+dr, curr[1]+dc
            if can_move_to(nr, nc, False) and (nr, nc) not in parent:
                parent[(nr, nc)] = curr; queue.append((nr, nc))

def execute_game_step(nr, nc, dr, dc):
    global player_row, player_col, trap_active, last_direction
    if game_over: return
    last_direction = (dr, dc)
    if can_move_to(nr, nc):
        player_row, player_col = nr, nc; trap_active = not trap_active
        check_game_status(); move_enemy(); check_game_status(); update_status_text(); draw_game()

def use_pickaxe():
    fr, fc = player_row + last_direction[0], player_col + last_direction[1]
    if has_pickaxe and 0 <= fr < 15 and 0 <= fc < 15 and maze_map[fr][fc] in ("1", "W"):
        maze_map[fr][fc] = "0"; move_enemy(); update_status_text("⛏️ Smashing!"); draw_game()

def place_wall_or_knockback():
    global enemy_row, enemy_col, freeze_duration
    fr, fc = player_row + last_direction[0], player_col + last_direction[1]
    if (fr, fc) == (enemy_row, enemy_col):
        kb_r, kb_c = enemy_row + last_direction[0] * 2, enemy_col + last_direction[1] * 2
        if not can_move_to(kb_r, kb_c, False): kb_r, kb_c = enemy_row + last_direction[0], enemy_col + last_direction[1]
        enemy_row, enemy_col = kb_r, kb_c; freeze_duration = 1; update_status_text("🛡️ STUNNED!"); draw_game()
    elif maze_map[fr][fc] == "0": maze_map[fr][fc] = "1"; move_enemy(); draw_game()

def reset_game():
    global game_over, player_hp, player_row, player_col, enemy_row, enemy_col, maze_map, has_pickaxe, has_key, has_code_key, gate_unlocked, switches_activated, room3_light_mode
    game_over, player_hp, has_pickaxe, has_key, has_code_key, gate_unlocked, switches_activated, room3_light_mode = False, 100, False, False, False, False, 0, 0
    player_row, player_col, enemy_row, enemy_col = 1, 1, 13, 13
    maze_map = [row[:] for row in original_map]; draw_game(); update_status_text(); screen.listen()

screen.listen()
screen.onkey(lambda: execute_game_step(player_row-1, player_col, -1, 0), "w")
screen.onkey(lambda: execute_game_step(player_row+1, player_col, 1, 0), "s")
screen.onkey(lambda: execute_game_step(player_row, player_col-1, 0, -1), "a")
screen.onkey(lambda: execute_game_step(player_row, player_col+1, 0, 1), "d")
screen.onkey(use_pickaxe, "e")
screen.onkey(place_wall_or_knockback, "q")
screen.onkey(reset_game, "r")

draw_game();
update_status_text(); 
