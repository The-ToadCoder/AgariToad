import random, sys, time, math, pygame
from pygame.locals import *
from lib.scr.msg.devMsg import *
from lib.scr.webLinks import *
from lib.config.config import *

HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)
#Add more colors later + some game sound effects
GRASSCOLOR = (24, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GRAY = (95, 95, 95)

CAMERASLACK = 90
GAMEOVERTIME = 4
INVULNTIME = 2
LEFT = 'left'
RIGHT = 'right'
fontPath = 'assets/fonts/'
imgPath = 'assets/imgs/'
soundPath = 'assets/sounds/'
print(MSG)


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, SCOREFONT, L_TOAD_IMG, R_TOAD_IMG, GRASSIMAGES, winSound, loseSound, hurtSound, collectSound

    pygame.init()
    winSound = pygame.mixer.Sound(soundPath + "Win.wav")
    loseSound = pygame.mixer.Sound(soundPath + "Lose.wav")
    hurtSound = pygame.mixer.Sound(soundPath + "hurt.wav")
    collectSound = pygame.mixer.Sound(soundPath + "crunch.wav")
    pygame.mixer.music.load(soundPath + 'backgroundMusic.wav')
    pygame.mixer.music.play(-1)
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_icon(pygame.image.load(imgPath + 'gameicon.png'))
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    pygame.display.set_caption('AgariToad')
    BASICFONT = pygame.font.Font(fontPath + 'upheavtt.ttf', 50)
    SCOREFONT = pygame.font.Font(fontPath + '3Dventure.ttf', 24)

    L_TOAD_IMG = pygame.image.load(imgPath + 'toad.png')
    R_TOAD_IMG = pygame.transform.flip(L_TOAD_IMG, True, False)
    GRASSIMAGES = []
    for i in range(1, 6):
        GRASSIMAGES.append(pygame.image.load(imgPath + 'grass%s.png' % i))

    while True:
        runGame()


def runGame():
    global SCORECOUNTER

    #Easy Way to Change the Point Counting system
    POINTSPERTOAD = 1
    SCORECOUNTER = 0
    invulnerableMode = False
    invulnerableStartTime = 0
    gameOverMode = False
    gameOverStartTime = 0
    winMode = False

    #BG text is for the back ground text for creating a cooler text style in-game
    gameOverSurf = BASICFONT.render('Game Over', True, WHITE)
    gameOverRect = gameOverSurf.get_rect()
    gameOverRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    BGgameOverSurf = BASICFONT.render('Game Over', True, BLACK)
    BGgameOverRect = BGgameOverSurf.get_rect()
    BGgameOverRect.center = (HALF_WINWIDTH + 3, HALF_WINHEIGHT + 3)

    winSurf = BASICFONT.render('Goliath Toad Achieved', True, WHITE)
    winRect = winSurf.get_rect()
    winRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT - 14)

    BGwinSurf = BASICFONT.render('Goliath Toad Achieved', True, BLACK)
    BGwinRect = BGwinSurf.get_rect()
    BGwinRect.center = (HALF_WINWIDTH + 3, HALF_WINHEIGHT - 11)

    winSurf2 = BASICFONT.render('(Press "r" to Restart)', True, WHITE)
    winRect2 = winSurf2.get_rect()
    winRect2.center = (HALF_WINWIDTH, HALF_WINHEIGHT + 20)

    BGwinSurf2 = BASICFONT.render('(Press "r" to Restart)', True, BLACK)
    BGwinRect2 = BGwinSurf2.get_rect()
    BGwinRect2.center = (HALF_WINWIDTH + 3, HALF_WINHEIGHT + 23)

    cameraX = 0
    cameraY = 0

    grassObjs = []
    toadObjs = []
    playerObj = {
        'surface': pygame.transform.scale(L_TOAD_IMG, (STARTSIZE, STARTSIZE)),
        'faceing': LEFT,
        'size': STARTSIZE,
        'x': HALF_WINWIDTH,
        'y': HALF_WINHEIGHT,
        'bounce': 0,
        'health': MAXHEALTH
    }

    moveLeft = False
    moveRight = False
    moveUp = False
    moveDown = False

    for i in range(10):
        grassObjs.append(makeNewGrass(cameraX, cameraY))
        grassObjs[i]['x'] = random.randint(0, WINWIDTH)
        grassObjs[i]['y'] = random.randint(0, WINHEIGHT)

    while True:
        if invulnerableMode and time.time(
        ) - invulnerableStartTime > INVULNTIME:
            invulnerableMode = False

        for tObj in toadObjs:
            tObj['x'] += tObj['movex']
            tObj['y'] += tObj['movey']
            tObj['bounce'] += 1
            if tObj['bounce'] > tObj['bouncerate']:
                tObj['bounce'] = 0
            if random.randint(0, 99) < DIRCHANGEFREQ:
                tObj['movex'] = getRandomVelocity()
                tObj['movey'] = getRandomVelocity()
                if tObj['movex'] > 0:
                    tObj['surface'] = pygame.transform.scale(
                        R_TOAD_IMG, (tObj['width'], tObj['height']))
                else:
                    tObj['surface'] = pygame.transform.scale(
                        L_TOAD_IMG, (tObj['width'], tObj['height']))

        for i in range(len(grassObjs) - 1, -1, -1):
            if isOutsideActiveArea(cameraX, cameraY, grassObjs[i]):
                del grassObjs[i]
        for i in range(len(toadObjs) - 1, -1, -1):
            if isOutsideActiveArea(cameraX, cameraY, toadObjs[i]):
                del toadObjs[i]

        while len(grassObjs) < NUMGRASS:
            grassObjs.append(makeNewGrass(cameraX, cameraY))
        while len(toadObjs) < NUMTOADS:
            toadObjs.append(makeNewToad(cameraX, cameraY))

        playerCenterX = playerObj['x'] + int(playerObj['size'] / 2)
        playerCenterY = playerObj['y'] + int(playerObj['size'] / 2)
        if (cameraX + HALF_WINWIDTH) - playerCenterX > CAMERASLACK:
            cameraX = playerCenterX + CAMERASLACK - HALF_WINWIDTH
        elif playerCenterX - (cameraX + HALF_WINWIDTH) > CAMERASLACK:
            cameraX = playerCenterX - CAMERASLACK - HALF_WINWIDTH
        if (cameraY + HALF_WINHEIGHT) - playerCenterY > CAMERASLACK:
            cameraY = playerCenterY + CAMERASLACK - HALF_WINHEIGHT
        elif playerCenterY - (cameraY + HALF_WINHEIGHT) > CAMERASLACK:
            cameraY = playerCenterY - CAMERASLACK - HALF_WINHEIGHT

        DISPLAYSURF.fill(GRASSCOLOR)

        for gObj in grassObjs:
            gRect = pygame.Rect((gObj['x'] - cameraX, gObj['y'] - cameraY,
                                 gObj['width'], gObj['height']))
            DISPLAYSURF.blit(GRASSIMAGES[gObj['grassImage']], gRect)

        for tObj in toadObjs:
            tObj['rect'] = pygame.Rect(
                (tObj['x'] - cameraX, tObj['y'] - cameraY - getBounceAmount(
                    tObj['bounce'], tObj['bouncerate'], tObj['bounceheight']),
                 tObj['width'], tObj['height']))
            DISPLAYSURF.blit(tObj['surface'], tObj['rect'])

        flashIsOn = round(time.time(), 1) * 10 % 2 == 1
        if not gameOverMode and not (invulnerableMode and flashIsOn):
            playerObj['rect'] = pygame.Rect((
                playerObj['x'] - cameraX, playerObj['y'] - cameraY -
                getBounceAmount(playerObj['bounce'], BOUNCERATE, BOUNCEHEIGHT),
                playerObj['size'], playerObj['size']))
            DISPLAYSURF.blit(playerObj['surface'], playerObj['rect'])

        drawScoreBox()
        drawHealthMeter(playerObj['health'])

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key in (K_UP, K_w):
                    moveDown = False
                    moveUp = True
                elif event.key in (K_DOWN, K_s):
                    moveUp = False
                    moveDown = True
                elif event.key in (K_LEFT, K_a):
                    moveRight = False
                    moveLeft = True
                    if playerObj['faceing'] == RIGHT:
                        playerObj['surface'] = pygame.transform.scale(
                            L_TOAD_IMG, (playerObj['size'], playerObj['size']))
                    playerObj['faceing'] = LEFT
                elif event.key in (K_RIGHT, K_d):
                    moveLeft = False
                    moveRight = True
                    if playerObj['faceing'] == LEFT:
                        playerObj['surface'] = pygame.transform.scale(
                            R_TOAD_IMG, (playerObj['size'], playerObj['size']))
                    playerObj['faceing'] = RIGHT
                elif event.key == K_n:
                    SCORECOUNTER = 0
                    return

            elif event.type == KEYUP:
                if event.key in (K_LEFT, K_a):
                    moveLeft = False
                elif event.key in (K_RIGHT, K_d):
                    moveRight = False
                elif event.key in (K_UP, K_w):
                    moveUp = False
                elif event.key in (K_DOWN, K_s):
                    moveDown = False

                elif event.key == K_ESCAPE:
                    terminate()

        if not gameOverMode:
            scorecounterdisplay(str(SCORECOUNTER))
            if moveLeft:
                playerObj['x'] -= MOVERATE
            if moveRight:
                playerObj['x'] += MOVERATE
            if moveUp:
                playerObj['y'] -= MOVERATE
            if moveDown:
                playerObj['y'] += MOVERATE

            if (moveLeft or moveRight or moveUp
                    or moveDown) or playerObj['bounce'] != 0:
                playerObj['bounce'] += 1
            if playerObj['bounce'] > BOUNCERATE:
                playerObj['bounce'] = 0

            for i in range(len(toadObjs) - 1, -1, -1):
                tdObj = toadObjs[i]
                if 'rect' in tdObj and playerObj['rect'].colliderect(
                        tdObj['rect']):
                    if tdObj['width'] * tdObj['height'] <= playerObj['size']**2:
                        playerObj['size'] += int(
                            (tdObj['width'] * tdObj['height'])**0.2) + 1
                        pygame.mixer.Sound.play(collectSound)
                        SCORECOUNTER += POINTSPERTOAD
                        del toadObjs[i]

                        if playerObj['faceing'] == LEFT:
                            playerObj['surface'] = pygame.transform.scale(
                                L_TOAD_IMG,
                                (playerObj['size'], playerObj['size']))
                        if playerObj['faceing'] == RIGHT:
                            playerObj['surface'] = pygame.transform.scale(
                                R_TOAD_IMG,
                                (playerObj['size'], playerObj['size']))

                        if playerObj['size'] > WINSIZE:
                            winMode = True

                    elif not invulnerableMode:
                        invulnerableMode = True
                        invulnerableStartTime = time.time()
                        pygame.mixer.Sound.play(hurtSound)
                        playerObj['health'] -= 1
                        if playerObj['health'] == 0:
                            pygame.mixer.Sound.play(loseSound)
                            gameOverMode = True
                            gameOverStartTime = time.time()
        else:
            pygame.draw.rect(DISPLAYSURF, BLACK, (0, 194, 680, 96))
            pygame.draw.rect(DISPLAYSURF, GRAY, (0, 196, 680, 92))
            DISPLAYSURF.blit(BGgameOverSurf, BGgameOverRect)
            DISPLAYSURF.blit(gameOverSurf, gameOverRect)
            writePlayerScore(str(SCORECOUNTER))
            if time.time() - gameOverStartTime > GAMEOVERTIME:
                SCORECOUNTER = 0
                return

        if winMode:
            pygame.draw.rect(DISPLAYSURF, BLACK, (0, 180, 680, 110))
            pygame.draw.rect(DISPLAYSURF, GRAY, (0, 182, 680, 106))
            pygame.mixer.Sound.play(winSound)
            writePlayerScore(str(SCORECOUNTER))
            drawScoreBox()
            while winMode:
                #Background text displays 1st
                DISPLAYSURF.blit(BGwinSurf, BGwinRect)
                DISPLAYSURF.blit(BGwinSurf2, BGwinRect2)
                #Main text displays 2nd
                DISPLAYSURF.blit(winSurf, winRect)
                DISPLAYSURF.blit(winSurf2, winRect2)
                for event in pygame.event.get():
                    if event.type == QUIT:
                        terminate()
                    elif event.type == KEYDOWN:
                        if event.key == K_r:
                            SCORECOUNTER = 0
                            return
                    elif event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            terminate()
                pygame.display.update()
                FPSCLOCK.tick(FPS)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def scorecounterdisplay(score):
    scoreCounterSurf = SCOREFONT.render(score, True, BLACK)
    scoreCounterRect = scoreCounterSurf.get_rect()
    scoreCounterRect.center = (645, 17)
    DISPLAYSURF.blit(scoreCounterSurf, scoreCounterRect)


def drawScoreBox():
    pygame.draw.rect(DISPLAYSURF, BLACK, (620, 5, 49, 24))
    pygame.draw.rect(DISPLAYSURF, WHITE, (622, 7, 45, 20))


def writePlayerScore(score):
    scoreboardSurf = BASICFONT.render('Toads Eaten: ' + score, True, WHITE)
    scoreboardRect = scoreboardSurf.get_rect()
    scoreboardRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT + 54)

    BGscoreboardSurf = BASICFONT.render('Toads Eaten: ' + score, True, BLACK)
    BGscoreboardRect = BGscoreboardSurf.get_rect()
    BGscoreboardRect.center = (HALF_WINWIDTH + 3, HALF_WINHEIGHT + 57)
    DISPLAYSURF.blit(BGscoreboardSurf, BGscoreboardRect)
    DISPLAYSURF.blit(scoreboardSurf, scoreboardRect)


def drawHealthMeter(currentHealth):
    for i in range(currentHealth):
        pygame.draw.rect(DISPLAYSURF, RED,
                         (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10))
    for i in range(MAXHEALTH):
        pygame.draw.rect(DISPLAYSURF, BLACK,
                         (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10), 1)


def terminate():
    pygame.quit()
    sys.exit()


def getBounceAmount(currentBounce, bounceRate, bounceHeight):
    return int(
        math.sin((math.pi / float(bounceRate)) * currentBounce) * bounceHeight)


def getRandomVelocity():
    speed = random.randint(TOADMINSPEED, TOADMAXSPEED)
    if random.randint(0, 1) == 0:
        return speed
    else:
        return -speed


def getRandomOffCameraPos(cameraX, cameraY, objWidth, objHeight):
    cameraRect = pygame.Rect(cameraX, cameraY, WINWIDTH, WINHEIGHT)
    while True:
        x = random.randint(cameraX - WINWIDTH, cameraX + (2 * WINWIDTH))
        y = random.randint(cameraY - WINHEIGHT, cameraY + (2 * WINHEIGHT))
        objRect = pygame.Rect(x, y, objWidth, objHeight)
        if not objRect.colliderect(cameraRect):
            return x, y


def makeNewToad(cameraX, cameraY):
    td = {}
    generalSize = random.randint(5, 25)
    multiplier = random.randint(1, 3)
    td['width'] = (generalSize + random.randint(0, 10)) * multiplier
    td['height'] = (generalSize + random.randint(0, 10)) * multiplier
    td['x'], td['y'] = getRandomOffCameraPos(cameraX, cameraY, td['width'],
                                             td['height'])
    td['movex'] = getRandomVelocity()
    td['movey'] = getRandomVelocity()
    if td['movex'] < 0:
        td['surface'] = pygame.transform.scale(L_TOAD_IMG,
                                               (td['width'], td['height']))
    else:
        td['surface'] = pygame.transform.scale(R_TOAD_IMG,
                                               (td['width'], td['height']))
    td['bounce'] = 0
    td['bouncerate'] = random.randint(10, 18)
    td['bounceheight'] = random.randint(10, 50)
    return td


def makeNewGrass(cameraX, cameraY):
    gr = {}
    gr['grassImage'] = random.randint(0, len(GRASSIMAGES) - 1)
    gr['width'] = GRASSIMAGES[0].get_width()
    gr['height'] = GRASSIMAGES[0].get_height()
    gr['x'], gr['y'] = getRandomOffCameraPos(cameraX, cameraY, gr['width'],
                                             gr['height'])
    gr['rect'] = pygame.Rect((gr['x'], gr['y'], gr['width'], gr['height']))
    return gr


def isOutsideActiveArea(cameraX, cameraY, obj):
    boundsLeftEdge = cameraX - WINWIDTH
    boundsTopEdge = cameraY - WINHEIGHT
    boundsRect = pygame.Rect(boundsLeftEdge, boundsTopEdge, WINWIDTH * 3,
                             WINHEIGHT * 3)
    objRect = pygame.Rect(obj['x'], obj['y'], obj['width'], obj['height'])
    return not boundsRect.colliderect(objRect)


if __name__ == '__main__':
    main()
