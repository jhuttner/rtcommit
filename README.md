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

The following commands would be executed at the top level of a Git repository.

Pre-populate the commit message with subject from rt#12345:

	git rtcommit 12345

Pre-populate the commit message with subject from rt#12345 and rt#67890:

	git rtcommit 12345 67890

Pre-populate the commit message with a blank subject and RT ticket ID 0:

	git rtcommit 0

Same as earlier, but sends an XMPP message to the recipients specified in --blast provided commit executes successfully.  Recipients are XMPP usernames:

	git rtcommit 12345 --blast="harry@appnexus.com, larry@appnexus.com: Check out this optimization."

Same as previous, but looks in alias file at ~/xmpp-aliases.json to do addressee lookups (a shortcut):

	git rtcommit 12345 --blast="hh,L: Check out this optimization."

## Installation

* At the top level of a Git repository, run the following command:
		git rtcommit init

## Uninstall

* At the top level of the Git repository that has RT Commit installed, run the following command:
		rm -rf .rtcommit

## Dependencies

*  Python (I am using 2.6)
*  Ruby (I am using 1.9.2)
*  Command-line script for accessing RT (included in this repository). You'll know it works when you can type 'rt' on the command line and you get an 'rt>' prompt:
		01:~ jhuttner$ rt
		rt>
*  An RT credentials file in your home directory.
		# ~/.rtrc

		server https://url.of.your.rt.server
		user MyRTusername
		passwd MyRTpass
		externalauth 1

## Dependencies for optional XMPP (IM) component.

* [xmpppy](http://xmpppy.sourceforge.net/), a Python implementation of the XMPP protocol.  You'll know it works when you can import 'xmpp' from the Python shell.  It will chirp a bit about deprecated modules:
		>>> import xmpp
		/usr/local/lib/python2.6/site-packages/xmpppy-0.5.0rc1-py2.6.egg/xmpp/auth.py:24: DeprecationWarning: the sha module is deprecated; use the hashlib module instead
		/usr/local/lib/python2.6/site-packages/xmpppy-0.5.0rc1-py2.6.egg/xmpp/auth.py:26: DeprecationWarning: the md5 module is deprecated; use hashlib instead
		>>>

* An XMPP credentials file in your home directory.  Your port may be 5222.  For help getting the client and server info, ask your server guys.
		# ~/xmpp-config.json

		{
			"username": "johns_username",
			"nickname": "John Smith",
			"password": "cGFzc3dvcmQ=",
			"client": "something.com",
			"server": "xmpp.something_else.net",
			"port": 5223
		}

* Optional - An XMPP aliases file in your home directory.  Groups are for multi-user chat.
		# ~/xmpp-aliases.json

		{
			"user": {
				"hh": "harry_hannukkah@appnexus.com",
				"L": "larry@appnexus.com"
			},
			"group": {
				"eng": "engineering_chat_room@appnexus.com"
			}
		}


Note: In the config file, you must store your password as the base-64 encoded value.  This prevents accidental, clear-text password viewing.

		>>> import base64
		>>> base64.b64encode('password')
		'cGFzc3dvcmQ='
		>>> base64.b64decode('cGFzc3dvcmQ=')
		'password'

## Helpful commands

* Add to .gitignore of the repository using this tool.
		*rtcommit*
* Get commands into your PATH:
		sudo ln -s PATH_TO_THIS_REPO/rtcommit.py /usr/local/bin/git-rtcommit
		sudo ln -s PATH_TO_THIS_REPO/rt /usr/local/bin/rt
