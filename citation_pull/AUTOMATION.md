Citation Management Automation
--------------------------
This document details the mechanisms for nightly automated updates to the Tax-Calculator citations within its Jupyter Book documentation. This process (and this documentation) is almost identical to those used by Peter Metz when [building the catalog of PSLModels.org](https://github.com/PSLmodels/PSL-Infrastructure/blob/fd03be906313702d61bc30267da156ff95d1ec97/Tools/Catalog-Builder/AUTOMATION.md).

`taxcalc_citation_pull.sh` is a bash script that runs a `curl` command to pull the latest `.bibtex` file containing Tax-Calculator citations from Zotero. The shell script then commits changes to a new local branch, pushes the new local branch, pulls any changes from the new branch into the master branch, and finally deletes the new branch locally and remotely.

`taxcalc_citation_pull.sh` is run nightly with a program called [Launchd](http://www.launchd.info), an open-source service management framework for managing scripts. To use Launchd, the user creates an agent, a program that runs in the background without requiring user input, that is specified in an XML file called a property list (plist) and saves the plist in the follow folder: `~/Library/LaunchAgents`. If the user's computer is asleep or shut down when the Launchd job is scheduled, the job will run once the computer is awake. To run the bash script every night at 1am, the plist should look similar to the following:

```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN"
           "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>[PLIST LABEL]</string>
  <key>Program</key>
    <string>[LOCATION OF BASH SCRIPT]</string>
  <key>ProgramArguments</key>
  <array>
    <string>./update-catalog.sh</string>
  </array>
  <key>StandardOutPath</key>
  <string>/tmp/stdout.log</string>
  <key>StandardErrorPath</key>
  <string>/tmp/stderr.log</string>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>1</integer>
    <key>Minute</key>
    <integer>0</integer>
  </dict>
</dict>
</plist>
```

Once the plist file is specified and saved, the user types the following into the command line to load the agent:

`launchctl load ~/Library/LaunchAgents/[PLIST FILENAME]`

To unload the agent, the user types:

`launchctl unload ~/Library/LaunchAgents/[PLIST FILENAME]`
