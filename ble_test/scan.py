from bleak import BleakScanner, BleakClient
import asyncio

async def connect_to_device(device):
    async with BleakClient(device) as client:
        try:
            await client.connect()
            print(f"Connected to {device.name}")

            # Example: Read data from a specific characteristic
            data = await client.read_gatt_char("00002a00-0000-1000-8000-00805f9b34fb")  # Example UUID
            print(f"Received data: {data}")

        except Exception as e:
            print(f"Error connecting to {device.name}: {e}")

async def scan_for_devices():
    scanner = BleakScanner()

    def callback(device, advertisement_data):
        if device.name == "Pybricks Hub":
            print(f"  Advertisement data: {advertisement_data}")

    scanner.register_detection_callback(callback)

    print("Scanning for 10 seconds...")
    await scanner.start()
    await asyncio.sleep(10.0)
    await scanner.stop()

asyncio.run(scan_for_devices())