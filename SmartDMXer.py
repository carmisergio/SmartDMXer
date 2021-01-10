from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import threading
import json
import signal

#  CONFIG VARIABLES #
RenderFPS = 60
# /CONFIG VARIABLES #

#Init statekeeper arrays 
curLightState = []
curLightBright = []

#Render values from statekeeper arrays to lights
def renderLights(_):
    global curLightState
    global curLightBright
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
        data = {"data": outputData}
        with open('lightdata.json', 'w+') as json_file:
            json.dump(data, json_file)
        FPSCLOCK2.tick(RenderFPS)
def main():
    def exitprogram():
        print('You pressed Ctrl+C! Exiting Program.')
        outputData = []
        for _ in range(0, 512):
            outputData.append(0)
        data = {"data": outputData}
        with open('lightdata.json', 'w+') as json_file:
            json.dump(data, json_file)
        exit()

    def signal_handler(sig, frame):
        exitprogram()
    FPSCLOCK = pygame.time.Clock()
    signal.signal(signal.SIGINT, signal_handler)

    for _ in range(0, 512):
        curLightState.append(False)


    for _ in range(0, 512):
        curLightBright.append(255)

    #print(curLightBright)
    #print(curLightState)
    lightRenderer = threading.Thread(target=renderLights, args=("Thread-1", ), daemon=True)
    lightRenderer.start()

    for box, _ in enumerate(range(0, 20)):
        curLightBright[box] = 0
        curLightState[box] = 0
        for i, _ in enumerate(range(0, 255)):
            curLightBright[box] = i
            if i > 0:
                curLightState[box] = True
            else: 
                curLightState[box] = False
            FPSCLOCK.tick(100)
    exitprogram()   

if __name__ == "__main__":
    main()