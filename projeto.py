import pgzrun
import random

#TAMANHO DA TELA
WIDTH = 800
HEIGHT = 600

#PERSONAGEM
player = Actor('player_idle')
player.x = 370
player.y = 550

#COIN
coin = Actor('coin_idle1')
coin.x = 450
coin.y = 550

#VARIAVEIS GLOBAIS
game_over = False
score = 0

# ANIMAÇÃO DO PLAYER (frames disponíveis na sua pasta images/)
idle_frames = ['player_idle', 'player_idle1', 'player_idle2', 'player_idle3']
run_frames = ['player_run1', 'player_run2', 'player_run3', 'player_run4']
jump_frames = ['player_jumping1', 'player_jumping2', 'player_jumping3', 'player_jumping4']

anim_state = 'idle'       # 'idle', 'run', 'jump'
anim_index = 0
anim_timer = 0
FRAME_DELAY = 5           # frames do jogo por troca de sprite
jump_anim_index = 0

# VARIAVEIS DE PULO
GROUND_Y = 550
is_jumping = False
vy = 0.0
JUMP_VELOCITY = -12.0
GRAVITY = 0.6

#PLATAFORMAS (mantive seu make_platform)
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

def skip():
    # força o estado de game over de qualquer ponto do jogo
    global game_over
    game_over = True

def update():
    global score, game_over, is_jumping, vy
    global anim_state, anim_index, anim_timer, jump_anim_index

    # se já for game over, não processa movimentação
    if game_over:
        return

    # atalho para "pular" e forçar game over
    if keyboard.k:
        skip()
        return

    # movimento horizontal
    moving = False
    if keyboard.a:
        player.x -= 5
        moving = True
    if keyboard.d:
        player.x += 5
        moving = True

    # iniciar pulo com Espaço (sem duplo pulo)
    if keyboard.space and not is_jumping:
        is_jumping = True
        vy = JUMP_VELOCITY
        jump_anim_index = 0
        anim_timer = 0

    # aplicar física do pulo quando estiver no ar
    if is_jumping:
        player.y += vy
        vy += GRAVITY
        # colisão com plataformas (só quando caindo)
        if vy > 0:
            for p in platforms:
                if player.colliderect(p):
                    player_bottom = player.y + player.height / 2
                    platform_top = p.y - p.height / 2
                    if player_bottom <= platform_top + 6:  # tolerância pequena
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
        # se não estiver pulando, verifica se ainda tem suporte (plataforma ou chão) abaixo
        standing = False
        player_bottom = player.y + player.height / 2
        for p in platforms:
            platform_top = p.y - p.height / 2
            # checa se estamos praticamente em cima da plataforma e dentro dos limites horizontais
            if abs(player_bottom - platform_top) <= 6:
                if (player.x > p.x - p.width / 2) and (player.x < p.x + p.width / 2):
                    standing = True
                    break
        # se não estiver em cima de nenhuma plataforma e não estiver no chão, começa a cair
        if not standing and player.y < GROUND_Y:
            is_jumping = True
            vy = 0.0

    # limitar jogador dentro da tela
    if player.x < 25:
        player.x = 25
    if player.x > WIDTH - 25:
        player.x = WIDTH - 25

    # colisão com coin
    if player.colliderect(coin):
        coin.x = random.randint(10, WIDTH - 10)
        score += 1
        coin.y = 550

    if score >= 10:
        game_over = True

    # --- lógica de animação (executa depois de mover e atualizar is_jumping) ---
    # decide estado
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
            player.image = idle_frames[anim_index]
    elif anim_state == 'run':
        if anim_timer >= FRAME_DELAY:
            anim_timer = 0
            anim_index = (anim_index + 1) % len(run_frames)
            player.image = run_frames[anim_index]
    elif anim_state == 'jump':
        # percorre frames de pulo enquanto estiver no ar (loop simples)
        if anim_timer >= FRAME_DELAY:
            anim_timer = 0
            jump_anim_index = min(jump_anim_index + 1, len(jump_frames) - 1)
        player.image = jump_frames[jump_anim_index]

def draw():
    screen.fill((80,0,70))
    player.draw()
    coin.draw()
    for p in platforms:
        p.draw()
    screen.draw.text('Score: ' + str(score), (15,10), color=(255,255,255), fontsize=30)

    if game_over:
        screen.draw.text('Game Over', (360, 300), color=(255,255,255), fontsize=60)
        screen.draw.text('Final Score: ' + str(score), (360, 350), color=(255,255,255), fontsize=60)

pgzrun.go()