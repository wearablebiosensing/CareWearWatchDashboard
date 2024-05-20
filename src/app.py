from flask import Flask, render_template, request, jsonify, make_response
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
import time
import os
import functools
import csv
from typing import List

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)




@app.route('/')
def index():
    return render_template('index.html')



# MQTT Related Stuff
# TODO - MAKE SURE TO RUN WITH 'python app.py' NOT 'flask run' since it does not start the socketio

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)

def connect_mqtt():
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()

@app.route('/socket.io.js')
def socketio_js():
    return app.send_static_file('socket.io.js')


@app.route('/get_folder_data', methods=['POST'])
def get_folder_data():
    folder_path: str|None = request.args.get("folder_path", None)
    if folder_path == None:
        return make_response(jsonify({'status': "failure", 'msg': "Folder Path Not Provided"}))
    
    
    isValidFolder = os.path.isdir(folder_path)
    
    print(folder_path, isValidFolder)
    
    if not isValidFolder:
        return make_response(jsonify({'status': "failure", 'msg': "Folder path is not a valid folder"}))
    
    fileData = []
    for filename in os.listdir(folder_path):
        
        file_timestamp = time.ctime(os.path.getctime(os.path.join(folder_path, filename)))
        
        num_lines = -1
        try:
            with open(os.path.join(folder_path, filename), "rb") as f:
                num_lines = sum(1 for _ in f)
        except OSError:
            print("Could not open file", filename)
            
        fileData.append({"filename": filename, "lines": num_lines, "ts": file_timestamp})
    
    return make_response(jsonify({'status': "success", 'msg': "Sent Folder Data", "data": fileData}))
        
        


@app.route('/check_watch_connection', methods=['POST'])
def check_watch_connection():
    watchID: str|None = request.args.get("watchID", None)
    if watchID == None:
        return make_response(jsonify({'status': "offline", 'msg': "Error: Watch ID not Provided"}))
    
    isWatchConnected: bool = checkWatchConnection(watchID)
    
    if isWatchConnected:
        return make_response(jsonify({'status': "online", 'msg': f"Watch is Connected: {watchID}"}))
    else:
        return make_response(jsonify({'status': "offline", 'msg': f"Failed to Connect: {watchID}"}))
    
    
        

@app.route('/start_data_collection', methods=['POST'])
def start_data_collection():
    watchID: str|None = request.args.get("watchID", None)
    if watchID == None:
        return make_response(jsonify({'status': "failure", 'msg': "Error: Watch ID not Provided"}))
    
    userID: str|None = request.args.get("userID", None)
    if userID == None:
        return make_response(jsonify({'status': "failure", 'msg': "Error: User ID not Provided"}))
    
    task: str|None = request.args.get("task", None)
    if task == None:
        return make_response(jsonify({'status': "failure", 'msg': "Error: Task not Provided"}))

    startMQTTCollection(userID, watchID, task)
    
    return make_response(jsonify({'status': "success", 'msg': f"Connected to MQTT Topics: {watchID}"}))        


@app.route('/stop_data_collection', methods=['POST'])
def stop_data_collection():
    watchID: str|None = request.args.get("watchID", None)
    if watchID == None:
        return make_response(jsonify({'status': "failure", 'msg': "Error: Watch ID not Provided"}))
    
    stopMQTTCollection(watchID)
    
    return make_response(jsonify({'status': "success", 'msg': f"Disconnected From MQTT Topics: {watchID}"}))        


def checkWatchConnection(watch_id: str, timeout=5) -> bool:
    """
    Check if a specific topic is receiving data.

    Args:
    watch_id (str): The ID of the watch.
    timeout (int): Time in seconds to wait for a message (Default 5s)

    Returns:
    bool: True if the topic is active, False otherwise.
    """
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    message_received = False

    def on_message(client, userdata, message):
        nonlocal message_received
        print(f"Message received on topic {message.topic}")
        message_received = True
        client.disconnect()  # Ensure disconnection after receiving a message

    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe(f"{watch_id}/gyroscope") # Any topic that we send data on

    client.loop_start()
    start_time = time.time()
    while not message_received and time.time() - start_time < timeout:
        time.sleep(0.1)  # Short sleep to yield control and wait efficiently

    client.loop_stop()
    client.disconnect()  # Ensure disconnection even if no message is received

    return message_received



def stopMQTTCollection(watchID):

    print(f"Stopping {watchID}")
    
    # Unsubscribe from MQTT topics for the watch ID
    topics = [
        f"{watchID}/accelerometer",
        f"{watchID}/gyroscope",
        f"{watchID}/heartrate",
        f"{watchID}/linear_acceleration"
    ]
    for topic in topics:
        print(f"Stopping listening on {topic}")
        mqtt_client.unsubscribe(topic)

def startMQTTCollection(userID: str, watchID: str, task: str) -> None:
    
    files_timestamp = int(time.time())
    file_prefix = f"{userID}_{task}_{watchID}_{files_timestamp}"
    
    mqtt_client.on_connect = functools.partial(on_connect, watchID=watchID)
    mqtt_client.on_message = functools.partial(on_message, watchID=watchID, file_prefix=file_prefix)
    
    # Subscribe to multiple topics based on the watch ID
    topics = [
        f"{watchID}/accelerometer",
        f"{watchID}/gyroscope",
        f"{watchID}/heartrate",
        f"{watchID}/linear_acceleration"
    ]
    for topic in topics:
        print(f"Listening on {topic}")
        mqtt_client.subscribe(topic)
        
# Callback for when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc, watchID):
    if rc == 0:
        # Subscribe to multiple topics based on the watch ID
        topics = [
            f"{watchID}/accelerometer",
            f"{watchID}/gyroscope",
            f"{watchID}/heartrate",
            f"{watchID}/linear_acceleration"
        ]
        for topic in topics:
            print(f"Listening on {topic}")
            mqtt_client.subscribe(topic)
    else:
        print(f"Failed to connect, return code: {rc}")
        
        
def on_message(client, userdata, message, watchID: str, file_prefix: str):
    topic = message.topic
    data_type = topic.split("/")[1]
    
    batch_data = message.payload.decode('utf-8')
    batch_data = batch_data.split("\n")

    full_filename = f"{file_prefix}_{data_type}"
    # print(batch_data, type(batch_data))
    saveToCSV(data_type, full_filename, data_type, batch_data)
    sendToChart(data_type, batch_data)
    
    
    
    
    
DATA_DIRECTORY = "data"
def saveToCSV(folder: str, filename: str, topic: str, batchData: list[str]) -> None:
    # Make sure directory path is valid
    directory = os.path.join(DATA_DIRECTORY, folder)
    os.makedirs(directory, exist_ok=True)

    # Create Full file path
    file_path = os.path.join(directory, f"{filename}.csv")
    file_exists = os.path.exists(file_path)
    
    header = get_csv_headers_from_topic(topic)
    
    with open(file_path, "a", newline='') as csv_file:
        csv_writer = csv.writer(csv_file)

        # Write the header only if the file did not exist and a header is provided
        if not file_exists and header is not None:
            csv_writer.writerow(header)

  
        # 2D array each row is a row for csv
        # Each column is a entry in each row
        csv_data = [row.split(',') for row in batchData]
        
        # for row in csv_data:
        #     row.append(str(relative_timestamp))

        csv_writer.writerows(csv_data)
        
        
def sendToChart(data_type: str, batch_data: list[str]):
    for line in batch_data:
        data = line.split(",")
        ax = data[0]
        ax_float_value = float(ax)
        socketio.emit(f'mqtt_data_{data_type}', {'data': ax_float_value})



    
def get_csv_headers_from_topic(topic: str) -> list[str]|None:
    """Ouputs the correct csv header for a specific topic of data

    Args:
        topic (str)

    Returns:
        list[str]: list of headers to be written to the csv
    """

    if(topic == "accelerometer"):
        return ["x(m/s^2)", "y(m/s^2)", "z(m/s^2)", "internal_ts", "watch_timestamp", "relative_timestamp"]

    if(topic == "gyroscope"):
        return ["x(rad)", "y(rad)", "z(rad)", "internal_ts", "watch_timestamp", "relative_timestamp"]

    if(topic == "heartrate"):
        return ["bpm", "internal_ts", "watch_timestamp", "relative_timestamp"]

    if(topic == "linear_acceleration"):
        return ["x(m/s^2)", "y(m/s^2)", "z(m/s^2)", "internal_ts", "watch_timestamp", "relative_timestamp"]
    
    return None
        
# def on_message(client, userdata, message, filename, watchID):
#     try:
#         topic_base = message.topic.split('/')[1]  # Extracts 'acceleration' or 'gyro' from the topic
#         directory = f"watch_data/{topic_base}_data/"  # Creates directory path based on topic
#         full_filename = f"{filename}_{topic_base}"  # Appends topic to the filename

#         data = message.payload.decode()
#         save_to_csv(data, directory, full_filename, watchID, get_csv_headers_from_topic(topic_base))
#     except Exception as e:
#         print(f"Error processing mqtt message: {e}")




# # Function to save data to CSV
# def save_to_csv(data, dir, filename, watchID, header=None):
#     # Correct directory name
#     directory = os.path.join(SAVED_DATA_DIRECTORY, dir)
    
#     os.makedirs(directory, exist_ok=True)

#     # Correct file path
#     file_path = os.path.join(directory, f"{filename}.csv")

#     # Check if file exists before opening it
#     file_exists = os.path.exists(file_path)
    
    
#     relative_timestamp = 0
#     # == Relative Timestamp == Initialize start_time if it's the first message
#     if mqtt_clients[watchID]["start_time"] is None:
#         mqtt_clients[watchID]["start_time"] = time.time()
#     else:
#         # Calculate relative timestamp
#         relative_timestamp = time.time() - mqtt_clients[watchID]["start_time"]
        
#     print(relative_timestamp)

#     with open(file_path, "a", newline='') as csv_file:
#         csv_writer = csv.writer(csv_file)

#         # Write the header only if the file did not exist and a header is provided
#         if not file_exists and header is not None:
#             csv_writer.writerow(header)

#         # Splite the gitant string blob into each row, still also just a big string
#         rows = data.split('\n')
        
        
#         # 2D array each row is a row for csv
#         # Each column is a entry in each row
#         csv_data = [row.split(',') for row in rows]
        
#         for row in csv_data:
#             row.append(str(relative_timestamp))

#         csv_writer.writerows(csv_data)
        
#     return file_path

#     # print(f"Data saved in CSV file: {file_path}")

# # Modified function to start data collection for specific user
# def start_data_collection(level, sub_level, userID, filename, watchID):
#     # Create a new MQTT client for the user
#     client = mqtt.Client()

#     # Set up callbacks
#     client.on_connect = partial(on_connect, watchID=watchID)
#     client.on_message = partial(on_message, filename=filename, watchID=watchID)
#     client.on_disconnect = on_disconnect
    


if __name__ == '__main__':
    connect_mqtt()  # Ensure MQTT connection is established
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
