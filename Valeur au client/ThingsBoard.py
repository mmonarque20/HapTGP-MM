# référence : https://thingsboard.io/docs/reference/python-client-sdk/
""" Programme permettant d'envoyer les données du bme280 et veml7700 
sur ThingsBoard  par MQTT seulement en "swipant" vers le haut sur l'écran"""

from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
import bme280
import veml7700
import time
import RPi.GPIO as GPIO
import cst816
import board

#Configutation des broches
TOUCH_RST_PIN = 17 
GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
GPIO.setup(TOUCH_RST_PIN, GPIO.OUT) # touch reset pin set as output

GPIO.output(TOUCH_RST_PIN, GPIO.HIGH)
time.sleep(0.1)

i2c = board.I2C()  # Utilise board.SCL et board.SDA
touch = cst816.CST816(i2c)


# Connection à ThingsBoard
client = TBDeviceMqttClient("206.167.80.224", username="wzRVz5UzTs6SvKQIuR2U") # (tb-io.claurendeau.qc.ca)

client.connect()

while not client.is_connected():
    print("Connexion en cours...")
    time.sleep(1)
print("Connecté à ThingsBoard !")

# Envoie de données en swipant vers le haut
try:
    while True:
        if touch.get_touch():
            gesture = touch.get_gesture()
            print(f"Touch détecté ! ID du geste reçu : {gesture}")
            while touch.get_touch():
                ges = touch.get_gesture()
                if (ges != 0):
                    gesture = ges
                time.sleep(0.01)
            if gesture == 2:
                print("Swipe détecté")
                time.sleep(0.1)

                telemetry = {"Temperature" : float(bme280.getTemperature()), "Humidite" : float(bme280.getHumidity()), 
                "Pression" : float(bme280.getPressure()), "Altitude" : float(bme280.getAltitude()), "Luminosite" : float(veml7700.getLuminosite())}

                result = client.send_telemetry(telemetry)

                if result.get() == TBPublishInfo.TB_ERR_SUCCESS:
                    print("Result", str(result))
                else:
                    print("Erreur lors de l'envoie")
       
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nArrêt du programme")
    client.disconnect()
    GPIO.cleanup()
