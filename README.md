# RTCommit

A "git commit" wrapper for committing against RT tickets using a specific commit message format.
Optionally invokes a post-commit hook that sends XMPP messages (IMs) to recipients specified for that commit.

## Overview

Commits to AppNexus's source code all happen against a ticket in [RT](http://bestpractical.com/rt/).
Even issues that don't address an RT ticket directly use rt#0.  Our convention
is to paste the subject of the RT ticket into the commit message
so that the log is pretty and we can build release notes easily.

I got tired of pasting subjects in from the web browser all the time, so I wrote this script instead.

## Usage

From a git repo:

Pre-populate the commit message with subject from rt#12345.

	git rtcommit 12345

Pre-populate the commit message with subject from rt#12345 and rt#67890

	git rtcommit 12345 67890

Pre-populate the commit message with a blank subject and RT ticket ID 0

	git rtcommit 0

Same as earlier, but sends an XMPP message to the recipients specified in --blast provided commit executes successfully.

	git rtcommit 12345 --blast="sergey@xmpp.google.com, larry@xmpp.google.com" --msg="Thought you would like to know about this commit."

Same as previous, but looks in alias file at ~/xmpp-aliases.json to do addreessee lookups.  A speedup.

	git rtcommit 12345 --blast="sb,lp" --msg="Thought you would like to know about this commit."

## Dependencies

*  Python (I am using 2.6)
*  Ruby (I am using 1.9.2)
*  Command-line script for accessing RT (Included in this repository)
		You will know it works when you can type 'rt' on
		the command line and you get an 'rt>' prompt
*  An RT credentials file in your home directory.  Filename: .rtrc
		server https://url.of.your.rt.server
		user MyRTusername
		passwd MyRTpass
		externalauth 1

## Installation

* Inside a Git repository, create a .rtcommit folder.  Your per-repo files for rtcommit (history, blasts) will be stored here.

## Dependencies for optional XMPP (IM) component.

* [xmpppy](http://xmpppy.sourceforge.net/), a Python implementation of the XMPP protocol.  You will know it works when you can import 'xmpp' from the Python shell.
* An XMPP credentials file in your home directory.  Filename: xmpp-config.json
	{
	"username": "johns_username",
	"nickname": "John Smith",
	"password": "cGFzc3dvcmQ=",
	"client": "something.com",
	"server": "xmpp.something_else.net",
	"port": 5223
	}

* Optional - An XMPP aliases file in your home directory.  Filename: xmpp-aliases.json
	{
		"user": {
			"sb": "sergey@xmpp.google.com",
			"lp": "larry@xmpp.google.com"
		},
		"group": {
			"cr": "a_chat_room@xmpp.google.com"
		}
	}

* Your port may be 5222.  For help getting the client and server info, ask your OPS people.
* Note: In the config file, you must store your password as the base 64 encoded value.  This does not protect the password, but prevents accidental, clear-text password viewing.

	>>> import base64
	>>> base64.b64encode('password')
	'cGFzc3dvcmQ='
	>>> base64.b64decode('cGFzc3dvcmQ=')
	'password'

## Helpful commands

* Add to .gitignore of the repository using this tool.
	*rtcommit*
* Other:
	sudo ln -s PATH_TO_THIS_REPO/rtcommit.py /usr/local/bin/git-rtcommit
	sudo ln -s PATH_TO_THIS_REPO/rt /usr/local/bin/rt
