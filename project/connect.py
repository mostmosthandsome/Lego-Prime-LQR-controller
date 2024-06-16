# SPDX-License-Identifier: MIT
# Copyright (c) 2020 Henrik Blidh
# Copyright (c) 2022-2023 The Pybricks Authors

"""
Example program for computer-to-hub communication.

Requires Pybricks firmware >= 3.3.0.
"""
import sys
import  time
sys.coinit_flags = 0

import asyncio
from contextlib import suppress
from bleak import BleakScanner, BleakClient
import  struct
import numpy as np

from env.sim import CartPoleSim
from env.controller import LQR, MPC

import numpy as np

PYBRICKS_COMMAND_EVENT_CHAR_UUID = "c5f50002-8280-46da-89f4-6d8051e4aeef"

# Replace this with the name of your hub if you changed
# it when installing the Pybricks firmware.
HUB_NAME = "Pybricks Hub"

ready_event = asyncio.Event()
length = 0.3
cart_mass = 0.3
pole_mass = 0.8
damping = 0.1
gravity = 9.81
Q = np.diag([0.5, 0.5])
R = np.array([[0.1]])
dt = 0.01
state = np.array([0.5, 0])
sim = CartPoleSim(state, length, cart_mass, pole_mass, damping, gravity, dt)
lqr = LQR(sim)
acc = 0.05
degree = 0
angular_velocity = 0
init_pos = 0



async def main():
    main_task = asyncio.current_task()

    start_time = time.time_ns()
    def handle_disconnect(_):
        print("Hub was disconnected.")

        # If the hub disconnects before this program is done,
        # cancel this program so it doesn't get stuck waiting
        # forever.
        if not main_task.done():
            main_task.cancel()

    async def handle_rx(_, data: bytearray):
        if data[0] == 0x01:  # "write stdout" event (0x01)
            payload = data[1:]
            if len(payload) == 8:
                # print(f"Received len{len(payload)} data:",payload)
                global degree, angular_velocity, init_pos
                degree = struct.unpack('f', payload[:4])[0]
                angular_velocity = struct.unpack('f', payload[4:])[0]
            else:
                pass
            ready_event.set()
                # print(f"receive {len(payload)} respond : ",payload)

    # Do a Bluetooth scan to find the hub.
    device = await BleakScanner.find_device_by_name(HUB_NAME)

    if device is None:
        print(f"could not find hub with name: {HUB_NAME}")
        return

    # Connect to the hub.
    async with BleakClient(device, handle_disconnect) as client:

        # Subscribe to notifications from the hub.
        await client.start_notify(PYBRICKS_COMMAND_EVENT_CHAR_UUID, handle_rx)

        # Shorthand for sending some data to the hub.
        async def send(data):
            # Send the data to the hub.
            await client.write_gatt_char(
                PYBRICKS_COMMAND_EVENT_CHAR_UUID,
                b"\x06" + data,  # prepend "write stdin" command (0x06)
                response=True
            )

        # Tell user to start program on the hub.
        print("Start the program on the hub now with the button.")
        #ensure read the first data
        await send(b"redy")
        await ready_event.wait()
        global init_pos,degree
        init_pos = degree
        # Send a few messages to the hub.
        while True :

            await send(0)
            await ready_event.wait()
            acc = await lqr._real_lqr_controller(Q, R, np.array([0, 0]),degree-init_pos, angular_velocity)
            await send(struct.pack('f',-acc))
            end_time = time.time_ns()
            ready_event.clear()
            print("send",acc)
            print(".", end="", flush=True)
            start_time = time.time_ns()

        # Send a message to indicate stop.
        await send(b"bye~")

        print("done.")

    # Hub disconnects here when async with block exits.


# Run the main async program.
if __name__ == "__main__":
    with suppress(asyncio.CancelledError):
        asyncio.run(main())

