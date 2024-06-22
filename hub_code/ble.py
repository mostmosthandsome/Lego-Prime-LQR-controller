from pybricks.pupdevices import Motor
from pybricks.hubs import PrimeHub
from pybricks.parameters import Port, Axis
from pybricks.tools import wait
import ustruct

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
freq = 10
dt = 1 / freq
micropython.kbd_intr(-1)
Kp = 500
Ki = 0.01
Kd = 0.11
init_pos = hub.imu.rotation(Axis.X)
sum = 0

while True:
    # Optional: Check available input.
    theta = hub.imu.rotation(Axis.X)
    omega = hub.imu.angular_velocity(Axis.X)
    a = hub.imu.acceleration(Axis.X)
    theta_error = theta - init_pos
    # sum += theta_error
    speed = -Kp * theta_error + Kd * omega
    if speed > 1000:
        speed = 1000
    elif speed < -1000:
        speed = -1000

    if keyboard.poll(0):
        cmd = stdin.buffer.read(1)
        if cmd == b'\x00':
            stdout.buffer.write(ustruct.pack('f', theta))
            stdout.buffer.write(ustruct.pack('f', omega))
            stdout.flush()
        elif cmd == b'\x01':
            break
        elif cmd == b'\x02':
            # Decide what to do based on the command.
            # read the command len
            acc = ustruct.unpack('f', stdin.buffer.read(4))[0]
            speed = motor.speed() + acc * 180 / 0.025 * dt

    motor.run(speed)





