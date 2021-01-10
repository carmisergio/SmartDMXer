import pygame, sys, random
from pygame.locals import QUIT 
import array
import json

# global variables
WINDOWWIDTH = 500
WINDOWHEIGHT = 400
FPS = 500

BOARDWIDTH = 5
BOARDHEIGHT = 4

BOXWIDTH = WINDOWWIDTH / BOARDWIDTH
BOXHEIGHT = WINDOWHEIGHT / BOARDHEIGHT


def main():
    global FPSCLOCK, DISPLAYSURF

    # Pygame initialization
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption("Light Output Visualizer")

    lightdata = []
    for _ in range(0, 512):
        lightdata.append(0)

    font = pygame.font.Font(None, 25)
    while True: # main game loop
        DISPLAYSURF.fill((0, 0, 0))
        # events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        with open('lightdata.json') as f:
            try:
                data = json.load(f)
                lightdata = data["data"]
            except:
                print("An exception occurred")
            
        i = 0
        # drawing
        for y, _ in enumerate(range(0, BOARDHEIGHT)):
            for x, _ in enumerate(range(0, BOARDWIDTH)):
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

if __name__ == "__main__":
    main()