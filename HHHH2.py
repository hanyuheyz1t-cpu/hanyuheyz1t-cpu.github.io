import turtle
from collections import deque

# --- 1. 初始化最基础的游戏画布 ---
screen = turtle.Screen()
screen.setup(440, 440)
screen.bgcolor("black") 
screen.title("Pure Chase: Six Chambers - Turn Based Edition")
screen.tracer(0) 

tile_size = 28
game_over = False
player_stuck = False  

# 核心统计变量
player_hp = 100
enemy_hp = 100          # 新增：红块敌人的初始血量
total_switches = 3
switches_activated = 0
gate_unlocked = False

# 钥匙与普通门的状态
has_key = False
door_opened = False

# 状态变量（包含冰冻球和反噬瘫痪状态）
freeze_turns = 0
enemy_stun_turns = 0    # 新增：红块伤害玩家后的10回合瘫痪状态

# 【15x15 六大房间地图】
maze_map = [
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1"],
    ["1","0","0","0","0","0","0","0","D","0","G","T","T","2","1"], 
    ["1","0","0","0","1","1","1","1","1","0","1","1","1","1","1"], 
    ["1","0","0","0","W","D","D","W","0","0","1","S","0","0","1"], 
    ["1","1","1","0","1","1","1","1","1","0","1","0","0","T","1"],
    ["1","0","0","0","0","0","0","1","0","0","1","T","0","0","1"],
    ["1","0","1","1","0","1","1","1","D","1","1","1","0","0","1"], 
    ["1","0","S","0","0","0","T","0","0","0","0","0","0","T","1"], 
    ["1","1","1","0","1","1","1","0","1","1","1","0","1","1","1"],
    ["1","0","0","T","1","1","1","0","0","1","1","0","0","0","1"], 
    ["1","S","1","1","1","1","1","0","1","1","1","1","1","0","1"],
    ["1","0","1","1","1","1","1","0","0","1","1","1","1","1","1"], 
    ["1","0","K","0","0","0","1","W","0","0","0","0","0","T","0"], 
    ["1","F","F","F","F","F","F","F","F","F","F","F","F","F","F"], 
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1"]
]

# 核心画笔定义
drawer = turtle.Turtle()
drawer.hideturtle()
drawer.speed(0)

msg_painter = turtle.Turtle()
msg_painter.hideturtle()
msg_painter.speed(0)

# 初始坐标
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
    drawer.clear()
    
    light_on = force_reveal or (switches_activated >= 1)
    
    for r in range(15):
        for c in range(15):
            distance = abs(r - player_row) + abs(c - player_col)
            
            if not light_on and distance > 2:
                draw_square(c, r, "black")
                continue
                
            tile = maze_map[r][c]
            if tile == "1":
                draw_square(c, r, "navy")       
            elif tile == "2":
                draw_square(c, r, "yellow")     
            elif tile == "S":
                draw_square(c, r, "blue")       
            elif tile == "G":
                draw_square(c, r, "cyan" if gate_unlocked else "orange") 
            elif tile == "K":
                draw_square(c, r, "gold")       
            elif tile == "D":
                draw_square(c, r, "brown")      
            elif tile == "W":
                draw_square(c, r, "purple")     
            elif tile == "F":
                draw_square(c, r, "lightskyblue") 
            elif tile == "T":
                draw_square(c, r, "darkgray")   
            else:
                draw_square(c, r, "darkgray")   

    # 敌人色彩状态树
    if light_on or (abs(enemy_row - player_row) + abs(enemy_col - player_col) <= 2):
        if enemy_stun_turns > 0:
            draw_square(enemy_col, enemy_row, "gray")          # 反噬瘫痪：显示灰色
        elif freeze_turns > 0:
            draw_square(enemy_col, enemy_row, "lightskyblue")  # 冰冻球：冰蓝色
        else:
            draw_square(enemy_col, enemy_row, "red")          # 正常：红色
        
    draw_square(player_col, player_row, "green")
    screen.update()

# --- 3. 移动可行性物理判定 ---
def can_move_to(row, col, is_player=True):
    if 0 <= row < 15 and 0 <= col < 15:
        tile = maze_map[row][col]
        if tile == "1": 
            return False
        
        if tile == "G" and not gate_unlocked:
            if is_player:
                trigger_gate_damage() 
            return False
        
        if tile == "W":
            if not is_player:
                return False
            return True
        
        if tile == "D":
            if is_player:
                global has_key, door_opened
                if has_key:
                    door_opened = True
                    maze_map[row][col] = "0" 
                    show_ui_message("DOOR OPENED WITH KEY!", "yellow")
                    return True
                else:
                    show_ui_message("NEED KEY FOR THIS DOOR!", "pink")
                    return False
            else:
                return False 
                
        return True
    return False

def trigger_gate_damage():
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
    global game_over, switches_activated, gate_unlocked, player_stuck, player_hp, enemy_hp, has_key, freeze_turns, enemy_stun_turns
    if game_over: return

    tile = maze_map[player_row][player_col]
    
    # 1. 踩到机关 T
    if tile == "T":
        player_stuck = True
        player_hp -= 10
        maze_map[player_row][player_col] = "0"
        show_ui_message("TRAP! STUCK & -10 HP", "red")
        check_hp_dead()
    
    # 2. 踩到蓝电箱 S
    elif tile == "S":
        switches_activated += 1
        maze_map[player_row][player_col] = "0"
        if switches_activated == 1:
            show_ui_message("LIGHTS ON! 2 MORE TO OPEN GATE", "white")
        if switches_activated == total_switches:
            gate_unlocked = True
            show_ui_message("GATE UNLOCKED!", "cyan")

    # 3. 捡到钥匙 K
    elif tile == "K":
        has_key = True
        maze_map[player_row][player_col] = "0"
        show_ui_message("GOT THE KEY!", "gold")

    # 4. 捡到冰冻球 F
    elif tile == "F":
        freeze_turns = 5 
        maze_map[player_row][player_col] = "0"
        show_ui_message("FROZEN ORB! ENEMY FROZEN FOR 5 TURNS", "lightskyblue")

    # 5. 重合碰撞检测：红块撞上绿块
    if player_row == enemy_row and player_col == enemy_col:
        # 如果敌人当前不在瘫痪僵直状态中，才触发碰撞结算
        if enemy_stun_turns <= 0:
            player_hp -= 20
            enemy_hp -= 10       # 红块自身受损扣除 10HP
            enemy_stun_turns = 10 # 触发长达 10 回合的瘫痪中断
            show_ui_message("BANG! Green -20HP | Red -10HP & STUNNED 10T", "red")
            check_hp_dead()

# --- BFS 寻路算法 ---
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
    global freeze_turns, enemy_stun_turns
    if game_over: return
    
    # 优先扣减受创瘫痪状态
    if enemy_stun_turns > 0:
        enemy_stun_turns -= 1
        return

    # 其次处理普通的冰冻状态
    if freeze_turns > 0:
        freeze_turns -= 1
        return

    # 正常推进行动步
    for _ in range(1):
        single_enemy_move()
        check_game_status() 
        if game_over: break

def show_ui_message(text, color):
    msg_painter.clear()
    msg_painter.color(color)
    msg_painter.penup()
    msg_painter.goto(0, 190)
    key_status = "YES" if has_key else "NO"
    
    # 动态构建敌人当前阻断状态描述
    if enemy_stun_turns > 0:
        enemy_status = f"STUN({enemy_stun_turns}T)"
    elif freeze_turns > 0:
        enemy_status = f"FREEZE({freeze_turns}T)"
    else:
        enemy_status = "ACTIVE"
        
    status_text = f"GreenHP: {max(0, player_hp)} | RedHP: {max(0, enemy_hp)} | Red: {enemy_status} | {text}"
    msg_painter.write(status_text, align="center", font=("Arial", 8, "bold"))

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
    
    if maze_map[player_row][player_col] == "2":
        game_over = True
        draw_game(force_reveal=True) 
        drawer.penup()
        drawer.goto(0, 0)
        drawer.color("green")
        drawer.write("SIX CHAMBERS CONQUERED!", align="center", font=("Arial", 16, "bold"))
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