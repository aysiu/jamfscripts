#!/usr/local/munki/munki-python

'''
When Jamf exports an applications report, it will leave empty rows if the versions below
are the same as the version above. This script fills in those empty rows for application
title and application version.

I tested this with Munki's python 3.9.2, but you may be able to use this fine with
other Python 3 versions
'''

import argparse
import csv
import os
from sys import exit
from tempfile import mkstemp

def get_options():
    parser = argparse.ArgumentParser(description='Fills in application version gaps in '
        'Application Report export from Jamf')
    parser.add_argument('--csv', required=True, help='Path to .csv export from Jamf')
    parser.add_argument('--app', help='Column number of Application Title (usually 1)')
    parser.add_argument('--vers', help='Column number of Application Version (usually 2)')
    args = parser.parse_args()
    if args.csv:
        csv = args.csv
    else:
        print('ERROR: You must specify a .csv using the --csv flag')
        exit(1)
    if not os.path.isfile(csv):
        print(f'ERROR: {csv} does not exist')
        exit(1)
    if args.app:
        app = (int(args.app)-1)
    else:
        app = 0
    if args.vers:
        vers = (int(args.vers)-1)
    else:
        vers = 1
    if app == vers:
        print('ERROR: The application title column and application version column '
            'cannot be the same column')
        exit(1)
    return csv, app, vers

def main():
    # Get CSV file
    csv_path, app_column, version_column = get_options()

    # Set up list to gather contents from CSV object
    csv_contents = []

    # Get CSV contents
    print(f'Getting contents of {csv_path}...')
    try:
        csv_file = open(csv_path, 'r')
    except:
        print(f'ERROR: Unable to open {csv_path}')
        exit(1)
    try:
        csv_lines = csv.reader(csv_file)
    except:
        print(f'ERROR: Unable to get contents of {csv_path}')
        exit(1)
    for csv_line in csv_lines:
        csv_contents.append(csv_line)
    csv_file.close()

    # Create a temporary file to write back to
    print('Creating temporary file to output filled-in data...')
    temp_descriptor, temp_path = mkstemp()
    try:
        temp_file = open(temp_path, 'w')
    except:
        print('ERROR: Unable to create temporary random file to write changes to')
        exit(1)
    csv_write = csv.writer(temp_file)
    # Set a counter, so it's easy to get the previous line
    counter = 0
    # Loop through the lines of the old CSV
    while counter < len(csv_contents):
        # Check to see if the columns are out of range
        if app_column > len(csv_contents[counter]):
            print(f"ERROR: You specified the app column as {app_column}, but there aren't "
                "that many columns in each row")
            exit(1)
        elif version_column > len(csv_contents[counter]):
            print(f"ERROR: You specified the app column as {version_column}, but there "
                "aren't that many columns in each row")
            exit(1)
        # If the first column is blank...
        if csv_contents[counter][app_column] == '':
            # ... set it to be the same as the previous line's
            csv_contents[counter][app_column] = csv_contents[(counter-1)][app_column]
        # If the second column is blank...
        if csv_contents[counter][version_column] == '':
            # ... set it to be the same as the previous line's
            csv_contents[counter][version_column] = csv_contents[(counter-1)][version_column]
        csv_write.writerow(csv_contents[counter])
        counter += 1
    temp_file.close()

    # Delete the original file
    print('Deleting original .csv file...')
    try:
        os.remove(csv_path)
    except:
        print(f'ERROR: Unable to remove original file {csv_path}')
        exit(1)

    # Move the temp file to where the original file used to be
    print(f'Moving temporarily file to original .csv file location of {csv_path}...')
    try:
        os.rename(temp_path, csv_path)
    except:
        print(f'ERROR: Unable to move temp file {temp_path} to {csv_path}')
        exit(1)

if __name__ == '__main__':
    main()
