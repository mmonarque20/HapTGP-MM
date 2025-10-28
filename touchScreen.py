#Code exemple pour tester le fonctionnement du Touch Screen CST816

import time
import board
import RPi.GPIO as GPIO
import cst816


# Pin Definitons:
touch_rst_n = 17 # Touch Screen reset pin

# Pin Setup:
GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
GPIO.setup(touch_rst_n, GPIO.OUT) # touch reset pin set as output

# Initial state for touch screen reset pin
GPIO.output(touch_rst_n, GPIO.HIGH)

# Initialize I2C
i2c = board.I2C()  # uses board.SCL and board.SDA
touch = cst816.CST816(i2c)

# Check if the touch controller is detected
if touch.who_am_i():
    print("CST816 detected.")
else:
    print("CST816 not detected.")

# Read touch data continuously
while True:
    point = touch.get_point()
    gesture = touch.get_gesture()
    press = touch.get_touch()
    distance = touch.get_distance()
    print("Position: {0},{1} - Gesture: {2} - Pressed? {3} - Distance: {4},{5}".format(point.x_point, point.y_point, gesture, press, distance.x_dist, distance.y_dist))
    time.sleep(0.05)
    