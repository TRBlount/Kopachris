#!/usr/bin/env python
# coding: utf8
from gluon import *
import bot_utils
import urllib2
from datetime import datetime

## Description stored in db.bot_modules
description = "Mailboxes for IRC networks"

## Prefix stored in db.bot_modules
## Each module should have its own prefix for bot_vars entries
prefix = "mail_"

## Event type handled by this module
event_type = "PRIVMSG"

_cmd = ["!mail"]

## Additional global vars


def init(db):
    pass


def remove(db):
    pass


def run(bot, event, db):
    mod_name = __name__.rsplit('.', 1)[1]
    this_mod = db(db.bot_modules.name == mod_name).select()
    prefix = this_mod.first().vars_pre
    m_items = prefix + "items"
    bot_nick = bot.nickname
    
    if m_items not in db:
        # define the table
        m_items = db.define_table(m_items,
                                  Field('m_time', 'datetime'),
                                  Field('m_from'),
                                  Field('m_to'),
                                  Field('m_msg'),
                                  Field('m_del', default='F'),
                                  Field('m_del_time', 'datetime')
                                  )
    else:
        m_items = db[m_items]

    all_unread = db(m_items.m_del == 'F').select()
    unread_users = [r.m_to.lower() for r in all_unread]

    if event.source.lower() in unread_users:
        # deliver mail
        old_target = event.target
        event.target = bot_nick
        these_unread = [r for r in all_unread if r.m_to.lower() == event.source.lower()]
        bot.bot_reply(event, "You have {} unread messages.".format(len(these_unread)))
        for m in these_unread:
            bot.bot_reply(event, "From {} at {}: {}".format(m.m_from, m.m_time, m.m_msg), reply=False)
            m.update_record(m_del_time=datetime.now(), m_del='T')
        event.target = old_target
        db.commit()

    msg = event.message.lower().split()
    if msg[0] == '!mail' and len(msg) > 2:
        # save mail
        msg_raw = event.message.split()
        m_from = event.source
        m_to = msg_raw[1]
        m_msg = ' '.join(msg_raw[2:])
        now = datetime.now()
        if m_to == bot_nick:
            bot.bot_reply(event, "I'm not going to read this mail because I'm a brainless bot you twit.")
            return
        m_items.insert(m_time=now,
                       m_from=m_from,
                       m_to=m_to,
                       m_msg=m_msg,
                       m_del_time=now
                       )
        re_msg = "Message for {} saved at {}".format(m_to, now.strftime('%c'))
        bot.bot_reply(event, re_msg)
    
    # if msg[0] == '!mail' and len(msg) == 1:
    #     if event.source.lower() in unread_users:
    #         event.target = bot_nick
    #         #these_unread = db(m_items.m_del == 'F' and m_items.m_to == event.source.lower()).select()
    #         these_unread = [r for r in all_unread if r.m_to.lower() == event.source.lower()]
    #         bot.bot_reply(event, "You have {} unread messages.".format(len(these_unread)))
    #         for m in these_unread:
    #             bot.bot_reply(event, "From {} at {}: {}".format(m.m_from, m.m_time, m.m_msg), reply=False)
    #             m.update_record(m_del_time=datetime.now(), m_del='T')
    #     else:
    #         bot.bot_reply(event, "You have no unread messages.")
    
    # if msg[0] != '!mail' and event.source in unread_users:
    #     event.target = bot_nick
    #     #these_unread = db(m_items.m_del == 'F' and m_items.m_to == event.source).select()
    #     these_unread = [r for r in all_unread if r.m_to.lower() == event.source.lower()]
    #     bot.bot_reply(event, "You have {} unread messages.".format(len(these_unread)))
    #     for m in these_unread:
    #         bot.bot_reply(event, "From {} at {}: {}".format(m.m_from, m.m_time, m.m_msg), reply=False)
    #         m.update_record(m_del_time=datetime.now(), m_del='T')
