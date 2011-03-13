# RTCommit

A "git commit" wrapper for committing against RT tickets using a specific commit message format.
Optionally invokes a post-commit hook that sends XMPP messages (IMs) to recipients specified for that commit.

## Overview

Commits to AppNexus's source code all happen against a ticket in [RT](http://bestpractical.com/rt/).
Even issues that don't address an RT ticket directly use rt#0.  Our convention
is to paste the subject of the RT ticket into the commit message
so that the log is pretty and we can build release notes easily.

I got tired of pasting subjects in from the web browser all the time, so I wrote this script instead.

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

Your port may be 5222.  For help getting the client and server info, ask your OPS people.
Note: In the config file, you must store your password as the base 64 encoded value.  This does not protect the password, but prevents accidental, clear-text password viewing.

	>>> import base64
	>>> base64.b64encode('password')
	'cGFzc3dvcmQ='
	>>> base64.b64decode('cGFzc3dvcmQ=')
	'password'

## Helpful commands

*  sudo ln -s PATH_TO_THIS_REPO/rtcommit.py /usr/local/bin/git-rtcommit
*  sudo ln -s PATH_TO_THIS_REPO/rt /usr/local/bin/rt
