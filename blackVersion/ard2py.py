import serial
import time

# Open serial communication with Arduino 1 (connected to Computer 1)
arduino1 = serial.Serial('COM3', 9600, timeout=0.05)  # Change COM port based on your setup
time.sleep(2)  # Give some time to establish connection

# Send a value to Arduino 1
# arduino1.write(b'Hello from Computer 1\n')

# Read response from Arduino 1 (which gets forwarded from Arduino 2)
while True:
    if arduino1.in_waiting > 0:
        message = arduino1.readline().decode().strip()
        print(message)
        arduino1.flushInput()
        # arduino1.write(b'Hello from Computer 1\n')
        # break     