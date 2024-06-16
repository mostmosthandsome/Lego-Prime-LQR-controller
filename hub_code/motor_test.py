from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor
from pybricks.parameters import Port, Stop, Axis
from pybricks.tools import wait
from usys import stdin, stdout
from uselect import poll

# We'll use two motors. One is a dial
# to set the speed of the other motor.
motor = Motor(Port.C)
hub = PrimeHub()


keyboard = poll()
keyboard.register(stdin)
speed = 700

while True:
    if keyboard.poll(0):
        cmd = stdin.buffer.read(1)
        if cmd == b'a':
            speed += 100
        elif cmd == b'b':
            speed = speed - 100
        elif cmd == b'c':
            speed += 10
        elif cmd == b'n':
            speed -= 10  
    # Run motor at desired speed
    motor.run(speed)
    # print(hub.imu.rotation(Axis.X))
    print(speed)
    # Wait briefly, then repeat
    wait(10)
