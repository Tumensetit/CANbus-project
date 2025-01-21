#!/bin/bash

# TODO: check if parameters are given
RAWDATA=$1	# pcang -file
DST=$2

echo "$(date) - Starting conversion.."
tshark -r $RAWDATA -T fields -e frame.time_epoch -e can -e data 2>&1 > $DST
echo "$(date) - Conversion done! Output stored at $DST"
