#!/usr/local/munki/Python.framework/Versions/Current/bin/python3

'''
To be called from Jamf Self-Service policy to mark a Munki optional install
for installation and then launch up Managed Software Center, so the user
can see what's going on
'''

import os
import plistlib
import subprocess
import sys

def main():
    # Munki item to add (fill in the name of the Munki item, not necessarily the display name)
    # Don't just leave this as literally NAMEOFMUNKIITEMTOADD
    item_to_add = 'NAMEOFMUNKIITEMTOADD'

    # Users to ignore
    ignored_users = [ 'root', '', '_mbsetupuser' ]

    # Path to SelfServeManifest
    manifest_location = '/Library/Managed Installs/manifests/SelfServeManifest'

    # Add the item as an optional install
    if os.path.isfile(manifest_location):
        # Try to read the current plist contents
        try:
            f = open(manifest_location, 'rb')
        except:
            print("ERROR: cannot open {} for reading".format(manifest_location))
            sys.exit(1)
        try:
            manifest_contents = plistlib.load(f)
        except:
            print("ERROR: cannot read plist contents from {}".format(manifest_location))
        f.close()
        # Initialize test variable
        contents_changed = 0
        if 'managed_installs' not in manifest_contents.keys():
            manifest_contents[ 'managed_installs' ] = [ item_to_add ]
            contents_changed = 1
        elif isinstance(manifest_contents[ 'managed_installs' ], list):
            if item_to_add not in manifest_contents[ 'managed_installs' ]:
                manifest_contents[ 'managed_installs' ].append(item_to_add)
                contents_changed = 1
        else:
            print("ERROR: Managed Installs is not an array")
            sys.exit(1)
        # There's no point in writing back the changes to the plist
        # if nothing actually changed, so double-check there were content changes 
        if contents_changed == 1:
            # Try to write the changes back
            try:
                f = open(manifest_location, 'wb')
            except:
                print("ERROR: cannot open {} for writing".format(manifest_location))
                sys.exit(1)
            try:
                plistlib.dump(manifest_contents, f)
            except:
                print("ERROR: cannot write plist contents back to {}".format(manifest_location))
                sys.exit(1)
            f.close()

        # Whether there are changes or not, we still want to launch up MSC so the user can see what's going on
        # Get the currently logged in user
        cmd = [ '/usr/bin/stat', '-f%Su',  '/dev/console' ]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf8')
        out, err = p.communicate()
        if err:
            print("ERROR: Unable to determine currently logged in user")
            sys.exit(1)
        else:
            current_user = str(out).strip()

        # Open up MSC, so the user can see what's going on
        if current_user not in ignored_users:
            # If there were any changes, open up the updates
            if contents_changed == 1:
                open_munki = 'open munki://updates'
            # If there were no changes, remind the user that this item is already installed
            else:
                open_munki = 'open munki://detail-' + item_to_add + '.html'
            cmd = [ '/usr/bin/su', '-l', current_user, '-c', open_munki ]
            subprocess.call(cmd)
            # If there were any changes, also do an --auto run, so the item actually installs
            if contents_changed == 1:
                # Do a background Munki run
                cmd = [ '/usr/local/munki/managedsoftwareupdate', '--auto' ]
                subprocess.call(cmd)

    else:
        print("ERROR: {} does not exist".format(manifest_location))
        sys.exit(1)

if __name__ == "__main__":
    main()