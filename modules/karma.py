#!/usr/bin/env python
"""
karma.py - Phenny karma module
By Ori Rawlings
"""

from itertools import imap

points = {}

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
    if op == '++':
        if input.nick == user:
            phenny.say('Silly ' + input.nick + ", you can't award yourself karma...")
            return
        f = lambda x: x+1
    elif op == '--':
        if input.nick == user:
            phenny.say('Wow ' + input.nick + ", you must have really been bad to take karma from yourself...")
        f = lambda x: x-1
    else:
        f = lambda x: x
    try:
        points[user] = f(points[user])
    except KeyError:
        points[user] = f(0)
karma_point.rule = '^(\w+)(\+{2}|-{2})$'

def karma(phenny, input):
    """
    .karma - prints all stored karma scores for various nicks to the channel
    """
    for entry in points.items():
        phenny.say('\t'.join(imap(str,entry)))
karma.commands = ['karma']
karma.priority = 'medium'

if __name__ == '__main__': 
   print __doc__.strip()
