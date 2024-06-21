import sys
import  time

import asyncio
from contextlib import suppress
from bleak import BleakScanner, BleakClient
import  struct
import numpy as np

from env.sim import CartPoleSim
from env.controller import LQR, MPC

import numpy as np

PYBRICKS_COMMAND_EVENT_CHAR_UUID = "c5f50002-8280-46da-89f4-6d8051e4aeef"
HUB_NAME = "Pybricks Hub"
data_buffer = bytearray(0)
async def main():
    main_task = asyncio.current_task()
    ready_event = asyncio.Event()
    ready_event.clear()

    start_time = time.time_ns()
    def handle_disconnect(_):
        print("Hub was disconnected.")

        global data_buffer
        record_num = (int)(len(data_buffer) / 10)
        degree_list = [struct.unpack("!f",data_buffer[i * 10:i * 10 + 4])[0] for i in range(record_num)]
        angular_list = [struct.unpack("!f",data_buffer[i * 10 + 4:i * 10 + 8])[0] for i in range(record_num)]
        speed_list = [struct.unpack("<h",data_buffer[i * 10 + 8:i * 10 + 10])[0] for i in range(record_num)]
        np.save("degree.npy", np.array(degree_list))
        np.save("angular.npy",np.array(angular_list))
        np.save("speed.npy",np.array(speed_list))


        # If the hub disconnects before this program is done,
        # cancel this program so it doesn't get stuck waiting
        # forever.
        if not main_task.done():
            main_task.cancel()

    async def handle_rx(_, data: bytearray):
        if data[0] == 0x01:  # "write stdout" event (0x01)
            payload = data[1:]
            global data_buffer
            data_buffer += payload
            ready_event.set()

    device = await BleakScanner.find_device_by_name(HUB_NAME)

    if device is None:
        print(f"could not find hub with name: {HUB_NAME}")
        return

    # Connect to the hub.
    async with BleakClient(device, handle_disconnect) as client:

        # Subscribe to notifications from the hub.
        await client.start_notify(PYBRICKS_COMMAND_EVENT_CHAR_UUID, handle_rx)

        print("Start the program on the hub now with the button.")

        while True:
            await ready_event.wait()
            ready_event.clear()

if __name__ == "__main__":
    with suppress(asyncio.CancelledError):
        asyncio.run(main())