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

# 【修改：由 3 颗心改为 100 数值型生命值】
player_hp = 100 

freeze_duration = 0
portal_cooldown = False
trap_active = False

room3_light_mode = 0  # 0: 全黑 | 1: 电箱B激活 | 2: 3个蓝电箱S全清
has_key = False
switches_activated = 0
total_switches = 3

# 【更新地图：加入了 T (地刺陷阱) 和 G (电能大门)】
# 1 = 墙壁 | 0 = 通路 | 2 = 终极金块 | X = 闪烁陷阱 | O = 冰冻球 | P = 传送门 
# B = 总电箱 | K = 钥匙 | D = 带锁的门 | S = 蓝电箱
# T = 地刺陷阱 (-10HP) | G = 电能栅栏门 (碰触扣30HP，集齐3个S后移除)
original_map = [
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1"],
    ["1","0","K","0","1","1","0","0","0","0","0","0","0","2","1"], 
    ["1","S","1","0","1","1","0","1","0","1","1","0","1","G","1"], # 终点2前面放了G门阻挡
    ["1","O","1","0","1","1","O","1","0","1","1","O","1","0","1"], 
    ["1","1","1","0","1","1","1","1","0","1","1","1","1","D","1"], 
    ["1","0","T","0","1","1","S","0","0","0","0","0","0","0","1"], # 加了 T 陷阱
    ["1","0","1","1","1","1","0","1","1","1","1","1","1","0","1"], 
    ["1","0","0","0","P","1","0","0","X","1","1","0","T","0","1"], # 加了 T 陷阱
    ["1","1","1","0","1","1","1","0","1","1","1","0","1","1","1"], 
    ["1","S","0","0","1","1","K","0","0","1","1","0","0","0","1"], 
    ["1","0","1","1","1","1","1","B","1","1","1","1","1","0","1"], 
    ["1","0","0","0","0","1","1","0","1","1","0","0","0","0","1"], 
    ["1","1","1","1","D","1","1","0","1","1","0","1","1","1","1"], 
    ["1","1","1","1","0","0","0","0","1","1","0","0","0","0","1"], 
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
    if col <= 4: return 1 
    elif 5 <= col <= 9: return 2 
    else: return 3 

# --- 3. 坐标转换与核心绘制 ---
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
            elif tile == "O": draw_square(c, r, "#5dade2")     
            elif tile == "P": draw_square(c, r, "#9b59b6")     
            elif tile == "B": draw_square(c, r, "#1abc9c")     
            elif tile == "K": draw_square(c, r, "#f39c12")     
            elif tile == "D": draw_square(c, r, "#8e44ad")     
            elif tile == "S": draw_square(c, r, "#3498db")     
            elif tile == "T": draw_square(c, r, "#95a5a6")     # 【新增】地刺深灰色
            elif tile == "G": draw_square(c, r, "#e74c3c")     # 【新增】电能大门红色
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
    
    # 【修改：生命值文本显示】
    hp_text = f"{player_hp}/100" if player_hp > 0 else "DEAD"
    key_text = "🔑" if has_key else "❌"
    
    if custom_msg:
        status_msg = f"HP: {hp_text} | Key: {key_text} | {custom_msg}"
        text_drawer.color("#e74c3c")
    else:
        current_p_room = get_current_room(player_col)
        text_drawer.color("#333333")
        if current_p_room == 1:
            status_msg = f"HP: {hp_text} | Key: {key_text} | Room 1: Get Key to unlock Door(D)"
        elif current_p_room == 2 and room3_light_mode == 0:
            status_msg = f"HP: {hp_text} | Room 2: Find Master Box (B)"
        else:
            status_msg = f"HP: {hp_text} | Switches: {switches_activated}/{total_switches} | WASD to Move"
        
    text_drawer.write(status_msg, align="center", font=("Arial", 10, "bold"))

def can_move_to(row, col, is_player=True):
    global player_hp
    if 0 <= row < 15 and 0 <= col < 15:
        tile = maze_map[row][col]
        if tile == "1": return False
        
        if not is_player:
            # 敌人在G门没开时不能穿过去，也不能踩基础道具
            if tile in ["K", "B", "S", "2", "P", "G"]: return False

        # 【新增：碰撞电能大门 G 的判定】
        if tile == "G":
            if is_player:
                player_hp -= 30  # 碰 G 扣 30 HP
                if player_hp <= 0:
                    player_hp = 0
                update_status_text("💥 Ouch! Hit Electric Gate (G)! -30 HP!")
                return False     # 挡住不让过去
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

    # 【修改：触发 3 个 S 蓝电箱时，同时移除地图上所有的 G 栅栏门】
    elif tile == "S":
        switches_activated += 1
        maze_map[player_row][player_col] = "0"
        if switches_activated == total_switches:
            room3_light_mode = 2 
            # 开启电能大门：遍历地图把所有的 "G" 变成通行的 "0"
            for r in range(15):
                for c in range(15):
                    if maze_map[r][c] == "G":
                        maze_map[r][c] = "0"
            update_status_text("⚡ ALL POWER CONNECTED! Electric Gates OPENED!")
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

    # 【新增：踩中地刺 T 扣 10 HP，不触发重生】
    if tile == "T":
        player_hp -= 10
        maze_map[player_row][player_col] = "0" # 踩过之后陷阱失效变成空地
        if player_hp <= 0:
            player_hp = 0
            game_over = True
            update_status_text("💀 No HP Left! Game Over! [R]")
            return
        else:
            update_status_text("🩹 Stepped on Spikes (T)! -10 HP!")

    if tile == "O":
        freeze_duration = 4 
        maze_map[player_row][player_col] = "0"
        update_status_text("❄️ Enemy frozen for 4 turns!")
        
    # 【修改：碰撞终点 2 进入下一关/胜利】
    if tile == "2":
        game_over = True
        update_status_text("🏆 CHAMPION! Cleared to Next Stage!")
        return
        
    if player_row == enemy_row and player_col == enemy_col:
        game_over = True
        update_status_text("💀 Wasted! Caught by enemy. Press R.")
        return

    if maze_map[player_row][player_col] == "X" and trap_active:
        player_hp -= 20  # 踩中闪烁地雷也可以设置扣除一部分HP
        if player_hp <= 0:
            player_hp = 0
            game_over = True
            update_status_text("💀 No HP Left! Game Over! [R]")
        else:
            player_row, player_col = 1, 1 
            portal_cooldown = False
            update_status_text("💥 Boom! Trap exploded! Respawned to start!")
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
        # 即使被阻挡（如撞到 G 门），如果没死也重新渲染一下状态和血量
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
    player_hp = 100
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