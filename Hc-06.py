import RPi.GPIO as GPIO
import time
import sys
import signal
from gpiozero import PWMOutputDevice

#GPIO
TRIG = 23
ECHO = 24

MAX_DISTANCE_CM =300
MAX_DURATION_TIMEOUT = (MAX_DISTANCE_CM *2 *29.1)

motor=PWMOutputDevice(13,active_high=True,frequency=5000)
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
    if distance<=100:
        motor.value=1.0
        time.sleep(0.5)
    elif distance>100 and distance<=150:
        motor.value=0.5
        time.sleep(0.5)
    elif distance>150 and distance<=200:
        motor.value=0.3
        time.sleep(0.5)
    elif distance>200:
        print(distance)
        motor.value=0.0
    
    
def main():
    GPIO.setmode(GPIO.BCM)
    
    GPIO.setup(TRIG,GPIO.OUT)
    GPIO.setup(ECHO,GPIO.IN)
    
    print('To Exit , Press the CTRL+c Keys')
    
    GPIO.output(TRIG,False)
    print('Waiting For Sensor To Ready')
    time.sleep(1)
    
    print('Start!!')
    
    while True:
        fail=False
        time.sleep(0.1)
        GPIO.output(TRIG,True)
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
        print(type(distance))
        vibration(distance)
        
    GPIO.cleanup()
    
if __name__=='__main__':
    main()