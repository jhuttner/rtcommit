#!/usr/local/bin/python

# Written by Joseph Huttner - jhuttner@appnexus.com
# Licensed under the GNU General Public License
#
# Change Log
#
# Jan 7 - Initial version
# Jan 17 - Support for use as git subcommand, added support for id=0
# Feb 7 - Added support for committing against multiple tickets in one commit
# Feb 28 - "git rt" without ticket number uses ticket IDs from
#  					last time they were passed
# March 5 - Add history option with -b flag
#  					Usage "git rt -b 3" populates commit file w/ last 3 rt tix that were
# 					referenced in commit messages.

import getopt
import os
import shlex
import subprocess
import sys

try:
	import json
except:
	import simplejson as json

SUBJECT_FILE = '/tmp/rtsubject'
COMMIT_MSG_FILE = '/tmp/rtcommit'
HISTORY_FILE = os.path.join(os.getcwd(), 'rtcommit-history.json')

def get_ticket_subject(ticket_id):
	if int(ticket_id) == 0:
		return 'YourMessageHere'
	else:
		command = "rt show -t ticket " + ticket_id + " -f subject,id"
		subprocess.call(shlex.split(command), stdout=file(SUBJECT_FILE, "w"))
		subject = open(SUBJECT_FILE).readline().split(":", 1)[1].strip()
		return subject

def format_ticket_id(ticket_id):
	"""All commits not referencing a ticket should go to rt#00000."""
	if int(ticket_id) == 0:
		return '00000'
	else:
		return ticket_id

def make_tmp_commit_file(ticket_ids):
	# TODO - make the commit msg formatted correctly
	commit_msg_parts = []
	for tid in ticket_ids:
		formatted_tid = format_ticket_id(str(tid));
		msg = " ".join(["#rt#" + formatted_tid + ":", get_ticket_subject(tid)])
		commit_msg_parts.append(msg)
	commit_msg = '\n'.join(commit_msg_parts)
	handle = open(COMMIT_MSG_FILE, "w")
	handle.write(commit_msg)
	handle.close()

def update_history_file(current, newest):
	if not current:
		result = newest
	else:
		for _id in reversed(newest):
			if current[0] != _id and id != 0:
				current.insert(0, _id)
		result = current
	# write it out
	fobj = open(HISTORY_FILE, 'w')
	fobj.write(json.dumps(result))
	fobj.close()

def read_history_file():
	try:
		fobj = open(HISTORY_FILE, 'r')
		history = json.loads(fobj.read())
		fobj.close()
		return history
	except IOError:
		return []
	except ValueError:
		return []

def exec_source_control_command():
	command = 'git commit -a --edit -F /tmp/rtcommit'
	subprocess.call(shlex.split(command))

def main(argv):
	optlist, args = getopt.getopt(argv[0:], 'h:')
	cl_ticket_ids = args
	optlist = dict(optlist)
	history = read_history_file()
	if '-h' in optlist:
		# Need 'map' because unicode breaks everything
		from_history = map(str, history[:int(optlist['-h'])])
	else:
		from_history = []
	ticket_ids =  cl_ticket_ids + from_history
	if ticket_ids:
		make_tmp_commit_file(ticket_ids)
		update_history_file(history, cl_ticket_ids)
		exec_source_control_command()

if __name__ == '__main__':
	main(sys.argv[1:])
