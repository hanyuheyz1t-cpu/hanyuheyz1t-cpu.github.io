import turtle
import random

# ----------------- 游戏初始化 -----------------
screen = turtle.Screen()
screen.title("Three Chambers - 10. Hell Mode: Finale")
screen.bgcolor("black")
screen.setup(width=600, height=600)
screen.tracer(0)

# ----------------- 绘制迷宫边界与障碍 -----------------
drawer = turtle.Turtle()
drawer.hideturtle()
drawer.speed(0)
drawer.color("red")
drawer.pensize(3)

def draw_borders():
    drawer.penup()
    drawer.goto(-250, 250)
    drawer.pendown()
    for _ in range(4):
        drawer.forward(500)
        drawer.right(90)

draw_borders()

# ----------------- 玩家设置 -----------------
player = turtle.Turtle()
player.shape("square")
player.color("green")
player.penup()
player.speed(0)
player.goto(-200, 200)

# ----------------- 敌人设置 (地狱模式多重追击) -----------------
enemies = []
colors = ["purple", "orange", "magenta"]
for i in range(3):
    en = turtle.Turtle()
    en.shape("square")
    en.color(colors[i])
    en.penup()
    en.speed(0)
    en.goto(150 + i * 30, -150)
    enemies.append(en)

# ----------------- 游戏状态变量 -----------------
score = 0
game_over = False

# ----------------- 移动控制函数 -----------------
def move_up():
    y = player.ycor()
    if y < 230:
        player.sety(y + 20)

def move_down():
    y = player.ycor()
    if y > -230:
        player.sety(y - 20)

def move_left():
    x = player.xcor()
    if x > -230:
        player.setx(x - 20)

def move_right():
    x = player.xcor()
    if x < 230:
        player.setx(x + 20)

# 特殊技能按键模拟 (Q 键推开敌人 / E 键清除障碍提示)
def special_push():
    for en in enemies:
        if player.distance(en) < 50:
            en.backward(40)

def restart_game():
    global game_over
    game_over = False
    player.goto(-200, 200)
    for i, en in enumerate(enemies):
        en.goto(150 + i * 30, -150)

# ----------------- 键盘绑定 -----------------
screen.listen()
screen.onkey(move_up, "w")
screen.onkey(move_down, "s")
screen.onkey(move_left, "a")
screen.onkey(move_right, "d")
screen.onkey(move_up, "Up")
screen.onkey(move_down, "Down")
screen.onkey(move_left, "Left")
screen.onkey(move_right, "Right")
screen.onkey(special_push, "q")
screen.onkey(restart_game, "r")

# ----------------- 游戏主循环 -----------------
def game_loop():
    global game_over
    if not game_over:
        # 敌人的追踪逻辑
        for en in enemies:
            en.setheading(en.towards(player))
            en.forward(1.5)  # 地狱模式敌人的移动速度较快
            
            # 检测碰撞
            if player.distance(en) < 15:
                game_over = True
                
        screen.update()
        screen.ontimer(game_loop, 20)
    else:
        drawer.penup()
        drawer.goto(0, 0)
        drawer.color("white")
        drawer.write("GAME OVER - 按 R 键重试", align="center", font=("Arial", 20, "bold"))
        screen.update()

game_loop()
screen.mainloop()