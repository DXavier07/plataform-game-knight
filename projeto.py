import pgzrun
import random

#TAMANHO DA TELA
WIDTH = 800
HEIGHT = 600

#PERSONAGEM
player = Actor('player_idle')  # removido .png (pgzero usa nome do recurso)
player.x = 370
player.y = 550

#COIN
coin = Actor('coin_idle1')
coin.x = 450
coin.y = 550

#VARIAVEIS GLOBAIS
game_over = False
score = 0

def update():
    global score, game_over
    if keyboard.a:
        player.x -= 5
    if keyboard.d:
        player.x += 5

    if player.colliderect(coin):
        coin.x = random.randint(10, WIDTH - 10)
        score += 1
        coin.y = 550

    if score >= 10:
        game_over = True

def draw():
    screen.fill((80,0,70))
    player.draw()
    coin.draw()
    screen.draw.text('Score: ' + str(score), (15,10), color=(255,255,255), fontsize=30)

    if game_over:
        screen.draw.text('Game Over', (360, 300), color=(255,255,255), fontsize=60)
        # skip.draw() removido porque 'skip' não está definido
        screen.draw.text('Final Score: ' + str(score), (360, 350), color=(255,255,255), fontsize=60)

pgzrun.go()