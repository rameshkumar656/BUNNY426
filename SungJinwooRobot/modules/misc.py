import re
from contextlib import suppress
from datetime import datetime

import wikipedia

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.exceptions import (
    BadRequest,
    MessageNotModified,
    MessageToDeleteNotFound,
)

from SungJinwooRobot.decorator import register

from .utils.disable import disableable_dec
from .utils.httpx import http
from .utils.language import get_strings_dec
from .utils.message import get_args_str
from .utils.notes import get_parsed_note_list, send_note, t_unparse_note_item
from .utils.user_details import is_user_admin



from SungJinwooRobot.modules.helper_funcs.chat_status import user_admin
from SungJinwooRobot.modules.disable import DisableAbleCommandHandler
from SungJinwooRobot import dispatcher

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ParseMode, Update
from telegram.ext.dispatcher import run_async
from telegram.ext import CallbackContext, Filters, CommandHandler

MARKDOWN_HELP = f"""
Markdown is a very powerful formatting tool supported by telegram. {dispatcher.bot.first_name} has some enhancements, to make sure that \
saved messages are correctly parsed, and to allow you to create buttons.

• <code>_italic_</code>: wrapping text with '_' will produce italic text
• <code>*bold*</code>: wrapping text with '*' will produce bold text
• <code>`code`</code>: wrapping text with '`' will produce monospaced text, also known as 'code'
• <code>[sometext](someURL)</code>: this will create a link - the message will just show <code>sometext</code>, \
and tapping on it will open the page at <code>someURL</code>.
<b>Example:</b><code>[test](example.com)</code>

• <code>[buttontext](buttonurl:someURL)</code>: this is a special enhancement to allow users to have telegram \
buttons in their markdown. <code>buttontext</code> will be what is displayed on the button, and <code>someurl</code> \
will be the url which is opened.
<b>Example:</b> <code>[This is a button](buttonurl:example.com)</code>

If you want multiple buttons on the same line, use :same, as such:
<code>[one](buttonurl://example.com)
[two](buttonurl://google.com:same)</code>
This will create two buttons on a single line, instead of one button per line.

Keep in mind that your message <b>MUST</b> contain some text other than just a button!
"""


@register(cmds="buttonshelp", no_args=True, only_pm=True)
async def buttons_help(message):
    await message.reply(
        """
<b>Buttons:</b>
Here you will know how to setup buttons in your note, welcome note, etc...

There are different types of buttons!

<i>Due to current Implementation adding invalid button syntax to your note will raise error! This will be fixed in next major version.</i>

<b>Did you know?</b>
You could save buttons in same row using this syntax
<code>[Button](btn{mode}:{args if any}:same)</code>
(adding <code>:same</code> like that does the job.)

<b>Button Note:</b>
<i>Don't confuse this title with notes with buttons</i> 😜

This types of button will allow you to show specific notes to users when they click on buttons!

You can save note with button note without any hassle by adding below line to your note ( Don't forget to replace <code>notename</code> according to you 😀)

<code>[Button Name](btnnote:notename)</code>

<b>URL Button:</b>
Ah as you guessed! This method is used to add URL button to your note. With this you can redirect users to your website or even redirecting them to any channel, chat or messages!

You can add URL button by adding following syntax to your note

<code>[Button Name](btnurl:https://your.link.here)</code>

<b>Button rules:</b>
Well in v2 we introduced some changes, rules are now saved seperately unlike saved as note before v2 so it require seperate button method!

You can use this button method for including Rules button in your welcome messages, filters etc.. literally anywhere*

You use this button with adding following syntax to your message which support formatting!
<code>[Button Name](btnrules)</code>
    """
    )


@register(cmds="variableshelp", no_args=True, only_pm=True)
async def buttons_help(message):
    await message.reply(
        """
<b>Variables:</b>
Variables are special words which will be replaced by actual info

<b>Avaible variables:</b>
<code>{first}</code>: User's first name
<code>{last}</code>: User's last name
<code>{fullname}</code>: User's full name
<code>{id}</code>: User's ID
<code>{mention}</code>: Mention the user using first name
<code>{username}</code>: Get the username, if user don't have username will be returned mention
<code>{chatid}</code>: Chat's ID
<code>{chatname}</code>: Chat name
<code>{chatnick}</code>: Chat username
    """
    )


@register(cmds="wiki")
@disableable_dec("wiki")
async def wiki(message):
    args = get_args_str(message)
    wikipedia.set_lang("en")
    try:
        pagewiki = wikipedia.page(args)
    except wikipedia.exceptions.PageError as e:
        await message.reply(f"No results found!\nError: <code>{e}</code>")
        return
    except wikipedia.exceptions.DisambiguationError as refer:
        refer = str(refer).split("\n")
        if len(refer) >= 6:
            batas = 6
        else:
            batas = len(refer)
        text = ""
        for x in range(batas):
            if x == 0:
                text += refer[x] + "\n"
            else:
                text += "- `" + refer[x] + "`\n"
        await message.reply(text)
        return
    except IndexError:
        msg.reply_text("Write a message to search from wikipedia sources.")
        return
    title = pagewiki.title
    summary = pagewiki.summary
    button = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔧 More Info...", url=wikipedia.page(args).url)
    )
    await message.reply(
        ("The result of {} is:\n\n<b>{}</b>\n{}").format(args, title, summary),
        reply_markup=button,
    )


@register(cmds="github")
@disableable_dec("github")
async def github(message):
    text = message.text[len("/github ") :]
    response = await http.get(f"https://api.github.com/users/{text}")
    usr = response.json()

    if usr.get("login"):
        text = f"<b>Username:</b> <a href='https://github.com/{usr['login']}'>{usr['login']}</a>"

        whitelist = [
            "name",
            "id",
            "type",
            "location",
            "blog",
            "bio",
            "followers",
            "following",
            "hireable",
            "public_gists",
            "public_repos",
            "email",
            "company",
            "updated_at",
            "created_at",
        ]

        difnames = {
            "id": "Account ID",
            "type": "Account type",
            "created_at": "Account created at",
            "updated_at": "Last updated",
            "public_repos": "Public Repos",
            "public_gists": "Public Gists",
        }

        goaway = [None, 0, "null", ""]

        for x, y in usr.items():
            if x in whitelist:
                x = difnames.get(x, x.title())

                if x in ("Account created at", "Last updated"):
                    y = datetime.strptime(y, "%Y-%m-%dT%H:%M:%SZ")

                if y not in goaway:
                    if x == "Blog":
                        x = "Website"
                        y = f"<a href='{y}'>Here!</a>"
                        text += "\n<b>{}:</b> {}".format(x, y)
                    else:
                        text += "\n<b>{}:</b> <code>{}</code>".format(x, y)
        reply_text = text
    else:
        reply_text = "User not found. Make sure you entered valid username!"
    await message.reply(reply_text, disable_web_page_preview=True)


@register(cmds="ip")
@disableable_dec("ip")
async def ip(message):
    try:
        ip = message.text.split(maxsplit=1)[1]
    except IndexError:
        await message.reply(f"Apparently you forgot something!")
        return

    response = await http.get(f"http://ip-api.com/json/{ip}")
    if response.status_code == 200:
        lookup_json = response.json()
    else:
        await message.reply(
            f"An error occurred when looking for <b>{ip}</b>: <b>{response.status_code}</b>"
        )
        return

    fixed_lookup = {}

    for key, value in lookup_json.items():
        special = {
            "lat": "Latitude",
            "lon": "Longitude",
            "isp": "ISP",
            "as": "AS",
            "asname": "AS name",
        }
        if key in special:
            fixed_lookup[special[key]] = str(value)
            continue

        key = re.sub(r"([a-z])([A-Z])", r"\g<1> \g<2>", key)
        key = key.capitalize()

        if not value:
            value = "None"

        fixed_lookup[key] = str(value)

    text = ""

    for key, value in fixed_lookup.items():
        text = text + f"<b>{key}:</b> <code>{value}</code>\n"

    await message.reply(text)


@register(cmds="cancel", state="*", allow_kwargs=True)
async def cancel_handle(message, state, **kwargs):
    await state.finish()
    await message.reply("Cancelled.")


async def delmsg_filter_handle(message, chat, data):
    if await is_user_admin(data["chat_id"], message.from_user.id):
        return
    with suppress(MessageToDeleteNotFound):
        await message.delete()


async def replymsg_filter_handler(message, chat, data):
    text, kwargs = await t_unparse_note_item(
        message, data["reply_text"], chat["chat_id"]
    )
    kwargs["reply_to"] = message.message_id
    with suppress(BadRequest):
        await send_note(chat["chat_id"], text, **kwargs)


@get_strings_dec("misc")
async def replymsg_setup_start(message, strings):
    with suppress(MessageNotModified):
        await message.edit_text(strings["send_text"])


async def replymsg_setup_finish(message, data):
    reply_text = await get_parsed_note_list(
        message, allow_reply_message=False, split_args=-1
    )
    return {"reply_text": reply_text}


@get_strings_dec("misc")
async def customise_reason_start(message: Message, strings: dict):
    await message.reply(strings["send_customised_reason"])


@get_strings_dec("misc")
async def customise_reason_finish(message: Message, _: dict, strings: dict):
    if message.text is None:
        await message.reply(strings["expected_text"])
        return False
    elif message.text in {"None"}:
        return {"reason": None}
    return {"reason": message.text}


__filters__ = {
    "delete_message": {
        "title": {"module": "misc", "string": "delmsg_filter_title"},
        "handle": delmsg_filter_handle,
        "del_btn_name": lambda msg, data: f"Del message: {data['handler']}",
    },
    "reply_message": {
        "title": {"module": "misc", "string": "replymsg_filter_title"},
        "handle": replymsg_filter_handler,
        "setup": {"start": replymsg_setup_start, "finish": replymsg_setup_finish},
        "del_btn_name": lambda msg, data: f"Reply to {data['handler']}: \"{data['reply_text'].get('text', 'None')}\" ",
    },
}



@run_async
@user_admin
def echo(update: Update, context: CallbackContext):
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message

    if message.reply_to_message:
        message.reply_to_message.reply_text(
            args[1], parse_mode="MARKDOWN", disable_web_page_preview=True)
    else:
        message.reply_text(
            args[1],
            quote=False,
            parse_mode="MARKDOWN",
            disable_web_page_preview=True)
    message.delete()


def markdown_help_sender(update: Update):
    update.effective_message.reply_text(
        MARKDOWN_HELP, parse_mode=ParseMode.HTML)
    update.effective_message.reply_text(
        "Try forwarding the following message to me, and you'll see, and Use #test!"
    )
    update.effective_message.reply_text(
        "/save test This is a markdown test. _italics_, *bold*, code, "
        "[URL](example.com) [button](buttonurl:github.com) "
        "[button2](buttonurl://google.com:same)")


@run_async
def markdown_help(update: Update, context: CallbackContext):
    if update.effective_chat.type != "private":
        update.effective_message.reply_text(
            'Contact me in pm',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "Markdown help",
                    url=f"t.me/{context.bot.username}?start=markdownhelp")
            ]]))
        return
    markdown_help_sender(update)


__mod_name__ = "Misc"

__help__ = """
An "odds and ends" module for small, simple commands which don't really fit anywhere.

<b>Available commands:</b>

<b> Basics</b>
- /direct (url): Generates direct links from the sourceforge.net
- /github (username): Returns info about a GitHub user or organization.
- /ip (url): Displays information about an IP / domain.
- /wiki (keywords): Get wikipedia articles just using this bot.
- /imdb: Search for a movie
- /cancel: Disables current state. Can help in cases if DaisyXBot not responing on your message.
- /id: get the current group id. If used by replying to a message, gets that user's id.
- /info: get information about a user.
- /paste: Pase the text/file in nekobin
- /gps: Find a location
- /fbdl: Download fb video (SD quality only)

<b> Book Download </b>
- /book <i>book name</i> : Usage :Gets Instant Download Link Of Given Book.

<b>Fake Information Generator</b>
- /fakegen : Generates Fake Information
- /picgen : generate a fake pic

<b> Zipper </b>
- /zip: reply to a telegram file to compress it in .zip format
- /unzip: reply to a telegram file to decompress it from the .zip format

<b> Weather </b>
- /weather: Gives weather forcast
- /wheatherimg: Gives weather image

<b> Phone info </b>
- /phone [phone no]: Gathers no info
"""


__help__ = """
*Available commands:*
*Markdown:*
 • `/markdownhelp`*:* quick summary of how markdown works in telegram - can only be called in private chats
*Paste:*
 • `/paste`*:* Saves replied content to `nekobin.com` and replies with a url
*React:*
 • `/react`*:* Reacts with a random reaction 
*Urban Dictonary:*
 • `/ud <word>`*:* Type the word or expression you want to search use
*Wikipedia:*
 • `/wiki <query>`*:* wikipedia your query
*Wallpapers:*
 • `/wall <query>`*:* get a wallpaper from wall.alphacoders.com
*Currency converter:* 
 • `/cash`*:* currency converter
Example:
 `/cash 1 USD INR`  
      _OR_
 `/cash 1 usd inr`
Output: `1.0 USD = 75.505 INR`
"""

ECHO_HANDLER = DisableAbleCommandHandler("echo", echo, filters=Filters.group)
MD_HELP_HANDLER = CommandHandler("markdownhelp", markdown_help)

dispatcher.add_handler(ECHO_HANDLER)
dispatcher.add_handler(MD_HELP_HANDLER)

__mod_name__ = "Extras"
__command_list__ = ["id", "echo"]
__handlers__ = [
    ECHO_HANDLER,
    MD_HELP_HANDLER,
]
