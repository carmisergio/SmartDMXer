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
RenderChannels = 100
SubscribeChannels = 100
BaseTopic = "mansardalight"
ClientName = "SmartDMXer"
BrokerHost = "192.168.1.61"
BrokerPort = 1883
MqttAuth = True
MqttUser = "sergio"
MqttPass = "sergio06"
SleepTime = 5
FilePath = "files/lightdata.json"
DefaultTransition = 1 #s
# /CONFIG VARIABLES #

#Init statekeeper arrays 
haLightBright = []
halightState = []
curLightBright = []
FadeDelta = []
FadeTarget = []

mqttfailflag = False
#Mqtt connection callbacks
def on_connect(client, userdata, flags, rc):
    print("MQTT client connected!")
    for i in range(0, SubscribeChannels):
        publishLightState(i)
    client.publish(BaseTopic + "/avail" ,"online",qos=0,retain=True)
    for i in range(0, SubscribeChannels):
        client.subscribe(BaseTopic + "/" + str(i) + "/set")

def on_disconnect(client, userdata, rc):
   print("MQTT connection lost")

def on_message(client, userdata, message):
    global curLightBright
    global halightState
    global haLightBright
    global FadeDelta
    global FadeTarget
    lightid = int(message.topic.split("/")[1])
    inPayload = {}
    try:
        inPayload = json.loads(str(message.payload.decode("utf-8")))
    except:
        print("ERROR: unable to parse incoming MQTT message")
    if "state" in inPayload:
        if "transition" in inPayload:
            transition = inPayload["transition"]
        else:
            transition = DefaultTransition
        if transition != 0:
            if inPayload["state"] == "ON":
                #if not halightState[lightid]:
                if "brightness" in inPayload:
                    print("Brightness in input")
                    haLightBright[lightid] = int(inPayload["brightness"])
                FadeTarget[lightid] = int(haLightBright[lightid])
                if FadeTarget[lightid] != curLightBright[lightid]:
                    FadeDelta[lightid] = (FadeTarget[lightid] - curLightBright[lightid]) / (transition * RenderFPS)
                if haLightBright[lightid] == 0:
                    halightState[lightid] = False
                else:
                    halightState[lightid] = True
            elif inPayload["state"] == "OFF":
                if curLightBright[lightid] != 0:
                    FadeTarget[lightid] = 0
                    FadeDelta[lightid] = (FadeTarget[lightid] - curLightBright[lightid]) / (transition * RenderFPS)
                halightState[lightid] = False
        else:
            if inPayload["state"] == "ON":
                #if not halightState[lightid]:
                if "brightness" in inPayload:
                    print("Brightness in input")
                    haLightBright[lightid] = int(inPayload["brightness"])
                FadeTarget[lightid] = int(haLightBright[lightid])
                if FadeTarget[lightid] != curLightBright[lightid]:
                    curLightBright[lightid] = FadeTarget[lightid]
                if haLightBright[lightid] == 0:
                    halightState[lightid] = False
                else:
                    halightState[lightid] = True
            elif inPayload["state"] == "OFF":
                if curLightBright[lightid] != 0:
                    FadeTarget[lightid] = 0
                    curLightBright[lightid] = FadeTarget[lightid]
                    halightState[lightid] = False

        publishLightState(lightid)
        print(inPayload)

def publishLightState(lightid):
    global client
    if halightState[lightid]:
        stateonoff = "ON"
    else:
        stateonoff = "OFF"
    data = {"state": stateonoff, "brightness": haLightBright[lightid]}
    jsonData = json.dumps(data)
    client.publish(BaseTopic + "/" + str(lightid) ,jsonData,qos=0,retain=True)

#Render values from statekeeper arrays to lights
def renderLights():
    outputData = []
    for i, bright in enumerate(curLightBright):
        outputData.append(int(bright))
    data = {"data": outputData}
    with open(FilePath, 'w+') as json_file:
        json.dump(data, json_file)
def main():
    global client
    def exitprogram():
        print('You pressed Ctrl+C! Exiting Program.')
        client.publish(BaseTopic + "/avail" ,"offline",qos=0,retain=True)
        client.loop_stop()
        outputData = []
        for _ in range(0, RenderChannels):
            outputData.append(0)
        data = {"data": outputData}
        with open(FilePath, 'w+') as json_file:
            json.dump(data, json_file)
        exit()
    print("SmartDMXer DMX engine is starting!")
    def signal_handler(sig, frame):
        exitprogram()
    FPSCLOCK = pygame.time.Clock()
    signal.signal(signal.SIGINT, signal_handler)

    print("Generating statekeeper arrays...")

    for _ in range(0, RenderChannels):
        haLightBright.append(255)
        halightState.append(False)
        curLightBright.append(0)
        FadeDelta.append(0)
        FadeTarget.append(255)

    print("Starting light output")
    lightOutput = True

    #Initialize mqtt client
    print("Initializing MQTT Client...")
    print("Host: " + str(BrokerHost))
    print("Port: " + str(BrokerPort))
    if MqttAuth:
        print("Using MQTT autentication")
    else:
        print("MQTT autentication not necessary")
    client = mqtt.Client(ClientName)
    if MqttAuth:
        client.username_pw_set(username=MqttUser,password=MqttPass)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message=on_message #attach function to callback
    client.will_set(BaseTopic + "/avail","offline",qos=1,retain=False)
    try:
        client.connect(BrokerHost, port=BrokerPort)
    except:
        print("MQTT connection failed.")
    client.loop_start()
    while True:
        for lightid in range(0, RenderChannels):
            if FadeDelta[lightid] != 0:
                if FadeDelta[lightid] > 0:
                    #print("FadingUp")
                    if curLightBright[lightid] < FadeTarget[lightid]:
                        curLightBright[lightid] = curLightBright[lightid] + FadeDelta[lightid]
                        if curLightBright[lightid] > 255:
                            curLightBright[lightid] = 255
                    else:
                        FadeDelta[lightid] = 0
                        print("finished fade!")
                if FadeDelta[lightid] < 0:
                    #print("FadingDpwn")
                    if curLightBright[lightid] > FadeTarget[lightid]:
                        curLightBright[lightid] = curLightBright[lightid] + FadeDelta[lightid]
                        if curLightBright[lightid] < 0:
                            curLightBright[lightid] = 0
                    else:
                        FadeDelta[lightid] = 0
                        print("finished fade!")
        if lightOutput:
            lightRenderer = threading.Thread(target=renderLights)
            lightRenderer.start()
        #print(FPSCLOCK.get_fps())
        FPSCLOCK.tick(RenderFPS)
    exitprogram()   

if __name__ == "__main__":
    main()