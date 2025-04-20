#!/bin/zsh

#### Example extension attribute to get that Munki's been running okay ####

# If it's been more than this many days since the last Munki run, consider unhealthy
days_threshold=5
# Convert days to seconds for easier comparison
seconds_threshold=$days_threshold*24*60*60

report_plist='/Library/Managed Installs/ManagedInstallReport.plist'

plistbuddy='/usr/libexec/PlistBuddy'

# Initialize errors variable
errors=''

# Check the report plist exists
if [[ ! -f $report_plist ]]; then
	errors="$report_plist doesn't exist, so Munki hasn't run"
else
	# Get errors array items (if any)
	index=0
	until ! $plistbuddy -c "Print :Errors:$index" "$report_plist"  > /dev/null 2>&1; do
		if [[ $index -gt 0 ]]; then
			errors+=', '
		fi
		errors+=$($plistbuddy -c "Print :Errors:$index" "$report_plist")
		index=$(( index + 1))
	done
	# If there are no errors, see the last time Munki was run
	if [[ $errors == '' ]]; then
		last_run=$(/usr/bin/defaults read $report_plist StartTime)
		last_epoch=$(/bin/date -j -f "%Y-%m-%d %H:%M:%S +0000" "$last_run" +%s)
		current_epoch=$(/bin/date +%s)
		date_threshold=$(($current_epoch-$seconds_threshold))
		if [[ $last_epoch -lt $date_threshold ]]; then
			errors="Last Munki run was $last_run"
		else
			echo "Last Munki run was $last_epoch and threshold was $date_threshold"
		fi
	fi
fi

if [[ $errors == '' ]]; then
	/bin/echo "<result>Munki healthy</result>"
else
	/bin/echo "<result>Unhealthy: $errors</result>"
fi
