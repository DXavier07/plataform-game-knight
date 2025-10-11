import pgzrun
import random
import os
import sys

WIDTH, HEIGHT = 800, 600

# images directory
_script_images = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
_cwd_images = os.path.join(os.getcwd(), 'images')
_IMAGE_DIR = _script_images if os.path.isdir(_script_images) else (_cwd_images if os.path.isdir(_cwd_images) else None)
if _IMAGE_DIR is None:
    print("ERROR: pasta 'images' não encontrada. Verifique onde estão os PNGs.")
    sys.exit(1)

idle_frames = ['player_idle', 'player_idle1', 'player_idle2', 'player_idle3']
run_frames = ['player_run1', 'player_run2', 'player_run3', 'player_run4']
jump_frames = ['player_jumping1', 'player_jumping2', 'player_jumping3', 'player_jumping4']

def frame_for_direction(name, facing):
    if facing == -1:
        cand = name + '_left'
        if os.path.isfile(os.path.join(_IMAGE_DIR, cand + '.png')):
            return cand
    return name

player = Actor('player_idle', (370, 550))

game_over = False
score = 0

anim_state = 'idle'
anim_index = anim_timer = 0
jump_anim_index = 0

GROUND_Y = 550
is_jumping = False
vy = 0.0
JUMP_VELOCITY = -12.0
GRAVITY = 0.6

# --- MOEDAS FIXAS ---
coin_positions = [
    (150, 500), (250, 450), (350, 400), (450, 350), (550, 300),
    (650, 250), (750, 200), (100, 350), (300, 300), (500, 250)
]
coins = [Actor('coin_idle1', pos=pos) for pos in coin_positions]
coin_frames = ['coin_idle1', 'coin_idle2', 'coin_idle3', 'coin_idle4']
coin_anim_index = coin_anim_timer = 0
COIN_FRAME_DELAY = 12

# --- PLATAFORMAS ---
PLATFORM_IMAGES = ['platform1', 'platform3']  # verde e amarelo
FLOOR_SPACING = 90
FLOORS = 5

def build_platforms(seed=None):
    rng = random.Random(0)
    sample = Actor(PLATFORM_IMAGES[0])
    tile_w, tile_h = sample.width, sample.height

    plats = []

    # chão principal
    for i in range(0, WIDTH, tile_w):
        plats.append(Actor('platform1', (i + tile_w // 2, GROUND_Y)))

    # gera linhas de plataformas intercaladas
    for floor in range(1, FLOORS + 1):
        y = GROUND_Y - floor * FLOOR_SPACING
        platform_type = PLATFORM_IMAGES[floor % 2]

        group_count = 3 if floor % 2 == 0 else 4
        x_positions = [rng.randint(60, WIDTH - 200) for _ in range(group_count)]

        for x_start in x_positions:
            length = rng.randint(3, 5)
            for i in range(length):
                x = x_start + i * tile_w
                plats.append(Actor(platform_type, (x, y)))

    return plats

platforms = build_platforms()

# --- MONSTROS ---
monster_frames = {
    'm1': ['monster1_run', 'monster1_run2', 'monster1_run3', 'monster1_run4'],
    'm2': ['monster2_run', 'monster2_run2', 'monster2_run3', 'monster2_run4'],
}
monsters = []

levels = {}
for p in platforms:
    ly = int(round(p.y / 4) * 4)
    levels.setdefault(ly, []).append(p)

rows = sorted([ly for ly in levels.keys() if ly >= 100])
sel_rows = rows[1::2][:3]
for idx, ly in enumerate(sel_rows):
    lvl = levels[ly]
    xs = sorted(p.x for p in lvl)
    min_x = max(40, int(min(xs) - 30))
    max_x = min(WIDTH - 40, int(max(xs) + 30))
    y = int(sum(p.y for p in lvl) / len(lvl)) - 20
    mtype = 'm1' if idx % 2 == 0 else 'm2'
    frames = monster_frames[mtype]
    monsters.append({
        'actor': Actor(frames[0], ((min_x + max_x) // 2, y)),
        'frames': frames, 'idx': 0, 'timer': 0, 'delay': 12 + idx * 2,
        'dir': -1 if idx % 2 else 1, 'speed': 1.0 + idx * 0.3,
        'min_x': min_x, 'max_x': max_x
    })

facing = 1

def update():
    global game_over, score, is_jumping, vy, facing
    global anim_state, anim_index, anim_timer, jump_anim_index
    global coin_anim_index, coin_anim_timer

    if game_over:
        return
    if keyboard.k:
        game_over = True
        return

    moving = False
    if keyboard.a or keyboard.left:
        player.x -= 5; moving = True; facing = -1
    elif keyboard.d or keyboard.right:
        player.x += 5; moving = True; facing = 1

    if keyboard.space and not is_jumping:
        is_jumping = True; vy = JUMP_VELOCITY; jump_anim_index = 0; anim_timer = 0

    if is_jumping:
        player.y += vy; vy += GRAVITY
        if vy > 0:
            for p in platforms:
                if player.colliderect(p):
                    pb = player.y + player.height/2
                    pt = p.y - p.height/2
                    if pb <= pt + 6:
                        player.y = pt - player.height/2
                        is_jumping = False; vy = 0.0; jump_anim_index = 0
                        break
        if player.y >= GROUND_Y:
            player.y = GROUND_Y; is_jumping = False; vy = 0.0; jump_anim_index = 0
    else:
        standing = False
        pb = player.y + player.height/2
        for p in platforms:
            pt = p.y - p.height/2
            if abs(pb - pt) <= 6 and (player.x > p.x - p.width/2) and (player.x < p.x + p.width/2):
                standing = True; break
        if not standing and player.y < GROUND_Y:
            is_jumping = True; vy = 0.0

    player.x = max(25, min(WIDTH - 25, player.x))

    # --- COLETA DE MOEDAS ---
    for c in coins[:]:
        if player.colliderect(c):
            coins.remove(c)
            score += 1

    if score >= 10:
        game_over = True

    # --- ANIMAÇÃO DO PLAYER ---
    anim_state = 'jump' if is_jumping else ('run' if moving else 'idle')
    anim_timer += 1
    if anim_state == 'idle':
        if anim_timer >= 12: anim_timer = 0; anim_index = (anim_index + 1) % len(idle_frames)
        base = idle_frames[anim_index]
    elif anim_state == 'run':
        if anim_timer >= 12: anim_timer = 0; anim_index = (anim_index + 1) % len(run_frames)
        base = run_frames[anim_index]
    else:
        if anim_timer >= 12: anim_timer = 0; jump_anim_index = min(jump_anim_index + 1, len(jump_frames)-1)
        base = jump_frames[jump_anim_index]

    player.image = frame_for_direction(base, facing)

    # --- MONSTROS ---
    for m in monsters:
        a = m['actor']
        a.x += m['speed'] * m['dir']
        if a.x <= m['min_x']:
            a.x = m['min_x']; m['dir'] = 1
        elif a.x >= m['max_x']:
            a.x = m['max_x']; m['dir'] = -1
        m['timer'] += 1
        if m['timer'] >= m['delay']:
            m['timer'] = 0; m['idx'] = (m['idx'] + 1) % len(m['frames'])
        cur_frame = m['frames'][m['idx']]
        a.image = frame_for_direction(cur_frame, -1 if m['dir'] < 0 else 1)

    # --- ANIMAÇÃO DAS MOEDAS ---
    coin_anim_timer += 1
    if coin_anim_timer >= COIN_FRAME_DELAY:
        coin_anim_timer = 0
        coin_anim_index = (coin_anim_index + 1) % len(coin_frames)
        for c in coins:
            c.image = coin_frames[coin_anim_index]

def draw():
    screen.fill((80, 0, 70))
    for p in platforms:
        p.draw()
    for m in monsters:
        m['actor'].draw()
    player.draw()
    for c in coins:
        c.draw()
    screen.draw.text(f"Score: {score}", (15, 10), color="white", fontsize=30)
    if game_over:
        screen.draw.text("Game Over", (WIDTH // 2 - 80, HEIGHT // 2 - 20), color="white", fontsize=48)
        screen.draw.text(f"Final Score: {score}", (WIDTH // 2 - 80, HEIGHT // 2 + 30), color="white", fontsize=28)

pgzrun.go()
