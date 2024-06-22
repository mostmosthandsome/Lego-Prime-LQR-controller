from pybricks.pupdevices import Motor
from pybricks.hubs import PrimeHub
from pybricks.parameters import Port, Axis, Stop
from pybricks.tools import wait
import ustruct
from pybricks.tools import multitask

# Standard MicroPython modules
from usys import stdin, stdout
from uselect import poll
import micropython

motor = Motor(Port.C)
hub = PrimeHub()

# Optional: Register stdin for polling. This allows
# you to wait for incoming data without blocking.
keyboard = poll()
keyboard.register(stdin)

speed = 0
# disable the ctrl + c input
micropython.kbd_intr(-1)

Kp = 500
Kd = 0.11
init_pos = hub.imu.rotation(Axis.X)
cnt = 0
data_buffer = bytearray(0)

while True:
    theta = hub.imu.rotation(Axis.X)
    omega = hub.imu.angular_velocity(Axis.X)

    # minus zero position to eliminate error
    theta_error = theta - init_pos

    # compute speed using pd control
    speed = -Kp * theta_error + Kd * omega
    if speed > 1000:
        speed = 1000
    elif speed < -1000:
        speed = -1000
    if abs(theta_error) > 45:
        break
    data_buffer = data_buffer + ustruct.pack('!f', theta_error) + ustruct.pack('!f', omega) + ustruct.pack('<h',
                                                                                                           motor.speed()) + ustruct.pack(
        "!f", speed)
    if cnt == 801:
        stdout.buffer.write(data_buffer)
        data_buffer = bytearray(0)

    # the first 4 byte is used to write cnt

    if keyboard.poll(0):
        if cmd == b'\x01':
            break

    cnt = cnt + 1
    motor.run(speed)
