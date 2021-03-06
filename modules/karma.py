#!/usr/bin/env python
"""
karma.py - Phenny karma module
By Ori Rawlings
"""

import sqlite3
import os
from itertools import imap
from functools import partial
from operator import add


ops = { '++':partial(add, 1), '+1':partial(add, 1), '--':partial(add, -1), '-1':partial(add, -1) }

class KarmaDAO:
    def __init__(self, path):
        self.db_path = path

    def karmas(self, conn, limit=None):
        comm='select name,score from karma order by abs(score) desc '
        if limit and int(limit)>0:
            comm += 'limit %d'%int(limit)
        return conn.execute(comm)

    def update_karma(self, conn, user, f, default=0):
        user = str(user)
        score = conn.execute('select score from karma where name = ?', (user,)).fetchone()
        if score:
            score = f(score[0] or default)
            conn.execute('update karma set score=? where name=?', (score,user))
        else:
            score = f(default)
            conn.execute('insert into karma (name,score) values (?,?)', (user,score))
        conn.commit()

    def get_karma(self, conn, user):
        user=str(user)
        score = conn.execute('select score from karma where name = ?', (user,)).fetchone()
        score=(score and score[0]) or 0
        return score

def karma_point(phenny, input):
    """
    This rule will detect and apply karma operations.
    Usage: <nick>(++|--)
    Example:

    orirawlings++
    Increases nick, orirawlings, karma score by 1 point

    foobar--
    Decreases nick, foobar, karma score by 1 point
    """
    user = input.group(1)
    op = input.group(2)
    if input.nick == user:
        if '+' in op:
            phenny.reply("Silly, you can't award yourself karma...")
            return
        elif '-' in op:
            phenny.reply("Wow, you must have really been bad to take karma from yourself...")
    f = ops.get(op, lambda x: x)
    conn = sqlite3.connect(phenny.karma_dao.db_path)
    phenny.karma_dao.update_karma(conn, user, f, 0)
karma_point.rule = '^(\w+)(?::\s*)?(\+{2}|-{2})\s*$'

def karma(phenny, input):
    """
    .karma - prints all stored karma scores for various nicks to the channel
    """
    who=input.group(1)
    conn = sqlite3.connect(phenny.karma_dao.db_path)
    if not who or (who.isdigit() and int(who)>5):
        phenny.say("Sending you the list in private messages, "+input.nick)
        for entry in phenny.karma_dao.karmas(conn,who):
            # List of all is IMed to the questioner, so as not
            # to spam the channel.
            phenny.msg(input.nick,'\t'.join(imap(str,entry)))
    elif who.isdigit():
        for entry in phenny.karma_dao.karmas(conn,who):
            phenny.say("\t".join(imap(str,entry)))
    else:
        score = phenny.karma_dao.get_karma(conn, input.group(1))
        phenny.say("Karma for %s: %d"%(input.group(1), score))
    conn.close()

karma.rule = '^\.karma\s*(\w*)'
karma.priority = 'medium'

def path(self):
    return os.path.join(os.path.expanduser('~/.phenny'),'karma','karma.db')

def setup(phenny):
    phenny.karma_dao = KarmaDAO(path(phenny))

if __name__ == '__main__': 
   print __doc__.strip()
