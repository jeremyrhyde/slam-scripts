import time
import os
import json
from datetime import datetime
import re
import sys

from google.protobuf.timestamp_pb2 import Timestamp

from viam.app.app_client import AppClient
from viam.app.viam_client import ViamClient
from viam.rpc.dial import DialOptions, Credentials
from viam.proto.app.data import Filter, CaptureInterval

def main(infile, outfile):
    
    keep_phrases = ["| LIDAR |", "|  IMU  |"]

    with open(infile) as f:
        f = f.readlines()

    out = open(outfile, "w")

    for line in f:
        for phrase in keep_phrases:
            if phrase in line:
                offset = line.find('sensorprocess') + 34
                out.write(line[offset:])



if __name__ == "__main__":
    infile = sys.argv[1]
    outfile = sys.argv[2]
    main(infile, outfile)