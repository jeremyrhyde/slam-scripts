import asyncio
import argparse
import os
import pytz

from datetime import datetime
from viam.app.viam_client import ViamClient
from viam.rpc.dial import DialOptions, Credentials
from viam.proto.app.data import Filter

async def main(delete_data):
    input_dir = '/Users/jeremyhyde/Downloads/LIDAR_OFFICE_DATA'
    data_directory = input_dir + '/data'

    component_type="camera"
    method_name="NextPointCloud"
    part_id = "6d0f936c-4518-474a-acc8-86c8f12fad39"
    component_name = "rplidar"

    dial_opts = DialOptions(
        auth_entity='data-main.fstmokoxld.viamstg.cloud',
        credentials=Credentials(
            type='robot-location-secret',
            payload='n9e1p4way31gud8r37ghb6ozrwdiot9ak6mcfdll8xw6xjes'
        )
    )
    app_client = await ViamClient.create_from_dial_options(dial_opts, "app.viam.dev")
    data_client = app_client.data_client

    # Delete existing data.
    if delete_data:
        await data_client.delete_binary_data_by_filter(Filter(component_name=component_name))
        print("Deleted old data associated with component_name: " + component_name)

    numFiles = len(os.listdir(data_directory))
    index = 0
    for filename in os.listdir(data_directory):
        # if index > 10:
        #     break
        file_path = os.path.join(data_directory, filename)
        print("Uploading Binary File " + str(index) + "/" + str(numFiles))
        if os.path.isfile(file_path):
            print("Filename: " + filename)

        datetime_str = filename[:filename.find("Z")+1]
        
        est = pytz.timezone('US/Eastern')
        datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.utc)
        datetime_obj = datetime_obj.astimezone(tz = est)
        print("Time: " + str(datetime_obj)+ " (" + str(datetime_obj.tzinfo) + ")\n")
        
        file = open(file_path,mode='rb')
        data = file.read()
        file.close()

        try:
            await data_client.binary_data_capture_upload(
                part_id=part_id,
                component_type=component_type,
                component_name=component_name,
                method_name=method_name,
                binary_data=data,
                data_request_times=(datetime_obj, datetime_obj) ,
            )
            print("Result: Successfully uploaded PCD data\n")
        except Exception as e: 
            print("Result: Failed to upload " + method_name + " data due to upload exception")
            print(e)

        index = index +1 

    print("Upload complete")
    app_client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-delete_past_data')
    args = parser.parse_args()
    delete_data  = False
    if args.delete_past_data == "true":
        delete_data = True
    asyncio.run(main(delete_data))