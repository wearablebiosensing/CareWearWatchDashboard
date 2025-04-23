
import time
import os
import functools
import csv
import datetime
from typing import List

DATA_DIRECTORY = "data"

def get_csv_headers_from_topic(topic: str) -> list[str]|None:
    """Ouputs the correct csv header for a specific topic of data

    Args:
        topic (str)

    Returns:
        list[str]: list of headers to be written to the csv
    """

    if(topic == "accelerometer"):
        return ["x(m/s^2)", "y(m/s^2)", "z(m/s^2)", "internal_ts", "watch_timestamp",]

    if(topic == "gyroscope"):
        return ["x(rad)", "y(rad)", "z(rad)", "internal_ts", "watch_timestamp"]

    if(topic == "heartrate"):
        return ["bpm", "internal_ts", "watch_timestamp"]

    if(topic == "linear_acceleration"):
        return ["x(m/s^2)", "y(m/s^2)", "z(m/s^2)", "internal_ts", "watch_timestamp"]
    
    return None
        

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
    