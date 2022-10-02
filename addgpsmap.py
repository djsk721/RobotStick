import os
import sys
import urllib.request
import json
import pygame
import time
from gps3 import gps3
import time
import RPi.GPIO as GPIO  # new

gps_socket=gps3.GPSDSocket()
data_stream=gps3.DataStream()
gps_socket.connect()
gps_socket.watch()
pygame.mixer.pre_init(44100,-16,2,2048)
pygame.init()
pygame.mixer.init()

GPIO.setmode(GPIO.BCM)  # new
GPIO.setup(8, GPIO.IN, GPIO.PUD_UP)  # new

client_id = "lic1b5lmm3"
client_secret = "ysA3czISD5bSK3HmLaMMkpaPpbWbj0YrbM6bHzyE"
client_accept = "application/json"
gps = None
#gps = None  #서울 특별시 서대문구 남가좌2동
# url = "https://openapi.naver.com/v1/map/geocode.xml?query=" + encText # xml 결과
def ttc(result):
    client_id = "k96yfgkhl4"
    client_secret = "9hQyKgv7polaBvn6AItVDnetvxqjSobpz8xdpafH"
    encText = urllib.parse.quote(result)
    data = "speaker=mijin&speed=0&text=" + encText;
    url = "https://naveropenapi.apigw.ntruss.com/voice/v1/tts"
    request = urllib.request.Request(url)
    request.add_header("X-NCP-APIGW-API-KEY-ID",client_id)
    request.add_header("X-NCP-APIGW-API-KEY",client_secret)
    response = urllib.request.urlopen(request, data=data.encode('utf-8'))
    rescode = response.getcode()
    if(rescode==200):
        print("TTS mp3 저장")
        response_body = response.read()
        with open('gps.mp3', 'wb') as f:
            f.write(response_body)
    else:
        print("Error Code:" + rescode)

i=0

    
while True:
    
    for new_data in gps_socket:
        if new_data:
            GPIO.wait_for_edge(8, GPIO.FALLING)  # new    
            data_stream.unpack(new_data)
            print('lon : ',data_stream.TPV['lon'])
            print('lat : ',data_stream.TPV['lat'])
            gps = str(data_stream.TPV['lon'])+','+str(data_stream.TPV['lat'])#부산샬라샬라
            print(gps)
            if i==0:
                i=i+1
                continue
            if(gps!='n/a,n/a'):
                url = "https://naveropenapi.apigw.ntruss.com/map-reversegeocode/v2/gc?request=coordsToaddr&coords="+gps+"&sourcecrs=epsg:4326&output=json&orders=admcode" # json 결과
                request = urllib.request.Request(url)
                request.add_header("X-NCP-APIGW-API-KEY-ID",client_id)
                request.add_header("X-NCP-APIGW-API-KEY",client_secret)
                #request.add_header("Accept",client_accept)
                response = urllib.request.urlopen(request)
                rescode = response.getcode()
                if(rescode==200):
                    response_body = response.read()
                    #print(response_body.decode('utf-8'))
                    j1=response_body
                    j2=json.loads(j1)

                    j3= (j2['results'][0]['region']['area0']['name']+" "+
                    j2['results'][0]['region']['area1']['name']+" "+
                    j2['results'][0]['region']['area2']['name']+" "+
                    j2['results'][0]['region']['area3']['name']+" "+
                    j2['results'][0]['region']['area4']['name']
                    )
                    print(j3)
                    
                    ttc(j3)
                    pygame.mixer.music.load("gps.mp3")
                    pygame.mixer.music.play()
                    time.sleep(1)
                    
                else:
                    print("Error Code:" + rescode)
            else:
                print("check data")
