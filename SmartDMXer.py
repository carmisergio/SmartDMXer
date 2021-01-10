from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import threading
import json
import signal
import time
import paho.mqtt.client as mqtt

#  CONFIG VARIABLES #
RenderFPS = 60
LightChannels = 512
ClientName = "SmartDMXer"
BrokerHost = "192.168.1.61"
BrokerPort = 1883
MqttAuth = True
MqttUser = "sergio"
MqttPass = "sergio06"
SleepTime = 5
# /CONFIG VARIABLES #

#Init statekeeper arrays 
curLightState = []
curLightBright = []

mqttfailflag = False
#Mqtt connection callbacks
def on_connect(client, userdata, flags, rc):
    print("MQTT client connected!")

def on_disconnect(client, userdata, rc):
   print("MQTT connection lost")

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
        for _ in range(0, LightChannels):
            outputData.append(0)
        data = {"data": outputData}
        with open('lightdata.json', 'w+') as json_file:
            json.dump(data, json_file)
        exit()

    def signal_handler(sig, frame):
        exitprogram()
    FPSCLOCK = pygame.time.Clock()
    signal.signal(signal.SIGINT, signal_handler)

    print("Generating statekeeper arrays...")
    for _ in range(0, LightChannels):
        curLightState.append(False)


    for _ in range(0, LightChannels):
        curLightBright.append(255)

    print("Starting light output")
    lightRenderer = threading.Thread(target=renderLights, args=("Thread-1", ), daemon=True)
    lightRenderer.start()

    #Initialize mqtt client
    client = mqtt.Client(ClientName)
    if MqttAuth:
        client.username_pw_set(username=MqttUser,password=MqttPass)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    #Try to connect, set flag if unable
    try:
        client.connect(BrokerHost, port=BrokerPort)
    except:
        mqttfailflag = True
        time.sleep(SleepTime)
    else:
        mqttfailflag = False

    while True:
        #Handle this software coming online before the mqtt server
        if mqttfailflag:
            try:
                print("Retrying mqtt connection...")
                client.connect(BrokerHost, port=BrokerPort)
            except:
                mqttfailflag = True
                print("Mqtt Connection Error")
                time.sleep(SleepTime)
            else:
                mqttfailflag = False
        client.loop()
    exitprogram()   

if __name__ == "__main__":
    main()