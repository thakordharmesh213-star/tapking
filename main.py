import pygame
import random
import math
import os
import wave
import struct

pygame.init()

# =========================
# SCREEN
# =========================
WIDTH, HEIGHT = 400, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tap King")
clock = pygame.time.Clock()

# =========================
# COLORS
# =========================
WHITE = (255,255,255)
BLACK = (15,15,25)
DARK = (15,22,55)
BLUE = (55,110,230)
PURPLE = (100,55,180)
GOLD = (255,200,0)
GREEN = (45,190,95)
RED = (230,60,70)
GRAY = (80,85,105)

font = pygame.font.Font(None,32)
small = pygame.font.Font(None,24)
big = pygame.font.Font(None,52)

# =========================
# PATHS
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE = os.path.join(BASE_DIR,"tapking_progress.txt")
CHAR_FILE = os.path.join(BASE_DIR,"character.png")

# =========================
# CHARACTER
# =========================
try:
    character = pygame.image.load(CHAR_FILE).convert_alpha()
    character_loaded = True
except:
    character = None
    character_loaded = False

# =========================
# SOUND
# =========================
try:
    pygame.mixer.init(22050,-16,1,512)
    SOUND = True
except:
    SOUND = False

def tone(freq,duration,volume=0.3):
    if not SOUND:
        return None

    rate = 22050
    count = int(rate*duration)
    raw = bytearray()

    for i in range(count):
        t = i/rate
        fade = 1

        if i < rate*0.02:
            fade = i/(rate*0.02)

        if i > count-rate*0.04:
            fade = (count-i)/(rate*0.04)

        v = int(
            32767*volume*fade*
            math.sin(2*math.pi*freq*t)
        )

        raw.extend(struct.pack("<h",v))

    try:
        return pygame.mixer.Sound(buffer=bytes(raw))
    except:
        return None

tap_sound = tone(750,0.07)
coin_sound = tone(1100,0.10)
wrong_sound = tone(180,0.15)
complete_sound = tone(1000,0.25)

def play(sound):
    if SOUND and sound:
        try:
            sound.play()
        except:
            pass

# =========================
# SAVE
# =========================
MAX_LEVEL = 45

def load_level():
    try:
        with open(SAVE_FILE,"r") as f:
            n = int(f.read())
            return max(1,min(MAX_LEVEL,n))
    except:
        return 1

def save_level(n):
    try:
        with open(SAVE_FILE,"w") as f:
            f.write(str(n))
    except:
        pass

unlocked = load_level()

# =========================
# GAME VARIABLES
# =========================
state = "menu"
level = 1
score = 0
coins = 0
lives = 3

target = 10
timer = 30
start_time = 0
size = 90

x = 200
y = 350

particles = []
ring = 0
scale = 1.0

# =========================
# BUTTONS
# =========================
play_btn = pygame.Rect(70,300,260,60)
settings_btn = pygame.Rect(70,375,260,55)
back_btn = pygame.Rect(20,20,100,45)

next_btn = pygame.Rect(70,450,260,60)
retry_btn = pygame.Rect(70,525,260,60)
menu_btn = pygame.Rect(100,610,200,45)

# =========================
# TEXT
# =========================
def text(msg,f,color,px,py):
    img = f.render(str(msg),True,color)
    r = img.get_rect(center=(px,py))
    screen.blit(img,r)

# =========================
# BACKGROUND
# =========================
stars = []

for i in range(60):
    stars.append([
        random.randrange(WIDTH),
        random.randrange(HEIGHT),
        random.randint(1,3)
    ])

def background():
    screen.fill(DARK)

    pygame.draw.circle(
        screen,(30,45,100),(60,180),150
    )

    pygame.draw.circle(
        screen,(65,35,110),(360,430),180
    )

    pygame.draw.circle(
        screen,(25,70,120),(200,700),180
    )

    for sx,sy,s in stars:
        pygame.draw.circle(
            screen,WHITE,(sx,sy),s
        )

# =========================
# LEVEL SETTINGS
# =========================
def settings(n):
    target = 8+n*2
    timer = max(12,40-int(n*0.5))
    size = max(45,100-n)
    return target,timer,size

# =========================
# MOVE KING
# =========================
def move():
    global x,y

    half = max(25,size//2)

    x = random.randint(
        half+5,
        WIDTH-half-5
    )

    y = random.randint(
        165,
        HEIGHT-half-15
    )

# =========================
# PARTICLES
# =========================
def make_particles(amount=20):
    for i in range(amount):
        a = random.uniform(0,math.pi*2)
        sp = random.uniform(1.5,5)

        particles.append([
            x,y,
            math.cos(a)*sp,
            math.sin(a)*sp,
            random.randint(20,40),
            random.randint(2,5)
        ])

def update_particles():
    for p in particles[:]:
        p[0]+=p[2]
        p[1]+=p[3]
        p[3]+=0.05
        p[4]-=1

        if p[4]<=0:
            particles.remove(p)

def draw_particles():
    for p in particles:
        pygame.draw.circle(
            screen,GOLD,
            (int(p[0]),int(p[1])),
            p[5]
        )

# =========================
# DRAW KING
# =========================
def draw_king():
    if character_loaded:
        s = int(size*1.45*scale)
        s = max(20,s)

        img = pygame.transform.smoothscale(
            character,(s,s)
        )

        r = img.get_rect(center=(x,y))
        screen.blit(img,r)

    else:
        pygame.draw.circle(
            screen,GOLD,(x,y),size//2
        )
        text("KING",small,BLACK,x,y)

# =========================
# START LEVEL
# =========================
def start_level(n):
    global level,score,coins,lives
    global target,timer,size,start_time
    global state,ring,scale

    level=n
    score=0
    coins=0
    lives=3

    target,timer,size=settings(level)

    start_time=pygame.time.get_ticks()

    particles.clear()
    ring=0
    scale=1

    move()

    state="game"

# =========================
# MENU
# =========================
def draw_menu():
    background()

    text("TAP KING",big,GOLD,200,80)
    text("CARTOON KING",small,WHITE,200,125)

    if character_loaded:
        img=pygame.transform.smoothscale(
            character,(150,150)
        )
        r=img.get_rect(center=(200,215))
        screen.blit(img,r)

    pygame.draw.rect(
        screen,BLUE,play_btn,
        border_radius=15
    )
    text("PLAY",font,WHITE,200,330)

    pygame.draw.rect(
        screen,PURPLE,settings_btn,
        border_radius=15
    )
    text("SETTINGS",font,WHITE,200,402)

    text(
        "Unlocked: "+str(unlocked)+"/45",
        small,WHITE,200,470
    )

# =========================
# LEVEL SELECT
# =========================
def draw_levels():
    background()

    text(
        "SELECT LEVEL",
        big,GOLD,200,60
    )

    bw=58
    bh=45
    gx=12
    gy=12

    for n in range(1,46):
        i=n-1
        row=i//5
        col=i%5

        bx=22+col*(bw+gx)
        by=105+row*(bh+gy)

        r=pygame.Rect(bx,by,bw,bh)

        if n<=unlocked:
            color=GREEN
            label=str(n)
        else:
            color=GRAY
            label="X"

        pygame.draw.rect(
            screen,color,r,
            border_radius=9
        )

        text(
            label,small,WHITE,
            r.centerx,r.centery
        )

    pygame.draw.rect(
        screen,RED,back_btn,
        border_radius=9
    )
    text("BACK",small,WHITE,70,42)

# =========================
# SETTINGS SCREEN
# =========================
def draw_settings():
    background()

    text(
        "SETTINGS",
        big,GOLD,200,120
    )

    text(
        "MUSIC / SOUND",
        font,WHITE,200,230
    )

    text(
        "Tap sound enabled",
        small,WHITE,200,270
    )

    pygame.draw.rect(
        screen,RED,back_btn,
        border_radius=10
    )

    text("BACK",small,WHITE,70,42)

# =========================
# GAME SCREEN
# =========================
def draw_game():
    background()

    pygame.draw.rect(
        screen,(10,15,40),
        (0,0,400,125)
    )

    text(
        "LEVEL "+str(level),
        font,GOLD,200,27
    )

    text(
        "Score: "+str(score)+"/"+str(target),
        small,WHITE,75,70
    )

    text(
        "Coins: "+str(coins),
        small,GOLD,200,70
    )

    text(
        "Lives: "+str(lives),
        small,RED,330,70
    )

    tc=RED if timer<=5 else WHITE

    text(
        "TIME: "+str(timer),
        small,tc,200,105
    )

    draw_king()
    draw_particles()

    if ring>0:
        rr=20+(18-ring)*3

        pygame.draw.circle(
            screen,GOLD,
            (x,y),rr,3
        )

# =========================
# COMPLETE
# =========================
def draw_complete():
    background()

    text(
        "LEVEL",
        small,WHITE,200,90
    )

    text(
        "COMPLETE!",
        big,GOLD,200,140
    )

    if character_loaded:
        img=pygame.transform.smoothscale(
            character,(140,140)
        )
        r=img.get_rect(center=(200,245))
        screen.blit(img,r)

    text(
        "Level "+str(level),
        font,WHITE,200,350
    )

    text(
        "Score: "+str(score),
        font,WHITE,200,395
    )

    text(
        "Coins: "+str(coins),
        font,GOLD,200,440
    )

    if level<MAX_LEVEL:
        pygame.draw.rect(
            screen,GREEN,next_btn,
            border_radius=14
        )
        text(
            "NEXT LEVEL",
            font,WHITE,200,480
        )

    pygame.draw.rect(
        screen,BLUE,retry_btn,
        border_radius=14
    )
    text(
        "RETRY",
        font,WHITE,200,555
    )

    pygame.draw.rect(
        screen,PURPLE,menu_btn,
        border_radius=12
    )
    text(
        "MENU",
        small,WHITE,200,632
    )

# =========================
# GAME OVER
# =========================
def draw_gameover():
    background()

    text(
        "GAME OVER",
        big,RED,200,170
    )

    text(
        "Level "+str(level),
        font,WHITE,200,240
    )

    text(
        "Score: "+str(score),
        font,WHITE,200,285
    )

    pygame.draw.rect(
        screen,BLUE,retry_btn,
        border_radius=14
    )
    text(
        "RETRY",
        font,WHITE,200,555
    )

    pygame.draw.rect(
        screen,PURPLE,menu_btn,
        border_radius=12
    )
    text(
        "MENU",
        small,WHITE,200,632
    )

# =========================
# MAIN LOOP
# =========================
running=True

while running:

    dt=clock.tick(60)

    # TIMER
    if state=="game":
        elapsed=(
            pygame.time.get_ticks()
            -start_time
        )//1000

        timer=max(
            0,
            settings(level)[1]-elapsed
        )

        if timer<=0:
            lives=0
            state="gameover"
            play(wrong_sound)

    # ANIMATION
    if ring>0:
        ring-=1

    if scale>1:
        scale-=0.03
        if scale<1:
            scale=1

    update_particles()

    # EVENTS
    for event in pygame.event.get():

        if event.type==pygame.QUIT:
            running=False

        if event.type==pygame.KEYDOWN:

            if event.key==pygame.K_ESCAPE:
                if state!="menu":
                    state="menu"

        if event.type==pygame.MOUSEBUTTONDOWN:

            mx,my=event.pos

            # MENU
            if state=="menu":

                if play_btn.collidepoint(mx,my):
                    state="levels"

                elif settings_btn.collidepoint(mx,my):
                    state="settings"

            # SETTINGS
            elif state=="settings":

                if back_btn.collidepoint(mx,my):
                    state="menu"

            # LEVEL SELECT
            elif state=="levels":

                if back_btn.collidepoint(mx,my):
                    state="menu"

                else:
                    bw=58
                    bh=45
                    gx=12
                    gy=12

                    for n in range(1,46):

                        i=n-1
                        row=i//5
                        col=i%5

                        bx=22+col*(bw+gx)
                        by=105+row*(bh+gy)

                        r=pygame.Rect(
                            bx,by,bw,bh
                        )

                        if r.collidepoint(mx,my):
                            if n<=unlocked:
                                start_level(n)
                            break

            # GAME
            elif state=="game":

                dist=math.hypot(
                    mx-x,my-y
                )

                hit_radius=max(
                    30,size
                )

                if dist<=hit_radius:

                    score+=1
                    coins+=1

                    play(tap_sound)
                    play(coin_sound)

                    make_particles(18)

                    ring=18
                    scale=1.15

                    if score>=target:

                        play(complete_sound)

                        if level<MAX_LEVEL:
                            if unlocked<level+1:
                                unlocked=level+1
                                save_level(unlocked)

                        state="complete"

                    else:
                        move()

                else:
                    lives-=1
                    play(wrong_sound)

                    if lives<=0:
                        state="gameover"

            # COMPLETE
            elif state=="complete":

                if level<MAX_LEVEL and next_btn.collidepoint(mx,my):
                    start_level(level+1)

                elif retry_btn.collidepoint(mx,my):
                    start_level(level)

                elif menu_btn.collidepoint(mx,my):
                    state="menu"

            # GAME OVER
            elif state=="gameover":

                if retry_btn.collidepoint(mx,my):
                    start_level(level)

                elif menu_btn.collidepoint(mx,my):
                    state="menu"

    # DRAW
    if state=="menu":
        draw_menu()

    elif state=="levels":
        draw_levels()

    elif state=="settings":
        draw_settings()

    elif state=="game":
        draw_game()
    elif state=="complete" :
        draw_complete()

    elif state=="gameover":
        draw_gameover()

    pygame.display.flip()

pygame.quit()
