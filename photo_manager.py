# Copyright (c) 2018-2019 Adrian Serio
#
#   Distributed under the Boost Software License, Version 1.0. 
#   (See accompanying file LICENSE_1_0.txt or copy at 
#   http://www.boost.org/LICENSE_1_0.txt)

import sys
import argparse
import re
import csv
from datetime import datetime, timedelta
from math import log10
from os import system, path as os_path

# Discover Patform
plat = sys.platform

# Setup
parser = argparse.ArgumentParser(description=
     "Hi! I am your photo album manager. If you provide me with an album name "
     "and a path I will rename all photos (.jpg) in the current directory to the "
     "album name and append a number to the end based on the time the photo "
     "was taken. These photos will be copied to the path supplied. ")

parser.add_argument('album_name', help='The first compoent of the photos new name')
parser.add_argument('path', help='The path to the location '
                                         'where the photos will be copied.')
args = parser.parse_args()

album_name = args.album_name
path = args.path

# Handle Windows
if plat == "win32" or plat == "win64":
    path='"'+path+'\\"'
#print(path)

# Read in photos and meta data
print("Reading in photos and meta data...")

if plat == "win32" or plat == "win64":
    system("exiftool.exe -datetimeoriginal -csv *.jpg > pm_output.txt")
else:
    system("exiftool -datetimeoriginal -csv *.jpg > pm_output.txt")

file_names=list()
dates=list()

with open("pm_output.txt") as f:
    reader = csv.DictReader(f)
    for row in reader:
        file_names.append(row['SourceFile'])
        dates.append(datetime.strptime(row['DateTimeOriginal'],"%Y:%m:%d %H:%M:%S"))

#print(file_names)
#print(dates)

# Preserve file extentions
exten=list()
for x in file_names:
    match = re.search(r'.(\w+)$', x)
    exten.append(match.group(0))
#print (exten)

# Check that lists are the same length
if len(file_names) == len(dates):
    print("Parsing complete! Photo Manager will rename", len(file_names), "photos.")
else:
    print("Parsing error!")

# Determine the padding for the number of days
diff = max(dates)-min(dates)
if diff.days == 0:
    pad = 1
else:
    pad = int(log10(diff.days))+1

print("The supplied photos span", diff.days, "days.")

# Create the list of new names
new_name=list()
for x in dates:
    d = x-min(dates)
    new_name.append(album_name+"_"+str(d.days).zfill(pad)+str(x.hour).zfill(2)+str(x.minute).zfill(2)+str(x.second).zfill(2))
#print (new_name)

# Rename photos
for i in range(len(file_names)):
    # Check for duplicate names
    #  Escape Whitespace
    if " " in file_names[i]:
        if plat == "win32" or plat == "win64":
            file_names_w = "\"" + file_names[i] + "\""
        else:
            file_names_w = file_names[i].replace(' ','\ ')
    else:
        file_names_w = file_names[i]
    #print (repr(file_names_w))
    if os_path.exists(path[1:-1] + new_name[i] + exten[i]):
        tag = 2
        new_name[i] += "_" + str(tag)
        while os_path.exists(path[1:-1] + new_name[i] + exten[i]):
            tag += 1
            # Remove the previous tag and underscore. int(log10(tag))
            #  will return 0 for tags <10, 1 for tags <100 etc.
            new_name[i] = new_name[i][:-(int(log10(tag))+2)]
            new_name[i] += "_" + str(tag)
    if plat == "win32" or plat == "win64":
        cmd = "copy " + file_names_w + " " + path + new_name[i] + exten[i]
    else:
        cmd = "cp " + file_names_w + " " + path + new_name[i] + exten[i]
    print(cmd)
    system(cmd)

# Cleanup

if plat == "win32" or plat == "win64":
    system("del pm_output.txt")
else:
    system("rm pm_output.txt")
