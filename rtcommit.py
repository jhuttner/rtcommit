#!/usr/local/bin/python

# Written by Joseph Huttner -- jhuttner@appnexus.com
# Licensed under the GNU General Public License
#
# Change Log
#
# Jan 7, 2011.
#   First release.  Commit against an RT ticket and have the
#   commit message automatically populate with the RT subject.
#
# Jan 17
#   Add support for use as Git subcommand
#   Add support for rt#id=0
#
# Feb 7 -
#   Add support for committing against multiple tickets in one commit.
#
# Feb 28
#   "git rt" without ticket number uses ticket IDs from
#   last time they were passed
#
# March 5
#   Add history option with -b flag
#   Usage "git rt -b 3" populates commit file w/ last 3 rt tix that were
#   referenced in commit messages.  (Does not work for rt=0)
#
# March 12
#   Add xmpp capability.  Requires Git post commit hook.
#   Note: Once I switch off of git-svn the post commit hook will become a post
#   update hook.

import base64
from datetime import datetime
import getopt
import os
import shlex
import subprocess
import sys
try:
  import json
except:
  import simplejson as json

import xmpp

TMP_FILE = '/tmp/rtcommit'
RT_HISTORY_FILE = os.path.join(os.getcwd(), '.rtcommit/rt-history.json')
BLAST_FILE = os.path.join(os.getcwd(), '.rtcommit/blast.json')
ALIAS_FILE = os.path.join(os.getcwd(), '.rtcommit/alias.json')
XMPP_CONFIG_FILE = os.path.join(os.getcwd(), '.rtcommit/xmpp-config.json')

################################################################################
# Helper functions

def read(path, default='', as_json=False):
  try:
    fobj = open(path, 'r')
    data = fobj.read()
    fobj.close()
    if as_json:
      data = json.loads(data)
    return data
  except IOError:
    return default
  except ValueError:
    return default

def write(path, data, as_json=False):
  fobj = open(path, 'w')
  if as_json:
    data = json.dumps(data)
  fobj.write(data)
  fobj.close()

################################################################################
# RT functions

def format_ticket_id(ticket_id):
  return '00000' if int(ticket_id == 0) else ticket_id

def get_ticket_subject(ticket_id):
  if int(ticket_id) == 0:
    return 'YourMessageHere'
  else:
    command = 'rt show -t ticket ' + ticket_id + ' -f subject,id'
    subprocess.call(shlex.split(command), stdout=file(TMP_FILE, 'w'))
    subject = open(TMP_FILE).readline().split(":", 1)[1].strip()
    return subject

def make_tmp_commit_file(ticket_ids):
  # TODO - make the commit msg formatted correctly
  commit_msg_parts = []
  for tid in ticket_ids:
    formatted_tid = format_ticket_id(str(tid));
    msg = " ".join(['#rt#' + formatted_tid + ':', get_ticket_subject(tid)])
    commit_msg_parts.append(msg)
  commit_msg = '\n'.join(commit_msg_parts)
  write(TMP_FILE, commit_msg)

def update_history_file(current, newest):
  if not current:
    result = newest
  else:
    for _id in reversed(newest):
      if current[0] != _id and id != 0:
        current.insert(0, _id)
    result = current
  write(RT_HISTORY_FILE, result, True)

def exec_git_commit():
  command = 'git commit -a --edit -F /tmp/rtcommit'
  subprocess.call(shlex.split(command))

################################################################################
# Blast functions

class Blast(object):

  def store_blast(self, to, msg):
    timestamp = datetime.utcnow()
    to = [s.strip() for s in to.split(',')]
    new_blast = {
      'to': to,
      'msg': msg,
      'timestamp': str(timestamp),
    }
    curr_blasts = read(BLAST_FILE, [], True)
    curr_blasts.insert(0, new_blast)
    write(BLAST_FILE, curr_blasts, True)

  def xmpp_connect(self):
    # should not be here but oh well
    self.aliases = read(ALIAS_FILE, {}, True)
    self.blasts = read(BLAST_FILE, [], True)
    self.xmpp_config = read(XMPP_CONFIG_FILE, as_json=True)

    client = self.xmpp_config['client']
    server = self.xmpp_config['server']
    port = self.xmpp_config['port']
    username = self.xmpp_config['username']
    password = base64.b64decode(self.xmpp_config['password'])

    self.cnx = xmpp.Client(client)
    self.cnx.connect(server=(server, port))
    self.cnx.auth(username, password, 'botty')

  def _get_alias_type(self, alias):
    if alias in self.aliases['group']:
      return 'group'
    elif alias in self.aliases['user']:
      return 'user'
    return 'unknown_type'

  def _send_group_blast(self, room, blast):
    nickname = self.xmpp_config['nickname']
    self.cnx.send(xmpp.Presence(to="%s/%s" % (room, nickname)))
    msg = xmpp.protocol.Message(body=blast)
    msg.setTo(room)
    msg.setType('groupchat')
    self.cnx.send(msg)

  def _send_user_blast(self, to, content):
    print 'sending USER blast to'
    msg = xmpp.Message(to, content)
    self.cnx.send(msg)

  def store_no_op(self):
    """No-op prohibits blast from executing."""
    return
    curr_blasts = read(BLAST_FILE, [], True)
    curr_blasts.insert(0, {'no_op': 1})
    write(BLAST_FILE, curr_blasts, True)

  def get_git_commit_info(self):
    command = 'git log -n 1'
    subprocess.call(shlex.split(command), stdout=file(TMP_FILE, 'w'))
    data = open(TMP_FILE).read()
    return data

  def send_blast(self):
    xmpp_targets = {
      'group': [],
      'user': [],
      'unknown_type': [],
    }

    if self.blasts and 'no_op' not in self.blasts[0]:
      blast = self.blasts[0]
      for recipient in blast['to']:
        _type = self._get_alias_type(recipient)
        if _type in ['group', 'user']:
          full = self.aliases[_type][recipient]
          xmpp_targets[_type].append(full)
        else:
          xmpp_targets[_type].append(recipient)

      parts = [blast['msg'], '', self.get_git_commit_info()]
      msg = '\n'.join(parts)

      for r in xmpp_targets['group']:
        self._send_group_blast(r, msg)

      # users.append(current_user) ?
      # treat the unknowns as users
      for r in xmpp_targets['user'] + xmpp_targets['unknown_type']:
        self._send_user_blast(r, msg)

################################################################################
# Main function

def main(argv):
  optlist, args = getopt.getopt(argv[0:], 'p:', ['blast=', 'msg=', 'send-blast'])
  optlist = dict(optlist)
  if '--send-blast' in optlist:
    instance = Blast()
    instance.xmpp_connect()
    instance.send_blast()
    instance.store_no_op()
    return
  if '--blast' in optlist and '--msg' in optlist:
    recipients = optlist['--blast']
    msg = optlist['--msg']
    instance = Blast()
    instance.store_blast(recipients, msg)
  cl_ticket_ids = args
  history = read(RT_HISTORY_FILE, as_json=True)
  if '-p' in optlist:
    # Need 'map' because unicode breaks everything
    from_history = map(str, history[:int(optlist['-p'])])
  else:
    from_history = []
  ticket_ids =  cl_ticket_ids + from_history
  if ticket_ids:
    make_tmp_commit_file(ticket_ids)
    update_history_file(history, cl_ticket_ids)
    exec_git_commit()

if __name__ == '__main__':
  main(sys.argv[1:])
