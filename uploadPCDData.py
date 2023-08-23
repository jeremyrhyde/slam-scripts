import asyncio
import time
import os
import json
from datetime import datetime
import re

from google.protobuf.timestamp_pb2 import Timestamp

from viam.app.app_client import AppClient
from viam.app.viam_client import ViamClient
from viam.rpc.dial import DialOptions, Credentials
from viam.proto.app.data import Filter, CaptureInterval

async def main():
    part_id = "819994b1-82c2-404b-ae43-93cdbdd328ba"
    input_dir = 'POCDATA5'
    directory = input_dir + 'data'
    component_name = "POCDATA5_lidar"

    dial_opts = DialOptions(
        auth_entity='jhlaptop-main.h63500gc3x.viam.cloud',
        credentials=Credentials(
            type='robot-location-secret',
            payload='sh4zytfyfqgqwhatm7me1581rzeb3b9rgn13puub2v5tdeee'
        )
    )
    app_client = await ViamClient.create_from_dial_options(dial_opts)
    data_client = app_client.data_client

    # Delete existing data.
    await data_client.delete_binary_data_by_filter(Filter(component_name=component_name))
    print("Deleted old data associated with " + component_name)

    numFiles = len(os.listdir(directory))
    index = 0
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        print("Uploading File " + str(index) + "/" + str(numFiles))
        if os.path.isfile(file_path):
            print("Filename: " + file_path)

        regex_pattern = r'_(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}\.\d{4})Z\.pcd'
        match = re.search(regex_pattern, filename)

        datetime_obj = datetime
        if match:
            date_str, time_str = match.groups()

            # Replace '/' with ':' in the time string to match datetime format
            time_str = time_str.replace('/', ':')
            
            datetime_str = f'{date_str}T{time_str}Z'
            datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')

            file = open(file_path,mode='rb')
            data = file.read()
            file.close()

            try:
                await data_client.binary_data_capture_upload(
                    part_id=part_id,
                    component_type="camera",
                    component_name=component_name,
                    method_name="NextPointCloud",
                    binary_data=data,
                    data_request_times=(datetime_obj, datetime_obj) ,
                )
                print("Result: Successfully uploaded PCD data\n")
            except:
                print("Result: Failure due to upload exception\n")

        else:
            print("Result: Failure to find match\n")

        index = index +1 

    print("Upload complete")
    app_client.close()

if __name__ == "__main__":
    asyncio.run(main())