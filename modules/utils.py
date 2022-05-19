from Moduleloader import *
import Moduleloader
import Bot
import logging
from ts3.TS3Connection import TS3QueryException

__version__ = "0.4"
bot: Bot.Ts3Bot = None
logger = logging.getLogger("bot")


@Moduleloader.setup
def setup(ts3bot):
    global bot
    bot = ts3bot


@command('hello', )
@group('Kaiser', )
def hello(sender, msg):
    Bot.send_msg_to_client(bot.ts3conn, sender, "Hello your majesty!")


@command('hello', )
@group('Truchsess', )
def hello(sender, msg):
    Bot.send_msg_to_client(bot.ts3conn, sender, "Hello seneschal!")


@command('hello', )
@group('Bürger', )
def hello(sender, msg):
    Bot.send_msg_to_client(bot.ts3conn, sender, "Hello citizen!")


@command('kickme', 'fuckme')
@group('.*', )
def kickme(sender, msg):
    ts3conn = bot.ts3conn
    ts3conn.clientkick(sender, 5, "Whatever.")


@command('mtest', )
@group('Kaiser', )
def mtest(sender, msg):
    channels = split_command(msg)[1:]
    ts3conn = bot.ts3conn
    answer = [ts3conn.channelfind(channel) for channel in channels]

    Bot.send_msg_to_client(ts3conn, sender, str(answer))


@command('multimove', 'mm')
@group('Kaiser', 'Truchsess')
def multi_move(sender, msg):
    """
    Move all clients from one channel to another.
    :param sender: Client id of sender that sent the command.
    :param msg: Sent command.
    """
    channels = split_command(msg)[1:]
    source = None
    dest = None
    ts3conn = bot.ts3conn
    if len(channels) != 2:
        if sender != 0:
            Bot.send_msg_to_client(ts3conn, sender, "Usage: multimove <source> <destination>")
            return
    source_name = channels[0]
    dest_name = channels[1]
    try:
        channel_matches = ts3conn.channelfind(source_name)
        channel_candidates = [chan for chan in channel_matches if
                              chan.get("channel_name", '-1').startswith(source_name)]
        if len(channel_candidates) == 1:
            source = channel_candidates[0].get("cid", '-1')
        elif len(channel_candidates) == 0:
            Bot.send_msg_to_client(ts3conn, sender, "Source channel could not be found.")
        else:
            channels = [chan.get('channel_name') for chan in channel_candidates]
            Bot.send_msg_to_client(ts3conn, sender, "Multiple source channels found: " + ", ".join(channels))
    except TS3QueryException:
        Bot.send_msg_to_client(ts3conn, sender, "Source channel not found")
    try:
        channel_matches = ts3conn.channelfind(dest_name)
        channel_candidates = [chan for chan in channel_matches if chan.get("channel_name",
                                                                           '-1').startswith(dest_name)]
        if len(channel_candidates) == 1:
            dest = channel_candidates[0].get("cid", '-1')
        elif len(channel_candidates) == 0:
            Bot.send_msg_to_client(ts3conn, sender, "Destination channel could not be found.")
        else:
            channels = [chan.get('channel_name') for chan in channel_candidates]
            Bot.send_msg_to_client(ts3conn, sender, "Multiple destination channels found: " + ", ".join(channels))
    except TS3QueryException:
        Bot.send_msg_to_client(ts3conn, sender, "Destination channel not found")

    if source and dest:
        try:
            client_list = ts3conn.clientlist()
            client_list = [client for client in client_list if client.get("cid", '-1') == source]
            for client in client_list:
                clid = client.get("clid", '-1')
                logger.info("Found client in channel: " + client.get("client_nickname", "") + " id = " + clid)
                ts3conn.clientmove(int(dest), int(clid))
        except TS3QueryException as e:
            Bot.send_msg_to_client(ts3conn, sender, "Error moving clients: id = " +
                                   str(e.id) + e.message)


def send_message_to_everyone(conn, message):
    client_list = conn.clientlist()
    for client in client_list:
        Bot.send_msg_to_client(conn, client.get("clid", '-1'), message)


@command('messageeveryone', )
@group('Kaiser', 'Truchsess', )
def message_everyone(sender, msg):
    message = msg[msg.index(" ") + 1:]
    send_message_to_everyone(bot.ts3conn, message)
    Bot.send_msg_to_client(bot.ts3conn, sender, "Done")


@command('echo', )
@group('.*')
def send_version(sender, msg):
    messages = split_command(msg)[1:]
    for message in messages:
        Bot.send_msg_to_client(bot.ts3conn, sender, message)


@command('version', )
@group('.*')
def send_version(sender, msg):
    Bot.send_msg_to_client(bot.ts3conn, sender, __version__)


@command('whoami', )
@group('.*')
def whoami(sender, msg):
    Bot.send_msg_to_client(bot.ts3conn, sender, "None of your business!")


@command('stop', )
@group('Kaiser', )
def stop_bot(sender, msg):
    Moduleloader.exit_all()
    bot.ts3conn.quit()
    logger.warning("Bot was quit!")


@command('restart', )
@group('Kaiser', )
def restart_bot(sender, msg):
    Moduleloader.exit_all()
    bot.ts3conn.quit()
    logger.warning("Bot was quit!")
    import main
    main.restart_program()


@command('commandlist', 'commands')
@group('Kaiser', 'Truchsess', 'Bürger')
def get_command_list(sender, msg):
    Bot.send_msg_to_client(bot.ts3conn, sender, str(list(bot.command_handler.handlers.keys())))


@command('sethostmessage', 'hostmessage', )
@group('Kaiser', )
def set_hostmessage(sender, msg):
    message = msg[msg.index(" ") + 1:]
    bot.ts3conn.set_hostmessage(message)
    Bot.send_msg_to_client(bot.ts3conn, sender, "set hostmessage:" + message)


@command('resethostmessage', 'deletehostmessage', 'disablehostmessage', )
@group('Kaiser', )
def set_hostmessage(sender, msg):
    bot.ts3conn.disable_hostmessage()
    Bot.send_msg_to_client(bot.ts3conn, sender, "disable hostmessage")
