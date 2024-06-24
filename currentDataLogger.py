import smbus2
import time
import csv
import pandas as pd
from datetime import datetime

# I2C address for INA260 module
INA260_I2C_ADDRESS = 0x40

# INA260 register configuration
REG_CONFIG = 0x00
REG_CURRENT = 0x01
REG_VOLTAGE = 0x02

# Initialize I2C with SMBus
bus = smbus2.SMBus(1)

# CSV file setup to log current and voltage
csv_filename = "data_log.csv"
csv_header = ["Si.No", "Timestamp", "Voltage (mV)", "Current (mA)"]

# Create new file and log the header to the CSV file
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(csv_header)

def read_register(address, register):
    # Read 2 bytes from the register
    data = bus.read_i2c_block_data(address, register, 2)
    return data

def read_current():
    # Read current register
    data = read_register(INA260_I2C_ADDRESS, REG_CURRENT)
    # Convert to signed 16-bit value
    current = data[0] << 8 | data[1]
    if current > 32767:
        current -= 65536
    return current * 1.25  # Current LSB = 1.25 mA

def read_voltage():
    # Read voltage register
    data = read_register(INA260_I2C_ADDRESS, REG_VOLTAGE)
    # Convert to unsigned 16-bit value
    voltage = data[0] << 8 | data[1]
    return voltage * 1.25  # Voltage LSB = 1.25 mV

try:
    si_no = 1
    data_log = []
    while True:
        current = read_current()
        voltage = read_voltage()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"Si.No: {si_no}, Timestamp: {timestamp}, Voltage: {voltage} mV, Current: {current} mA")
        
        # Log data
        with open(csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([si_no, timestamp, voltage, current])

        data_log.append([si_no, timestamp, voltage, current])
        
        si_no += 1
        time.sleep(1)

except KeyboardInterrupt:
    print("Measurement stopped by user")

finally:
    bus.close()

    df = pd.DataFrame(data_log, columns=csv_header)
    excel_filename = "data_log.xlsx"
    df.to_excel(excel_filename, index=False)
    print(f"Data saved to {csv_filename} and {excel_filename}")
