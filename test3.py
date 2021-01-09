from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame, sys, random
from pygame.locals import *
import threading
import json
import signal

# global variables for dummy light output
WINDOWWIDTH = 500
WINDOWHEIGHT = 400
FPS = 500

BOARDWIDTH = 5
BOARDHEIGHT = 4

BOXWIDTH = WINDOWWIDTH / BOARDWIDTH
BOXHEIGHT = WINDOWHEIGHT / BOARDHEIGHT
# End global variables

curLightState = []
curLightBright = []

def renderLights(threadname):
    global curLightState
    global curLightBright
    localCurLightState = curLightState
    localCurLightBright = curLightBright
    FPSCLOCK2 = pygame.time.Clock()
    outputData = []
    while True:
        outputData = []
        for i, value in enumerate(curLightState):
            if value:
                outputData.append(curLightBright[i])
            else:
                outputData.append(0)
        #print(len(outputData))
        #Render output to screen
        # Pygame initialization
        pygame.init()
        FPSCLOCK = pygame.time.Clock()
        DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        pygame.display.set_caption("Light Output Visualizer")

        lightdata = []
        for number in range(0, 512):
            lightdata.append(0)

        font = pygame.font.Font(None, 25)
        while True: # main game loop
            DISPLAYSURF.fill((0, 0, 0))
            # events
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            i = 0
            # drawing
            for y, line in enumerate(range(0, BOARDHEIGHT)):
                for x, box in enumerate(range(0, BOARDWIDTH)):
                    data = lightdata[i]
                    if data > 255:
                        data = 255
                    pygame.draw.rect(DISPLAYSURF, (data, data, data), (x * BOXWIDTH, y * BOXHEIGHT, BOXWIDTH, BOXHEIGHT))
                    text = font.render(str(i + 1), True, (255, 0, 0))
                    DISPLAYSURF.blit(text, (x * BOXWIDTH, y * BOXHEIGHT))
                    i += 1


            # update
            pygame.display.update()
            FPSCLOCK.tick(FPS)
        
        FPSCLOCK2.tick(255)
def main():
    def signal_handler(sig, frame):
        print('You pressed Ctrl+C! Exiting Program.')
        exit()
    FPSCLOCK = pygame.time.Clock()
    signal.signal(signal.SIGINT, signal_handler)

    for number in range(0, 512):
        curLightState.append(False)


    for number in range(0, 512):
        curLightBright.append(255)

    #print(curLightBright)
    #print(curLightState)
    lightRenderer = threading.Thread(target=renderLights, args=("Thread-1", ), daemon=True)
    lightRenderer.start()

    up = True
    while True:
        if up:
            curLightState[0] = True
            up = False
        else:
            curLightState[0] = False
            up = True
        
        FPSCLOCK.tick(10)

if __name__ == "__main__":
    main()