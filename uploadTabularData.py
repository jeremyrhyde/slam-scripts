import asyncio
import argparse
import json
import ndjson
import os
import pytz

from datetime import datetime
from viam.app.viam_client import ViamClient
from viam.rpc.dial import DialOptions, Credentials

async def main(delete_data):
    input_dir = '/Users/jeremyhyde/Downloads/IMU_OFFICE_DATA'
    data_directory = input_dir + '/data'
    metadata_directory = input_dir + '/metadata'
    org_id = "fce007ac-a1f1-4db8-bfda-e08c2dee89fe"

    component_type="movement_sensor"
    component_name = "imuwit"
    part_id = "6d0f936c-4518-474a-acc8-86c8f12fad39"
    
    dial_opts = DialOptions(
        auth_entity='data-main.fstmokoxld.viamstg.cloud',
        credentials=Credentials(
            type='robot-location-secret',
            payload='n9e1p4way31gud8r37ghb6ozrwdiot9ak6mcfdll8xw6xjes'
        )
    )
    app_client = await ViamClient.create_from_dial_options(dial_opts, "app.viam.dev")
    data_client = app_client.data_client

    if delete_data:
        await data_client.delete_tabular_data(org_id, 1)
        print("Deleted old data associated with org: " + org_id)

    # Metadata
    numMetadataFiles = len(os.listdir(metadata_directory))
    metadata = []
    for filename in os.listdir(metadata_directory):
        file_path = os.path.join(metadata_directory, filename)
        if os.path.isfile(file_path):
            print("Metadata Filename: " + file_path)

        with open(file_path) as f:
            metadata.append(json.load(f))

    print()

    # Data
    filename = "data.ndjson"
    file_path = os.path.join(data_directory, filename)
    if os.path.isfile(file_path):
        print("Filename: " + file_path)
    with open(file_path) as f:
        dataset = ndjson.load(f)
    
    index = 0
    for data in dataset:
        # if index > 10:
        #     break
        print("Uploading Tabular File " + str(index) + "/" + str(len(dataset)))
        timeReceived = data["TimeReceived"]
        metadata_index = data["MetadataIndex"]
        method_name = metadata[metadata_index]["methodName"]

        data_point = {"X": data["X"], "Y": data["Y"], "Z": data["Z"]}
        est = pytz.timezone('US/Eastern')
        datetime_obj = datetime.fromtimestamp(timeReceived["seconds"]+ timeReceived["nanos"]/1000000000).replace(tzinfo=est)
        print(data)
        print("Time: " + str(datetime_obj)+ " (" + str(datetime_obj.tzinfo) + ")\n")

        try: 
            await data_client.tabular_data_capture_upload(
                part_id=part_id,
                component_type=component_type,
                component_name=component_name,
                method_name=method_name, 
                tabular_data=[data_point],
                data_request_times=[(datetime_obj, datetime_obj)],
            )
            print("Result: Successfully uploaded " + method_name + " data")
        except Exception as e: 
            print("Result: Failed to upload " + method_name + " data due to upload exception")
            print(e)

        index = index + 1

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