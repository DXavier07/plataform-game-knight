import pgzrun
import random
import os
import sys

# TAMANHO DA TELA
WIDTH = 800
HEIGHT = 600

# caminhos: resolve images de forma robusta (prioriza pasta junto ao script, depois cwd, depois argv[0])
_IMAGE_DIR = None
_candidates = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images'),
    os.path.join(os.getcwd(), 'images'),
    os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'images'),
]
for _c in _candidates:
    if os.path.isdir(_c):
        _IMAGE_DIR = _c
        break
if _IMAGE_DIR is None:
    print("ERROR: pasta 'images' não encontrada. Caminhos testados:")
    for p in _candidates:
        print("  -", p)
    sys.exit(1)

# FRAMES DO PLAYER
idle_frames = ['player_idle', 'player_idle1', 'player_idle2', 'player_idle3']
run_frames = ['player_run1', 'player_run2', 'player_run3', 'player_run4']
jump_frames = ['player_jumping1', 'player_jumping2', 'player_jumping3', 'player_jumping4']

def frame_for_direction(frame_name, facing):
    """
    Retorna "<frame>_left" se facing == -1 e o arquivo existir,
    caso contrário encerra o jogo (exit) para facilitar teste.
    Adiciona prints de debug (apenas na primeira chamada) e
    mostra a checagem para cada frame pedido.
    """
    global _IMAGE_DIR
    # imprime debug da pasta e arquivos só na primeira chamada
    if not globals().get('_frame_debug_printed'):
        try:
            files = sorted(os.listdir(_IMAGE_DIR))
        except Exception as e:
            print("ERROR: não consegui listar _IMAGE_DIR:", _IMAGE_DIR, "->", e)
            sys.exit(1)
        print("DEBUG: _IMAGE_DIR =", os.path.abspath(_IMAGE_DIR))
        print("DEBUG: imagens disponíveis:", files)
        globals()['_frame_debug_printed'] = True

    if facing == -1:
        left = frame_name + '_left'
        left_path = os.path.join(_IMAGE_DIR, left + '.png')
        exists = os.path.isfile(left_path)
        print(f"DEBUG: procurando left sprite for '{frame_name}': {left_path} -> exists={exists}")
        if exists:
            return left
        # não encontrou: imprime caminho esperado e encerra para teste
        print(f"ERROR: left sprite not found for '{frame_name}'. Expected: {left_path}")
        sys.exit(1)
    return frame_name

# PERSONAGEM
player = Actor('player_idle')
player.x = 370
player.y = 550

# COIN
coin = Actor('coin_idle1')
coin.x = 450
coin.y = 550

# VARIAVEIS GLOBAIS
game_over = False
score = 0

# ANIMAÇÃO E PULO
anim_state = 'idle'     # 'idle', 'run', 'jump'
anim_index = 0
anim_timer = 0
FRAME_DELAY = 12   # mais lento
jump_anim_index = 0

GROUND_Y = 550
is_jumping = False
vy = 0.0
JUMP_VELOCITY = -12.0
GRAVITY = 0.6

# MOEDA
coin_frames = ['coin_idle1', 'coin_idle2', 'coin_idle3', 'coin_idle4']
coin_anim_index = 0
coin_anim_timer = 0
COIN_FRAME_DELAY = 12  # mais lento

# PLATAFORMAS (Actors simples)
def make_platform(x, y, image):
    p = Actor(image)
    p.x = x
    p.y = y
    return p

platforms = [
    make_platform(150, 500, 'platform1'),
    make_platform(400, 520, 'platform2'),
    make_platform(600, 480, 'platform3'),
    make_platform(300, 460, 'platform4'),
]

# 1 = right, -1 = left
facing = 1

def skip():
    global game_over
    game_over = True

def update():
    global score, game_over, is_jumping, vy, facing
    global anim_state, anim_index, anim_timer, jump_anim_index
    global coin_anim_index, coin_anim_timer

    if game_over:
        return

    if keyboard.k:
        skip()
        return

    # MOVIMENTO HORIZONTAL (A/D ou setas)
    moving = False
    if keyboard.a or keyboard.left:
        player.x -= 5
        moving = True
        facing = -1
    elif keyboard.d or keyboard.right:
        player.x += 5
        moving = True
        facing = 1

    # INICIAR PULO
    if keyboard.space and not is_jumping:
        is_jumping = True
        vy = JUMP_VELOCITY
        jump_anim_index = 0
        anim_timer = 0

    # FISICA DO PULO
    if is_jumping:
        player.y += vy
        vy += GRAVITY

        # colisão com plataformas (apenas ao descer)
        if vy > 0:
            for p in platforms:
                if player.colliderect(p):
                    player_bottom = player.y + player.height / 2
                    platform_top = p.y - p.height / 2
                    if player_bottom <= platform_top + 6:
                        player.y = platform_top - player.height / 2
                        is_jumping = False
                        vy = 0.0
                        jump_anim_index = 0
                        break

        # aterrissagem no chão
        if player.y >= GROUND_Y:
            player.y = GROUND_Y
            is_jumping = False
            vy = 0.0
            jump_anim_index = 0
    else:
        # verifica suporte (plataformas ou chão); se saiu da plataforma começa a cair
        standing = False
        player_bottom = player.y + player.height / 2
        for p in platforms:
            platform_top = p.y - p.height / 2
            if abs(player_bottom - platform_top) <= 6:
                if (player.x > p.x - p.width / 2) and (player.x < p.x + p.width / 2):
                    standing = True
                    break
        if not standing and player.y < GROUND_Y:
            is_jumping = True
            vy = 0.0

    # LIMITES HORIZONTAIS
    if player.x < 25:
        player.x = 25
    if player.x > WIDTH - 25:
        player.x = WIDTH - 25

    # COLISÃO COM MOEDA
    if player.colliderect(coin):
        coin.x = random.randint(10, WIDTH - 10)
        coin.y = 550
        score += 1

    if score >= 10:
        game_over = True

    # ANIMAÇÃO DO PLAYER
    if is_jumping:
        anim_state = 'jump'
    elif moving:
        anim_state = 'run'
    else:
        anim_state = 'idle'

    anim_timer += 1
    if anim_state == 'idle':
        if anim_timer >= FRAME_DELAY:
            anim_timer = 0
            anim_index = (anim_index + 1) % len(idle_frames)
        base_frame = idle_frames[anim_index]
    elif anim_state == 'run':
        if anim_timer >= FRAME_DELAY:
            anim_timer = 0
            anim_index = (anim_index + 1) % len(run_frames)
        base_frame = run_frames[anim_index]
    else:  # jump
        if anim_timer >= FRAME_DELAY:
            anim_timer = 0
            jump_anim_index = min(jump_anim_index + 1, len(jump_frames) - 1)
        base_frame = jump_frames[jump_anim_index]

    # usa versão "_left" se existir e estivermos virados para a esquerda
    player.image = frame_for_direction(base_frame, facing)

    # ANIMAÇÃO DA MOEDA
    coin_anim_timer += 1
    if coin_anim_timer >= COIN_FRAME_DELAY:
        coin_anim_timer = 0
        coin_anim_index = (coin_anim_index + 1) % len(coin_frames)
        coin.image = coin_frames[coin_anim_index]

def draw():
    screen.fill((80,0,70))
    for p in platforms:
        p.draw()
    player.draw()
    coin.draw()
    screen.draw.text('Score: ' + str(score), (15,10), color=(255,255,255), fontsize=30)

    if game_over:
        screen.draw.text('Game Over', (360, 300), color=(255,255,255), fontsize=60)
        screen.draw.text('Final Score: ' + str(score), (360, 350), color=(255,255,255), fontsize=60)

pgzrun.go()