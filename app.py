from flask import Flask, render_template, jsonify, request, Response
import random
import time
import json
import os
from flask_socketio import SocketIO
import eventlet
import csv
import struct
import datetime

app = Flask(__name__)

# In-memory store for demonstration purposes
message_history = []

@app.route('/rockblock', methods=['POST'])
def handle_rockblock():
    imei = request.args.get('imei')
    data = request.args.get('data')

    # Debugging: Log incoming request
    print(f"Received POST /rockblock - IMEI: {imei}, Data: {data}")

    if imei != "300434065264590":
        print("Invalid credentials")
        return "FAILED,10,Invalid login credentials", 400

    if not data:
        print("No data provided")
        return "FAILED,16,No data provided", 400

    try:
        byte_data = bytearray.fromhex(data)

        if len(byte_data) != 50:  # Ensure 50 bytes as expected
            print(f"Unexpected message length: {len(byte_data)} bytes")
            return "FAILED,17,Invalid message length", 400

        # Unpack binary data into meaningful values
        unpacked_data = struct.unpack('IhffHhhhhhhhhhhhhhhhh', byte_data)
        unpacked_data = list(unpacked_data)

        # Scale values where necessary
        for x in range(5, 12):  # Pressure and temperatures (multiplied by 10 before sending)
            unpacked_data[x] /= 10
        for x in range(12, 15):  # Average velocities (multiplied by 1000 before sending)
            unpacked_data[x] /= 1000
        for x in range(15, 21):  # Std and peak velocities (multiplied by 100 before sending)
            unpacked_data[x] /= 100

        # Convert Unix Epoch timestamp to UTC format
        sent_time_utc = datetime.datetime.fromtimestamp(unpacked_data[0], datetime.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')

        # Store data for live retrieval
        message_data = {
            "received_time": datetime.datetime.utcnow().isoformat() + "Z",
            "sent_time": sent_time_utc,
            "unix_epoch": unpacked_data[0],
            "siv": unpacked_data[1],
            "latitude": unpacked_data[2],
            "longitude": unpacked_data[3],
            "altitude": unpacked_data[4],
            "pressure_mbar": unpacked_data[5],
            "temperature_pht_c": unpacked_data[6],
            "temperature_cj_c": unpacked_data[7],
            "temperature_tctip_c": unpacked_data[8],
            "roll_deg": unpacked_data[9],
            "pitch_deg": unpacked_data[10],
            "yaw_deg": unpacked_data[11],
            "vavg_1_mps": unpacked_data[12],
            "vavg_2_mps": unpacked_data[13],
            "vavg_3_mps": unpacked_data[14],
            "vstd_1_mps": unpacked_data[15],
            "vstd_2_mps": unpacked_data[16],
            "vstd_3_mps": unpacked_data[17],
            "vpk_1_mps": unpacked_data[18],
            "vpk_2_mps": unpacked_data[19],
            "vpk_3_mps": unpacked_data[20],
        }

        message_history.append(message_data)

        print(f"Decoded Message: {message_data}")

        return "OK,0"

    except Exception as e:
        print("Error processing data:", e)
        return "FAILED,15,Error processing message data", 400

@app.route('/live-data', methods=['GET'])
def get_live_data():
    return jsonify(message_history[-1] if message_history else {"message": "No data received yet"})

@app.route('/history', methods=['GET'])
def load_flight_history():
    return jsonify(message_history)

@app.route('/download-history', methods=['GET'])
def download_history():
    if not message_history:
        return "No data available", 404

    def generate_csv():
        fieldnames = message_history[0].keys()
        csv_output = csv.DictWriter(Response(), fieldnames=fieldnames)
        yield ','.join(fieldnames) + '\n'
        for row in message_history:
            yield ','.join(str(row[field]) for field in fieldnames) + '\n'

    return Response(generate_csv(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment; filename=flight_history.csv"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


