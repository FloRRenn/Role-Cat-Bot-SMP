"""
The MIT License (MIT)

Copyright (c) 2020-Current Skelmis

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from typing import Set, Dict, Any, Union

import attr


@attr.s(slots=True, eq=True, kw_only=True)
class Options:
    """Options for the AntiSpamHandler, see :py:class:`antispam.AntiSpamHandler` for usage.

    Parameters
    ----------
    warn_threshold : int
        Default: ``3``

        This is the amount of duplicates within ``message_interval`` that will result in a warning.
    kick_threshold : int
        Default: ``2``

        This is the amount of warns required before a kick is the next punishment.
        I.e. After 2 warns, you will get kicked.
    ban_threshold : int
        Default: ``2``

        This is the amount of kicks required before a ban is the next punishment.
        I.e. After 2 kicks, you will get banned.
    message_interval : int
        Default: ``30000ms (30 seconds)``

        Amount of time a message is kept before being discarded.
        Essentially the amount of time (In milliseconds) a message can count towards spam.
    message_duplicate_count : int
        Default: ``5``

        The amount of duplicate messages needed within message_interval to trigger a punishment.
        I.e. Once you've sent 5 'spam' messages you'll get punished.
    message_duplicate_accuracy : int
        Default: ``90``

        How ‘close’ messages need to be to be registered as duplicates (Out of 100)
        You can test this with the code:

        .. highlight:: python
        .. code-block:: python
            from fuzzywuzzy import fuzz
            fuzz.token_sort_ratio("message one", "message two")
    guild_log_warn_message : Union[str, dict]
        Default: ``$MEMBERNAME was warned for spamming/sending duplicate messages.``

        The message to be sent in the guild when someone is warned.
        Please see the note at the bottom.
    guild_log_kick_message : Union[str, dict]
        Default: ``$MEMBERNAME was kicked for spamming/sending duplicate messages.``

        The message to be sent in the guild when someone is kicked.
        Please see the note at the bottom.
    guild_log_ban_message : Union[str, dict]
        Default: ``$MEMBERNAME was banned for spamming/sending duplicate messages.``

        The message to be sent in the guild when someone is banned.
        Please see the note at the bottom.
    member_warn_message : Union[str, dict]
        Default: ``Hey $MENTIONMEMBER, please stop spamming/sending duplicate messages.``

        The message to be sent in the guild when a member is warned.
    member_kick_message : Union[str, dict]
        Default: ``Hey $MENTIONMEMBER, you are being kicked from $GUILDNAME for spamming/sending duplicate messages.``

        The message to be sent to the member who is being kicked.
    member_ban_message : Union[str, dict]
        Default: ``Hey $MENTIONMEMBER, you are being banned from $GUILDNAME for spamming/sending duplicate messages.``

        The message to be sent to the member who is being banned.
    guild_log_warn_message_delete_after : int
        Default: ``None``

        How many seconds after sending the guild warn message to delete it.
    guild_log_kick_message_delete_after : int
        Default: ``None``

        How many seconds after sending the guild kick message to delete it.
    guild_log_ban_message_delete_after : int
        Default: ``None``

        How many seconds after sending the guild ban message to delete it.
    member_warn_message_delete_after : int
        Default: ``None``

        How many seconds after sending the member warn message to delete it.
    member_kick_message_delete_after : int
        Default: ``None``

        How many seconds after sending the member kick message to delete it.
    member_ban_message_delete_after : int
        Default: ``None``

        How many seconds after sending the member ban message to delete it.
    ignored_members : Set[int]
        Default: ``Empty Set``

        A Set of members to ignore messages from.
        Set this with :py:meth:`antispam.AntiSpamHandler.add_ignored_item`
        Remove members with :py:meth:`antispam.AntiSpamHandler.remove_ignored_item`
    ignored_channels : Set[int]
        Default: ``Empty Set``

        A Set of channels to ignore messages in.
        Set this with :py:meth:`antispam.AntiSpamHandler.add_ignored_item`
        Remove channels with :py:meth:`antispam.AntiSpamHandler.remove_ignored_item`
    ignored_roles : Set[int]
        Default: ``Empty Set``

        A Set of roles to ignore messages from.
        Set this with :py:meth:`antispam.AntiSpamHandler.add_ignored_item`
        Remove roles with :py:meth:`antispam.AntiSpamHandler.remove_ignored_item`
    ignored_guilds : Set[int]
        Default: ``Empty Set``

        A Set of guilds to ignore messages in.
        Set this with :py:meth:`antispam.AntiSpamHandler.add_ignored_item`
        Remove guilds with :py:meth:`antispam.AntiSpamHandler.remove_ignored_item`
    delete_spam : bool
        Default: ``False``

        Whether or not to delete messages marked as spam

        Won’t delete messages if ``no_punish`` is ``True``

        Note, this method is expensive.
        It will delete all messages marked as spam, and this means an api call per message.
    ignore_bots : bool
        Default: ``True``

        Should bots bypass anti-spam?
    warn_only : bool
        Default: ``False``

        Whether or not to only warn users, this means it will not kick or ban them.
    no_punish : bool
        Default: ``False``

        Don’t punish anyone, simply return whether or not they should be punished within ``propagate``.
        This essentially lets the end user handle punishments themselves.

        To check if someone should be punished, use the returned value from the propagate method.
        If should_be_punished_this_message is True then this package believes they should be punished.
        Otherwise just ignore that message since it shouldn’t be punished.

        Use :py:class:`antispam.plugins.AntiSpamTracker` with this mode for best affect.
    mention_on_embed : bool
        Default: ``True``

        If the message your trying to send is an embed, also send some content to mention the person being punished.
    delete_zero_width_chars : bool
        Default: ``test``

        Should zero width characters be removed from messages. Useful as otherwise it helps
        people bypass antispam measures.
    per_channel_spam : bool
        Default: ``False``

        Track spam as per channel, rather then per guild.
        I.e. False implies spam is tracked as ``Per Member Per Guild``
        True implies ``Per Member Per Channel``
    addons : Dict
        Default: ``Empty Dict``

        Use-able storage for plugins to store Options

    Notes
    -----
    Guild log messages will **only** send if :py:attr:`antispam.dataclasses.guild.Guild.log_channel_id` is set.
    You can set it with :py:meth:`antispam.AntiSpamHandler.add_guild_log_channel`
    """

    # Ints
    warn_threshold: int = attr.ib(default=3, validator=attr.validators.instance_of(int))
    kick_threshold: int = attr.ib(default=2, validator=attr.validators.instance_of(int))
    ban_threshold: int = attr.ib(default=2, validator=attr.validators.instance_of(int))
    message_interval: int = attr.ib(
        default=30000, validator=attr.validators.instance_of(int)
    )
    message_duplicate_count: int = attr.ib(
        default=5, validator=attr.validators.instance_of(int)
    )
    message_duplicate_accuracy: int = attr.ib(
        default=90, validator=attr.validators.instance_of(int)
    )

    # Strings
    guild_log_warn_message: Union[str, dict] = attr.ib(
        default="$MEMBERNAME bị cảnh cáo bị spam quá nhiều",
        kw_only=True,
        validator=attr.validators.instance_of((str, dict)),
    )
    
    guild_log_kick_message: Union[str, dict] = attr.ib(
        default="$MEMBERNAME bị kick vì đã cảnh cáo spam nhiều lần.",
        kw_only=True,
        validator=attr.validators.instance_of((str, dict)),
    )
    guild_log_ban_message: Union[str, dict] = attr.ib(
        default="$MEMBERNAME bị cấm vì spam quá nhiều.",
        kw_only=True,
        validator=attr.validators.instance_of((str, dict)),
    )
    
    member_warn_message: Union[str, dict] = attr.ib(
        default="Spam hơi nhiều rồi đấy $MENTIONMEMBER",
        kw_only=True,
        validator=attr.validators.instance_of((str, dict)),
    )
    
    member_kick_message: Union[str, dict] = attr.ib(
        default="$MENTIONMEMBER, Bạn đã bị kick khỏi $GUILDNAME vì spam quá nhiều",
        kw_only=True,
        validator=attr.validators.instance_of((str, dict)),
    )
    
    member_ban_message: Union[str, dict] = attr.ib(
        default="$MENTIONMEMBER, Bạn bị ăn BAN từ $GUILDNAME vì spam quá nhiều",
        kw_only=True,
        validator=attr.validators.instance_of((str, dict)),
    )
    
    member_failed_kick_message: Union[str, dict] = attr.ib(
        default="Hên cho bạn là tui không có quyền ```KICK``` đối với bạn, nhưng hãy văn minh lên, đừng spam nữa :(",
        kw_only=True,
        validator=attr.validators.instance_of((str, dict)),
    )
    
    member_failed_ban_message: Union[str, dict] = attr.ib(
        default="Hên cho bạn là tui không có quyền ```BAN``` đối với bạn, nhưng hãy văn minh lên, đừng spam nữa :(",
        kw_only=True,
        validator=attr.validators.instance_of((str, dict)),
    )

    # delete_after
    guild_log_ban_message_delete_after: int = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(int)),
    )
    guild_log_kick_message_delete_after: int = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(int)),
    )
    member_ban_message_delete_after: int = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(int)),
    )
    guild_log_warn_message_delete_after: int = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(int)),
    )
    member_kick_message_delete_after: int = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(int)),
    )
    member_warn_message_delete_after: int = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(int)),
    )

    # Sets
    ignored_members: Set[int] = attr.ib(
        default=attr.Factory(set),
        validator=attr.validators.instance_of(set),
        converter=set,
    )
    ignored_channels: Set[int] = attr.ib(
        default=attr.Factory(set),
        validator=attr.validators.instance_of(set),
        converter=set,
    )
    ignored_roles: Set[int] = attr.ib(
        default=attr.Factory(set),
        validator=attr.validators.instance_of(set),
        converter=set,
    )
    ignored_guilds: Set[int] = attr.ib(
        default=attr.Factory(set),
        validator=attr.validators.instance_of(set),
        converter=set,
    )

    # Booleans
    delete_spam: bool = attr.ib(
        default=False, validator=attr.validators.instance_of(bool)
    )
    ignore_bots: bool = attr.ib(
        default=True, validator=attr.validators.instance_of(bool)
    )
    warn_only: bool = attr.ib(
        default=False, validator=attr.validators.instance_of(bool)
    )
    no_punish: bool = attr.ib(
        default=False, validator=attr.validators.instance_of(bool)
    )
    mention_on_embed: bool = attr.ib(
        default=True, validator=attr.validators.instance_of(bool)
    )
    delete_zero_width_chars: bool = attr.ib(
        default=True, validator=attr.validators.instance_of(bool)
    )

    # Core punishment settings
    per_channel_spam: bool = attr.ib(
        default=False, validator=attr.validators.instance_of(bool)
    )  # False implies per_user_per_guild

    # TODO Implement this
    # Catches 5 people saying the same thing
    is_per_channel_per_guild: bool = attr.ib(
        default=True, validator=attr.validators.instance_of(bool)
    )

    # Add on option storage for plugins
    addons: Dict[str, Any] = attr.ib(
        default=attr.Factory(dict), validator=attr.validators.instance_of(dict)
    )
