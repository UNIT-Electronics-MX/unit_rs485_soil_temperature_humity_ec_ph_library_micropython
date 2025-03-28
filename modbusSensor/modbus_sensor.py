# modbus_sensor.py
# Version: 0.0.2
# Copyright (C) 2025 UNIT-Electronics-MX
# Released under the terms of the GNU General Public License v3.0

import machine
import time

class ModbusSensor:
    """
    A class to communicate with the RS485 Soil Sensor (Temperature, Humidity, EC, PH).
    """

    def __init__(self, tx_pin=4, rx_pin=19, baudrate=4800, uart_num=1):
        """
        Initialize the ModbusSensor with UART configuration.

        :param tx_pin: Transmit pin number.
        :param rx_pin: Receive pin number.
        :param baudrate: Communication baud rate.
        :param uart_num: UART number.
        """
        self.uart = machine.UART(
            uart_num,
            baudrate=baudrate,
            tx=tx_pin,
            rx=rx_pin,
            bits=8,
            parity=None,
            stop=1,
            timeout=200
        )
        # Default command to read 4 registers from address 0x0000
        self.command = bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x04])
        self.command += self.compute_crc(self.command)

    def compute_crc(self, data):
        """
        Compute the CRC16 for the given data.

        :param data: Data for which CRC is to be computed.
        :return: CRC16 as bytes.
        """
        crc = 0xFFFF
        for b in data:
            crc ^= b
            for _ in range(8):
                if (crc & 0x0001):
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return bytes([crc & 0xFF, (crc >> 8) & 0xFF])

    def send_command(self):
        """
        Send the command to the sensor.
        """
        try:
            self.uart.write(self.command)
        except Exception as e:
            print("Error sending command:", e)

    def read_data(self):
        """
        Read the data from the sensor.

        :return: Tuple containing humidity, temperature, EC, and pH values.
        """
        try:
            response = self.uart.read()

            if not response or len(response) < 11:
                raise ValueError("No response or incomplete data")

            if response[0] != 0x01 or response[1] != 0x03 or response[2] != 8:
                raise ValueError("Invalid response header")

            # Extract sensor readings
            humidity = (response[3] << 8) | response[4]
            temperature = (response[5] << 8) | response[6]
            ec = (response[7] << 8) | response[8]
            ph = (response[9] << 8) | response[10]

            return (
                humidity / 10.0,
                temperature / 10.0,
                ec,
                ph / 10.0
            )

        except Exception as e:
            print("Error reading sensor data:", e)
            return (-1.0, -1.0, -1, -1.0)  # Default error values

    def get_sensor_data(self):
        """
        Retrieve sensor data by sending a command and reading the response.

        :return: Tuple containing humidity, temperature, EC, and pH values.
        """
        self.send_command()
        time.sleep(0.5)  # Wait for sensor to process and respond
        return self.read_data()
