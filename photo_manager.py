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
parser.add_argument('location', help='The location of the photos to be renamed')
parser.add_argument('path', help='The path to the location '
                                         'where the photos will be copied.')
parser.add_argument('--dry_run', help='This flag will run the program but will not copy the files.', action="store_true")
args = parser.parse_args()
if args.dry_run:
    dry_run_ = True

album_name = args.album_name
location = args.location
path = args.path

# Read in photos and meta data
print("Reading in photos and meta data...")

#Set up and execute the exiftool command
exif_cmd=list()

if plat == "win32" or plat == "win64":
    exif_cmd = "exiftool.exe -datetimeoriginal -csv "+location+"*.jpg > pm_output.txt"
else:
    exif_cmd = "exiftool -datetimeoriginal -csv "+location+"*.jpg > pm_output.txt"

system(exif_cmd)

file_names=list()
dates=list()
errors = 0         # Count the number of files which do not have Date/Time Metadata
error_list=list()  # List of files without Date/Time Metadata

with open("pm_output.txt") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['DateTimeOriginal'] == '':
            print("Error: No \"DateTimeOriginal\" MetaData for " + row['SourceFile'])
            error_list.append(row['SourceFile'])
            errors += 1
        else:
            file_names.append(row['SourceFile'])
            dates.append(datetime.strptime(row['DateTimeOriginal'],"%Y:%m:%d %H:%M:%S"))

#print(file_names)
#print(dates)

# Preserve file extentions
# Fix backslashes in Windows
exten=list()
count = 0
for x in file_names:
    match = re.search(r'.(\w+)$', x)
    exten.append(match.group(0))
    file_names[count] = re.sub('/','\\\\',x)
    count = count+1
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
count_copy = 0
if dry_run_:
    print("The non-dry_run version will execute the following commands:")

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
    if dry_run_:
        print(cmd)
    else:
        system(cmd)
        count_copy = count_copy + 1

# Report number of photos copied and errors
print("Number of photos copied:", count_copy)
if errors > 0:
    print("Number of errors:", errors)
    print("Files not copied:")
    for a in error_list:
        print('\t'+a)

if dry_run_:
    print("This was a dry run! No copies were made!")

# Cleanup

if plat == "win32" or plat == "win64":
    system("del pm_output.txt")
else:
    system("rm pm_output.txt")
