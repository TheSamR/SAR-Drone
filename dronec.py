import airsim
import time
from pynput import keyboard

client = airsim.MultirotorClient()
client.confirmConnection()

print("Waiting for PX4 connection...")
time.sleep(5) 

print("Checking GPS lock...")
while True:
    gps_data = client.getGpsData()
    home_pos = client.getMultirotorState().gps_location

    if home_pos.altitude != 0 and gps_data.gnss.geo_point.altitude != 0:
        print(f"✅ GPS lock acquired! Home location: {home_pos}")
        break
    print("⏳ Waiting for PX4 to register home location...")
    time.sleep(1)

client.enableApiControl(True)

time.sleep(2)

client.armDisarm(True)
print("🚁 PX4 Drone is ready!")

client.takeoffAsync().join()

SPEED = 5.0
ALTITUDE_SPEED = 2.0

velocity_x, velocity_y, velocity_z = 0, 0, 0

def on_press(key):
    global velocity_x, velocity_y, velocity_z
    try:
        if key.char == 'w': velocity_x = SPEED
        elif key.char == 's': velocity_x = -SPEED
        elif key.char == 'a': velocity_y = -SPEED
        elif key.char == 'd': velocity_y = SPEED
    except AttributeError:
        if key == keyboard.Key.space: velocity_z = -ALTITUDE_SPEED
        elif key == keyboard.Key.shift: velocity_z = ALTITUDE_SPEED
    client.moveByVelocityAsync(velocity_x, velocity_y, velocity_z, 0.1)

def on_release(key):
    global velocity_x, velocity_y, velocity_z
    try:
        if key.char in ['w', 's']: velocity_x = 0
        elif key.char in ['a', 'd']: velocity_y = 0
    except AttributeError:
        if key in [keyboard.Key.space, keyboard.Key.shift]: velocity_z = 0
    client.moveByVelocityAsync(velocity_x, velocity_y, velocity_z, 0.1)
    if key == keyboard.Key.esc:
        print("🛬 Landing...")
        client.landAsync().join()
        client.armDisarm(False)
        client.enableApiControl(False)
        print("🔴 Drone disarmed. Exiting.")
        return False

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

print("🚀 Use W/A/S/D to move, SPACE to go up, SHIFT to go down, ESC to exit.")
while listener.running:
    time.sleep(0.1)
