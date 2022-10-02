#-*- coding: utf-8 -*-
# /etc/rc.local 에 sudo python3 /home/pi/Downloads/stick_v3.py 붙이기
import pygame
import sys
import urllib.request
import cv2
import numpy as np
import pytesseract
from  PIL import Image
import time
import picamera
import RPi.GPIO as GPIO  # new
import signal
from gpiozero import PWMOutputDevice
from gpiozero import Button
import datetime
from gps3 import gps3

# 초기 변수 선언
bt = 0  # 버튼2 변수 가중치
TRIG = 2  # 초음파 TRIG
ECHO = 3  # 초음파 ECHO
button2 = Button(16)  # 버튼2 -> GPS 및 시간 알려주는 버튼
button = Button(21)  # 버튼1 -> 카메라 전환 및 촬영
GPIO.setmode(GPIO.BCM)  # new
GPIO.setup(16, GPIO.IN, GPIO.PUD_UP)  # new
GPIO.setup(21, GPIO.IN, GPIO.PUD_UP)  # new
pygame.mixer.init(16000)
gps_socket = gps3.GPSDSocket()  # GPS로부터 정보를 받아오는 로직
data_stream = gps3.DataStream()
gps_socket.connect()
gps_socket.watch()


# 시간을 불러오는 함수
def clock():
    now = datetime.datetime.now()
    DateAndTime = now.strftime('%m - %d  %H : %M ')
    print(DateAndTime)
    ttc(DateAndTime)
    
    pygame.mixer.music.load('/home/pi/Downloads/camera.mp3')
    pygame.mixer.music.play()
    time.sleep(3)


# 초음파 모듈을 통해서 거리에 따라서 진동하는 함수
# 참고 : https://m.blog.naver.com/PostView.nhn?blogId=chandong83&logNo=221155355360&proxyReferer=https%3A%2F%2Fwww.google.com%2F
def cho():
         
    MAX_DISTANCE_CM =300
    MAX_DURATION_TIMEOUT = (MAX_DISTANCE_CM *2 *29.1)
    motor=PWMOutputDevice(26,active_high=True,frequency=5000)
    motor.off()
    def signal_handler(signal,frame):
        print("Ctrl+C")
        GPIO.cleanup()
        sys.exit(0)
    signal.signal(signal.SIGINT,signal_handler)

    def distanceInCm(duration):
        return (duration/2)/29.1

    def print_distance(distance):
        if distance==0:
            distanceMsg = 'Distance : out of range\n'
        else:
            distanceMsg = 'Distance : '+str(distance)+'cm'+'\n'
        sys.stdout.write(distanceMsg)
        sys.stdout.flush()
        
    def vibration(distance):
        if distance<=130:
            motor.value=1.0
            time.sleep(0.5)
        elif distance>130 and distance<=150:
            motor.value=0.5
            time.sleep(0.5)
        elif distance>150 and distance<=200:
            motor.value=0.3
            time.sleep(0.5)
        elif distance>200:
            print(distance)
            motor.value=0.0
            
        
        
    def main():
        choum= 0
        global bt
        
        GPIO.setmode(GPIO.BCM)
        
        GPIO.setup(TRIG,GPIO.OUT)
        GPIO.setup(ECHO,GPIO.IN)
        
        #print('To Exit , Press the CTRL+c Keys')
        
        GPIO.output(TRIG,False)
        #print('Waiting For Sensor To Ready')
        #time.sleep(1)
        print('Start!!')
        ttc('진동이 울립니다')
        pygame.mixer.music.load('/home/pi/Downloads/camera.mp3')
        pygame.mixer.music.play()
        
        while choum==0:
            fail=False
            time.sleep(0.1)
            GPIO.output(TRIG,True)
            if(button.is_pressed):
                choum=1
                bt=1
            if(button2.is_pressed):
                choum=1
                bt=2    
            time.sleep(0.00001)
            GPIO.output(TRIG,False)
            
            timeout=time.time()
            while GPIO.input(ECHO)==0:
                pulse_start = time.time()
                if((pulse_start-timeout)*1000000)>=MAX_DURATION_TIMEOUT:
                    fail=True
                    break
            if fail:
                continue
            timeout=time.time()
            while GPIO.input(ECHO)==1:
                pulse_end=time.time()
                if((pulse_end-pulse_start)*1000000)>=MAX_DURATION_TIMEOUT:
                    print_distance(0)
                    fail=True
                    break
            
            if fail:
                continue
            
            pulse_duration=(pulse_end-pulse_start)*1000000
            
            distance=distanceInCm(pulse_duration)
            distance=round(distance,2)
            print_distance(distance)
            vibration(distance)
        
        #GPIO.cleanup()
        
        
    if __name__=='__main__':
        motor.on()
        main()
        #bt=1
        motor=0
        return bt
        

# 사진 촬영하는 함수
def takeaPicture():
    with picamera.PiCamera() as camera:
    
        camera.start_preview()
        #GPIO2.wait_for_edge(21, GPIO.FALLING)  # new
        while True:
            if(button.is_pressed):
                camera.capture('/home/pi/Downloads/image.jpg')
                camera.stop_preview()
                break


# 읽은 텍스트를 MP3 파일로 변환해주는 함수 (Text To Speech)
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
        with open('/home/pi/Downloads/camera.mp3', 'wb') as f:
            f.write(response_body)
    else:
        print("Error Code:" + rescode)


# 모듈로부터 위치 정보를 받아와서 도로명 주소로 변환 하는 로직
def gps():
    i = 0
    client_id = "lic1b5lmm3"
    client_secret = "ysA3czISD5bSK3HmLaMMkpaPpbWbj0YrbM6bHzyE"
    client_accept = "application/json"
    # 로직 수정 1
    # gps='n/a,n/a'
    for new_data in gps_socket:
        if new_data:
            data_stream.unpack(new_data)
            print('lon : ', data_stream.TPV['lon'])
            print('lat : ', data_stream.TPV['lat'])
            gps = str(data_stream.TPV['lon']) + ',' + str(data_stream.TPV['lat'])
            print(gps)
            if i == 0:
                i = i + 1
                continue
            if (gps != 'n/a,n/a'):
                url = "https://naveropenapi.apigw.ntruss.com/map-reversegeocode/v2/gc?request=coordsToaddr&coords=" + gps + "&sourcecrs=epsg:4326&output=json&orders=admcode"  # json 결과
                request = urllib.request.Request(url)
                request.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
                request.add_header("X-NCP-APIGW-API-KEY", client_secret)
                # request.add_header("Accept",client_accept)
                response = urllib.request.urlopen(request)
                rescode = response.getcode()
                if (rescode == 200):
                    response_body = response.read()
                    # print(response_body.decode('utf-8'))
                    j1 = response_body
                    j2 = json.loads(j1)

                    j3 = (j2['results'][0]['region']['area0']['name'] + " " +
                          j2['results'][0]['region']['area1']['name'] + " " +
                          j2['results'][0]['region']['area2']['name'] + " " +
                          j2['results'][0]['region']['area3']['name'] + " " +
                          j2['results'][0]['region']['area4']['name']
                          )
                    print(j3)

                    ttc(j3)
                    pygame.mixer.music.load('/home/pi/Downloads/camera.mp3')
                    pygame.mixer.music.play()
                    time.sleep(1)
                    break
                else:
                    print("Error Code:" + rescode)
            else:
                ttc('gps 정보를 받아오는 중입니다. 잠시만 기다려주세요.')
                pygame.mixer.music.load('/home/pi/Downloads/camera.mp3')
                pygame.mixer.music.play()
                time.sleep(4.5)
                break;


# 카메라 촬영한 전처리하여 인식하는 부분
class Recognition:
    def ExtractNumber(self):
        config = ('-l Hangul --oem 1 --psm 3')
        takeaPicture()
        # 전처리 과정
        #1....입력 이미지
        Number = '/home/pi/Downloads/image.jpg'
        img = cv2.imread(Number, cv2.IMREAD_COLOR)

        # 이미지 샤프닝 부분 -----------시작--------------
        sharpening = np.array([[-1, -1, -1, -1, -1],
                                [-1, 2, 2, 2, -1],
                                 [-1, 2, 9, 2, -1],
                                 [-1, 2, 2, 2, -1],
                                 [-1, -1, -1, -1, -1]]) / 9.0
        
        dst = cv2.filter2D(img, -1, sharpening)
        cv2.imwrite('/home/pi/Downloads/sharp.jpg',dst)
        #이미지 샤프닝 부분 ----- end ----------

        # 2....RGBTOGRAY : RGB 색상의 이미지를 회색으로 처리한다
        img2 = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
        cv2.imwrite('/home/pi/Downloads/gray.jpg', img2)
        #블러 적용
        blur = cv2.bilateralFilter(img2, 9, 75, 75)
        cv2.imwrite('/home/pi/Downloads/blur.jpg', blur)
        
        # 사진 흑백 후 이진화 한 다음 글자 진하게
        th_plate = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
        cv2.imwrite('/home/pi/Downloads/plate_th.jpg', th_plate)
        
        # Opening (노이즈 제거)
        # erosion 수행후 바로 DIlation 실행
        kernel = np.ones((3,3), np.uint8)
        er_plate = cv2.morphologyEx(th_plate, cv2.MORPH_OPEN, kernel)

        er_invplate = er_plate
        cv2.imwrite('/home/pi/Downloads/er_plate.jpg', er_invplate)
        result = pytesseract.image_to_string(Image.open('/home/pi/Downloads/er_plate.jpg'), lang='Hangul'+'eng',config=config)
        print(result)
        return (result.replace(" ", ""))

# 실제 구동 부분
while True:
    if(bt==1):
        try:
            print("111")
            ttc('카메라가 켜졌습니다')
            
            pygame.mixer.music.load('/home/pi/Downloads/camera.mp3')
            pygame.mixer.music.play()
            #GPIO.cleanup()
            
            recogtest=Recognition()
            result=recogtest.ExtractNumber()
            ttc(result)
            
            pygame.mixer.music.load('/home/pi/Downloads/camera.mp3')
            pygame.mixer.music.play()
            time.sleep(7)
            bt=0
            
            
        except Exception:
            print('error')
            ttc('인식 에러 입니다')
            pygame.mixer.music.load('/home/pi/Downloads/camera.mp3')
            pygame.mixer.music.play()
            
            bt=0
            time.sleep(7)
    elif(bt==0):
        print("22")
        bt=cho()
    elif(bt==2):
        while(True):
            if button2.is_pressed:
                print(button2.is_pressed)
                bt+=1
                print(bt)
                time.sleep(1.0) # time sec
                
                    
            else:
                if(bt<=3):
                    gps()
                    bt=0
                    time.sleep(0.5)
                    break
                elif(bt>3):
                    clock()
                    bt=0
                    time.sleep(0.5)
                    break
