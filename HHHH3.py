import turtle
from collections import deque

# --- 1. 初始化最基础的游戏画布 ---
screen = turtle.Screen()
screen.setup(440, 440)
screen.bgcolor("black") 
screen.title("Pure Chase: Frozen Orb Edition")
screen.tracer(0) 

tile_size = 28
game_over = False
player_stuck = False  

# 核心统计变量
player_hp = 100
total_switches = 3
switches_activated = 0
gate_unlocked = False

# 钥匙与普通门的状态
has_key = False
door_opened = False

# 【新增】冰冻球状态变量：剩余冰冻回合数
freeze_turns = 0

# 15x15 包含：1:墙, 0:路, S:蓝电箱, G:电门, 2:金块, T:机关, K:钥匙, D:带锁的门, F:冰冻球, W:红块结界
maze_map = [
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1"],
    ["1","0","0","0","0","0","0","0","0","0","G","T","T","2","1"], # 右上角终点
    ["1","0","1","0","1","1","1","1","G","1","1","1","1","1","1"], 
    ["1","0","1","0","D","0","0","0","S","1","1","S","F","F","1"], # 2个蓝电箱
    ["1","1","1","0","1","0","0","0","0","1","1","F","F","F","1"],
    ["1","0","0","F","0","1","0","0","0","1","1","F","F","F","1"],
    ["1","0","1","1","0","1","1","1","D","1","1","1","W","W","1"], # 在这里放置一扇门 D
    ["1","0","S","0","0","0","0","0","0","0","0","0","0","T","1"], # 1个蓝电箱
    ["1","1","1","0","1","1","1","0","1","1","1","0","1","1","1"],
    ["1","K","0","0","1","1","1","0","0","1","1","0","0","0","1"], # 在这里放置一把钥匙 K
    ["1","0","1","1","1","1","1","0","1","1","1","1","1","0","1"],
    ["1","0","0","0","0","1","1","0","1","1","0","0","0","0","1"], 
    ["1","0","1","1","1","1","1","W","1","1","0","1","1","0","1"], # W 为红块结界
    ["1","0","0","F","0","0","0","0","0","0","0","0","0","0","1"], # 【新增】在第13行第3列埋藏一颗冰冻球 "F"
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1"]
]

drawer = turtle.Turtle()
drawer.hideturtle()
drawer.speed(0)

msg_painter = turtle.Turtle()
msg_painter.hideturtle()
msg_painter.speed(0)

player_row = 1
player_col = 1
enemy_row = 13
enemy_col = 13

# --- 2. 基础渲染函数 ---
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

def draw_game(force_reveal=False):
    """渲染游戏画面"""
    drawer.clear()
    
    # 修改机制：如果激活了至少1个蓝电箱，或者游戏结束，则全图大放光明；否则依然保持2格迷雾
    light_on = force_reveal or (switches_activated >= 1)
    
    for r in range(15):
        for c in range(15):
            distance = abs(r - player_row) + abs(c - player_col)
            
            # 没开灯且超出视距，全黑
            if not light_on and distance > 2:
                draw_square(c, r, "black")
                continue
                
            tile = maze_map[r][c]
            if tile == "1":
                draw_square(c, r, "navy")     # 障碍深蓝色
            elif tile == "2":
                draw_square(c, r, "yellow")    # 金色终点
            elif tile == "S":
                draw_square(c, r, "blue")      # 蓝电箱
            elif tile == "G":
                draw_square(c, r, "cyan" if gate_unlocked else "orange") # 电门
            elif tile == "K":
                draw_square(c, r, "gold")      # 钥匙渲染为金黄色
            elif tile == "D":
                draw_square(c, r, "brown")     # 未开启的门渲染为棕色
            elif tile == "W":
                draw_square(c, r, "purple")    # 红块结界渲染为紫色
            elif tile == "F":
                draw_square(c, r, "lightskyblue") # 【新增】冰冻球渲染为浅冰蓝色
            elif tile == "T":
                draw_square(c, r, "darkgray")  
            else:
                draw_square(c, r, "darkgray")  

    # 敌人渲染逻辑：若处于冰冻状态，敌人显示为冰蓝色，否则为红色
    if light_on or (abs(enemy_row - player_row) + abs(enemy_col - player_col) <= 2):
        if freeze_turns > 0:
            draw_square(enemy_col, enemy_row, "lightskyblue") # 被冰冻的敌人外观
        else:
            draw_square(enemy_col, enemy_row, "red")
        
    draw_square(player_col, player_row, "green")
    screen.update()

# --- 3. 稳健距离追踪与伤害判定 ---
def can_move_to(row, col, is_player=True):
    if 0 <= row < 15 and 0 <= col < 15:
        tile = maze_map[row][col]
        if tile == "1": 
            return False
        if tile == "G" and not gate_unlocked:
            if is_player:
                trigger_gate_damage() 
            return False
        
        # 红块结界：绿块(Player)能过，红块(Enemy)不能过
        if tile == "W":
            if not is_player:
                return False
            return True
        
        # 撞到未开启的门逻辑
        if tile == "D":
            if is_player:
                global has_key, door_opened
                if has_key:
                    door_opened = True
                    maze_map[row][col] = "0" # 开门，变成通路
                    show_ui_message("DOOR OPENED WITH KEY!", "yellow")
                    return True
                else:
                    show_ui_message("NEED KEY FOR THIS DOOR!", "pink")
                    return False
            else:
                return False # 红块敌人无法通过未开的门
                
        return True
    return False

def trigger_gate_damage():
    """触电扣血 60"""
    global player_hp
    player_hp -= 60
    show_ui_message("ZAP! Gate -60 HP", "orange")
    check_hp_dead()

def check_hp_dead():
    global game_over
    if player_hp <= 0 and not game_over:
        game_over = True
        draw_game(force_reveal=True) 
        drawer.penup()
        drawer.goto(0, 0)
        drawer.color("red")
        drawer.write("WASTED!", align="center", font=("Arial", 24, "bold"))
        return True
    return False

def check_game_status():
    """检测当前的碰撞与交互状态"""
    global game_over, switches_activated, gate_unlocked, player_stuck, player_hp, has_key, freeze_turns
    if game_over: return

    tile = maze_map[player_row][player_col]
    
    # 1. 踩到机关
    if tile == "T":
        player_stuck = True
        player_hp -= 10
        maze_map[player_row][player_col] = "0"
        show_ui_message("TRAP! STUCK & -10 HP", "red")
        check_hp_dead()
    
    # 2. 踩到蓝电箱
    elif tile == "S":
        switches_activated += 1
        maze_map[player_row][player_col] = "0"
        if switches_activated == 1:
            show_ui_message("LIGHTS ON! 2 MORE TO OPEN GATE", "white")
        if switches_activated == total_switches:
            gate_unlocked = True
            show_ui_message("GATE UNLOCKED!", "cyan")

    # 3. 捡到钥匙
    elif tile == "K":
        has_key = True
        maze_map[player_row][player_col] = "0"
        show_ui_message("GOT THE KEY!", "gold")

    # 4. 【新增】捡到冰冻球
    elif tile == "F":
        freeze_turns = 5 # 赋予敌人 5 回合无法移动的冰冻状态
        maze_map[player_row][player_col] = "0"
        show_ui_message("FROZEN ORB! ENEMY FROZEN FOR 5 TURNS", "lightskyblue")

    # 5. 踩到红块敌人
    if player_row == enemy_row and player_col == enemy_col:
        player_hp -= 20
        show_ui_message("HIT! Enemy -20 HP", "red")
        check_hp_dead()

# --- BFS 高智商最短路径寻路算法 ---
def single_enemy_move():
    global enemy_row, enemy_col
    if enemy_row == player_row and enemy_col == player_col:
        return

    queue = deque()
    visited = set()
    
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] 
    for dr, dc in directions:
        nr, nc = enemy_row + dr, enemy_col + dc
        if can_move_to(nr, nc, is_player=False):
            queue.append((nr, nc, (dr, dc)))
            visited.add((nr, nc))

    found_step = None
    while queue:
        curr_r, curr_c, first_step = queue.popleft()
        
        if curr_r == player_row and curr_c == player_col:
            found_step = first_step
            break
            
        for dr, dc in directions:
            nr, nc = curr_r + dr, curr_c + dc
            if (nr, nc) not in visited and can_move_to(nr, nc, is_player=False):
                visited.add((nr, nc))
                queue.append((nr, nc, first_step))

    if found_step:
        enemy_row += found_step[0]
        enemy_col += found_step[1]

def move_enemy():
    global freeze_turns
    if game_over: return
    
    # 【新增】如果冰冻回合大于0，则敌人本回合跳过移动，并减少1个冰冻回合数
    if freeze_turns > 0:
        freeze_turns -= 1
        show_ui_message(f"ENEMY IS FROZEN! ({freeze_turns} turns left)", "lightskyblue")
        return

    for _ in range(1):
        single_enemy_move()
        check_game_status() 
        if game_over: break

def show_ui_message(text, color):
    """刷新顶部的UI栏"""
    msg_painter.clear()
    msg_painter.color(color)
    msg_painter.penup()
    msg_painter.goto(0, 190)
    key_status = "YES" if has_key else "NO"
    # 【新增】在UI中加入 Freeze 状态指示
    freeze_status = f"{freeze_turns}T" if freeze_turns > 0 else "NO"
    status_text = f"HP: {max(0, player_hp)} | Boxes: {switches_activated}/{total_switches} | Key: {key_status} | Freeze: {freeze_status} | {text}"
    msg_painter.write(status_text, align="center", font=("Arial", 9, "bold"))

# --- 4. 键盘响应机制 ---
def execute_game_step(next_row, next_col):
    global player_row, player_col, game_over, player_stuck
    if game_over: return
    
    if player_stuck:
        player_stuck = False
        show_ui_message("STUCK! TURN SKIPPED", "red")
        move_enemy()
        draw_game()
        return

    step_r = 1 if next_row > player_row else (-1 if next_row < player_row else 0)
    step_c = 1 if next_col > player_col else (-1 if next_col < player_col else 0)
    
    curr_r, curr_c = player_row, player_col
    target_r, target_c = next_row, next_col
    
    while curr_r != target_r or curr_c != target_c:
        nr = curr_r + step_r
        nc = curr_c + step_c
        if can_move_to(nr, nc, is_player=True):
            curr_r, curr_c = nr, nc
        else:
            break 
            
    player_row, player_col = curr_r, curr_c
    
    # 胜利截断
    if maze_map[player_row][player_col] == "2":
        game_over = True
        draw_game(force_reveal=True) 
        drawer.penup()
        drawer.goto(0, 0)
        drawer.color("green")
        drawer.write("THE CHOSEN RUNNER!", align="center", font=("Arial", 18, "bold"))
        return 

    check_game_status()
    if not game_over:
        move_enemy()
    
    if not game_over:
        draw_game()
        
    screen.listen()

def move_up():    execute_game_step(player_row - 1, player_col)
def move_down():  execute_game_step(player_row + 1, player_col)
def move_left():  execute_game_step(player_row, player_col - 1)
def move_right(): execute_game_step(player_row, player_col + 1)

# --- 5. 双重控制绑定 ---
screen.listen()
screen.onkey(move_up, "w")
screen.onkey(move_up, "W")
screen.onkey(move_down, "s")
screen.onkey(move_down, "S")
screen.onkey(move_left, "a")
screen.onkey(move_left, "A")
screen.onkey(move_right, "d")
screen.onkey(move_right, "D")

# 开局首次渲染
draw_game()
show_ui_message("NEED 1 BOX TO LIGHT UP, 3 BOXES FOR GATE!", "white")
turtle.done()