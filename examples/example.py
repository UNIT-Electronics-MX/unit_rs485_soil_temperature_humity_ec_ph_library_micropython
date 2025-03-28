from modbusSensor.modbus_sensor import ModbusSensor
import time

# Initialize the sensor
sensor = ModbusSensor(tx_pin=26, rx_pin=25, baudrate=4800)

while True:
    humidity, temperature, ec, ph = sensor.get_sensor_data()
    print(f"Humidity: {humidity}% | Temperature: {temperature}°C | EC: {ec} µS/cm | pH: {ph}")
    time.sleep(1)
