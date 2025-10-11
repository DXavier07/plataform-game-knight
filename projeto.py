import pgzrun
import random
import os
import sys

WIDTH, HEIGHT = 800, 600

# images directory (script dir first, depois cwd)
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
coin = Actor('coin_idle1', (450, 550))

game_over = False
score = 0

anim_state = 'idle'
anim_index = anim_timer = 0
FRAME_DELAY = 14
jump_anim_index = 0

GROUND_Y = 550
is_jumping = False
vy = 0.0
JUMP_VELOCITY = -12.0
GRAVITY = 0.6

coin_frames = ['coin_idle1', 'coin_idle2', 'coin_idle3', 'coin_idle4']
coin_anim_index = coin_anim_timer = 0
COIN_FRAME_DELAY = 14

platforms = [
    Actor('platform1', (150, 500)),
    Actor('platform2', (400, 520)),
    Actor('platform3', (600, 480)),
    Actor('platform4', (300, 460)),
]

# --- monsters: frames, instâncias e parâmetros de movimento/anim ---
monster_frames = {
    'm1': ['monster1_run', 'monster1_run2', 'monster1_run3', 'monster1_run4'],
    'm2': ['monster2_run', 'monster2_run2', 'monster2_run3', 'monster2_run4'],
}
monsters = [
    # monster1 patrulha entre 100..350
    {'actor': Actor(monster_frames['m1'][0], (220, 520)),
     'frames': monster_frames['m1'], 'idx': 0, 'timer': 0, 'delay': 12,
     'dir': 1, 'speed': 1.2, 'min_x': 100, 'max_x': 350},
    # monster2 patrulha entre 500..750
    {'actor': Actor(monster_frames['m2'][0], (620, 500)),
     'frames': monster_frames['m2'], 'idx': 0, 'timer': 0, 'delay': 14,
     'dir': -1, 'speed': 1.0, 'min_x': 500, 'max_x': 750},
]

facing = 1  # 1=right, -1=left

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

    if player.colliderect(coin):
        coin.x = random.randint(10, WIDTH - 10); coin.y = 550; score += 1
    if score >= 10:
        game_over = True

    anim_state = 'jump' if is_jumping else ('run' if moving else 'idle')
    anim_timer += 1
    if anim_state == 'idle':
        if anim_timer >= FRAME_DELAY: anim_timer = 0; anim_index = (anim_index + 1) % len(idle_frames)
        base = idle_frames[anim_index]
    elif anim_state == 'run':
        if anim_timer >= FRAME_DELAY: anim_timer = 0; anim_index = (anim_index + 1) % len(run_frames)
        base = run_frames[anim_index]
    else:
        if anim_timer >= FRAME_DELAY: anim_timer = 0; jump_anim_index = min(jump_anim_index + 1, len(jump_frames)-1)
        base = jump_frames[jump_anim_index]

    player.image = frame_for_direction(base, facing)

    # --- animate & move monsters ---
    for m in monsters:
        a = m['actor']
        # move and clamp / reverse direction
        a.x += m['speed'] * m['dir']
        if a.x <= m['min_x']:
            a.x = m['min_x']; m['dir'] = 1
        elif a.x >= m['max_x']:
            a.x = m['max_x']; m['dir'] = -1
        # animation timer
        m['timer'] += 1
        if m['timer'] >= m['delay']:
            m['timer'] = 0
            m['idx'] = (m['idx'] + 1) % len(m['frames'])
        # set frame; use frame_for_direction so "<frame>_left" is used if present
        cur_frame = m['frames'][m['idx']]
        a.image = frame_for_direction(cur_frame, -1 if m['dir'] < 0 else 1)

    coin_anim_timer += 1
    if coin_anim_timer >= COIN_FRAME_DELAY:
        coin_anim_timer = 0
        coin_anim_index = (coin_anim_index + 1) % len(coin_frames)
        coin.image = coin_frames[coin_anim_index]

def draw():
    screen.fill((80,0,70))
    for p in platforms: p.draw()
    for m in monsters: m['actor'].draw()
    player.draw(); coin.draw()
    screen.draw.text(f"Score: {score}", (15,10), color="white", fontsize=30)
    if game_over:
        screen.draw.text("Game Over", (360,300), color="white", fontsize=60)
        screen.draw.text(f"Final Score: {score}", (360,350), color="white", fontsize=40)

pgzrun.go()