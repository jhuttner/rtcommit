## Overview

Commits to AppNexus's source code all happen against a ticket in RT.  
Even issues that don't address an RT directly use rt 0.  The convention
is to paste the subject of the rt ticket into the commit msg
so that the log is pretty and we can build release notes easily.

I got tired of pasting subjects in from the web browser all the time,
so I wrote this script instead.  

"Eliminate the mundane so you can focus on the insane."
-Me

## Dependencies

1.  Python
1.  Ruby
1.  Command-line script for accessing RT.
		You will know it works when you can type 'rt' on
		the command line and you get an 'rt>' prompt
1.  .rtrc file with your RT creds.  Required for (3).

## Helpful commands

1.  sudo ln -s PATH_TO_THIS_REPO/rtcommit.py /usr/local/bin/rtcommit
1.  sudo ln -s PATH_TO_THIS_REPO/rt /usr/local/bin/rt
1.  sudo ln -s PATH_TO_THIS_REPO/.rtrc ~/
1.  Inside .gitconfig file
[alias]
  rt = !rtcommit
