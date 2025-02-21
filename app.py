import struct
import time
import json
import requests
import random

# Generate random data within reasonable ranges
data = [0] * 21
data[0] = int(time.time())  # Current Unix timestamp (seconds since Jan 1 1970)
data[1] = random.randint(5, 20)  # GPS satellites in view (5-20)
data[2] = random.uniform(40.0, 45.0)  # GPS latitude (around Medford, MA: 42.35 ± 2.65)
data[3] = random.uniform(-73.0, -70.0)  # GPS longitude (around Medford: -71.7 ± 1.3)
data[4] = random.randint(500, 1500)  # Altitude (meters, 500-1500m)
data[5] = random.uniform(950, 1050)  # Pressure (mbar, 950-1050)
data[6] = random.uniform(20.0, 30.0)  # Internal electronics temp (C, 20-30)
data[7] = random.uniform(15.0, 25.0)  # TC cold junction temp (C, 15-25)
data[8] = random.uniform(10.0, 20.0)  # TC tip (air) temp (C, 10-20)
data[9] = random.uniform(-15.0, 15.0)  # Euler roll angle (deg, ±15)
data[10] = random.uniform(-15.0, 15.0)  # Euler pitch angle (deg, ±15)
data[11] = random.uniform(0.0, 360.0)  # Euler yaw angle (deg, 0-360)
data[12] = random.uniform(-5.0, 5.0)  # Avg wind direction 1 (m/s, ±5)
data[13] = random.uniform(-5.0, 5.0)  # Avg wind direction 2 (m/s, ±5)
data[14] = random.uniform(-5.0, 5.0)  # Avg wind direction 3 (m/s, ±5)
data[15] = random.uniform(0.0, 5.0)  # Stddev wind direction 1 (m/s, 0-5)
data[16] = random.uniform(0.0, 5.0)  # Stddev wind direction 2 (m/s, 0-5)
data[17] = random.uniform(0.0, 5.0)  # Stddev wind direction 3 (m/s, 0-5)
data[18] = random.uniform(5.0, 15.0)  # Peak wind direction 1 (m/s, 5-15)
data[19] = random.uniform(5.0, 15.0)  # Peak wind direction 2 (m/s, 5-15)
data[20] = random.uniform(5.0, 15.0)  # Peak wind direction 3 (m/s, 5-15)

# Scaling as before
for x in range(5, 12):
    data[x] = int(data[x] * 10)  # Pressure, temps, Euler angles (*10)
for x in range(12, 15):
    data[x] = int(data[x] * 1000)  # Avg velocities (mm/s, *1000)
for x in range(15, 21):
    data[x] = int(data[x] * 100)  # Std dev, peak velocities (cm/s, *100)

# Pack into a binary string
packed_data = struct.pack('IhffHhhhhhhhhhhhhhhhh', *data)
print(f"Number of bytes: {len(packed_data)}")
print(packed_data)

# Convert to hex
encoded_packed_data = packed_data.hex()

# Data to send
senddata = {
    "imei": "301434061119410",
    "iridium_latitude": data[2],
    "iridium_longitude": data[3],
    "data": encoded_packed_data
}

url = "https://tufts-anemometer3.onrender.com/rockblock"

# Send the request
response = requests.post(url, json=senddata, headers={"Content-Type": "application/json"})

print("Status Code:", response.status_code)
print("Response:", response.text)

