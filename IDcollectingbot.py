from telethon import TelegramClient, sync, events
from telethon.utils import get_display_name
from telethon.tl.functions.channels import GetAdminLogRequest
from telethon.tl.types import ChannelAdminLogEventsFilter
from time import sleep


import logging
import asyncio
import re

#Log
logging.basicConfig(filename='log.log', level=logging.ERROR, format="%(asctime)s:%(levelname)s:%(message)s")

#Insert your own values
api_id = 123456
api_hash = 'ranDOmNUmbers678789AndLettersKOWDKOWD'

client = TelegramClient('ACOOLNAME', api_id, api_hash).start()

#This part just waits for a new message
async def await_event(client, event, pre):
    message = asyncio.Future()

    @client.on(event)
    async def handler(ev):
        if isinstance(ev, events.CallbackQuery.Event):
            await ev.answer()
            message.set_result(ev)
        else:
            message.set_result(ev.message)
    await pre
    message = await message
    client.remove_event_handler(handler)
    return message

#You can change parameters here. In this setup, it listens to messages of you, and only starts when you type /Spamids, case insensitive
@client.on(events.NewMessage(outgoing=True, pattern="(?i)/SpamIDs"))
async def handler(event):
    #the two lists we are going to need
    namelist = []
    idlist = []
    #this will help us to know how many IDs we should put out in the end, end helps to show you numbers. So you don't have to count
    x = 0
    # param: (join, leave, invite, ban, unban, kick, unkick, promote, demote, info, settings, pinned, edit, delete)
    filterr = ChannelAdminLogEventsFilter(True, False, False, False, False, False, False, False, False, False, False,
                                          False, False, False)
    message = event.respond("Ok. Let's get started. For which group do you want the IDs? Send as @username")
    #this sends the message above and waits till you answer it. As stated, use the @username of the channel. The joinlink would probably work as well. Or the chat_id. the library deals with it, not my code.
    groupname = await await_event(client, events.NewMessage(outgoing=True), message)
    message = event.respond("Great. How many names do you want to see?")
    #sends and waits. Only state numbers, since its not going to be used by idiots, I'm fine with not checking stuff
    number = await await_event(client, events.NewMessage(outgoing=True), message)
    #this one only gets the join messages of the group and how many you like
    result = await client(GetAdminLogRequest(
        groupname.raw_text, q='', min_id=0, max_id=0, limit=int(number.raw_text), events_filter=filterr))
    #users are a subcategory, so we access it like this. Get_display_name is great to just get the name, we put x in front so we don't have to count.
    for _user in result.users:
        x += 1
        namelist.append('{} {}'.format(x, get_display_name(_user)))
    #now we put it in a handy list with paragraphs
    listes = "\n".join(namelist)
    #and give it out
    await event.respond('{}'.format(listes))
    #no sleeping needed, but I felt like it
    sleep(2)
    message = event.respond("Cool. Now tell me, from where should I start to list the IDs?")
    starting = await await_event(client, events.NewMessage(outgoing=True), message)
    message = event.respond("Wuhu. Last step: How many IDs should I show you?")
    ending = await await_event(client, events.NewMessage(outgoing=True), message)
    #this one needed a bit playing with the input above. It again gets all the join actions, the limit is enough when we both put it together. Math, yay
    result = await client(GetAdminLogRequest(
        groupname.raw_text, q='', min_id=0, max_id=0, limit=int(starting.raw_text) + int(ending.raw_text),
        events_filter=filterr))
    #reseting x is important, we used it before, so there we go
    x = 0
    #python is pretty awesome with and and or. Because everything else would be too complicated, I just start when x is the first number and then go along. Again, math.
    for _user in result.users:
        x += 1
        if x == int(starting.raw_text) or x > int(starting.raw_text) and  x < int(starting.raw_text)+ int(ending.raw_text):
            idlist.append('{}'.format(_user.id))
    ids = "\n".join(idlist)
    #thanks to the library, this will be formated at a copyable list.
    await event.respond('```{}```'.format(ids))

client.run_until_disconnected()
