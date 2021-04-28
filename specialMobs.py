
# TODO not release!!!


from mcdreforged.command.builder import command_builder_util as utils
from mcdreforged.command.builder.command_node import ArgumentNode, Literal, ParseResult
from mcdreforged.command.builder.exception import RequirementNotMet

from mcdreforged.minecraft.rtext import RColor, RStyle, RText, RTextList, RTextTranslation
from mcdreforged.plugin.server_interface import ServerInterface


import os
import yaml
from threading import Thread
from time import sleep
import json

import lib.plugin_metadata as pm

# ~ plugin metadata config ~

# * Metadata
plugin_metadata = pm.metadata()
plugin_metadata.set_value("id", "special_mobs")
plugin_metadata.set_value("author", "KSHSlime")
plugin_metadata.set_value("version", "1.0.0")
plugin_metadata.set_value("name", "Special Mobs")
plugin_metadata.set_value("prefix", "smobs")
plugin_metadata.set_value("description", "Let mobs more special")
plugin_metadata.set_value("dependencies", {})
plugin_metadata.set_value("link", None)


PLUGIN_METADATA = plugin_metadata.get_settings()

# * help msg
plugin_help_msg = pm.help_msg()
plugin_help_msg.add_msg("=========={} v{}==========".format(
    plugin_metadata.get_value("prefix"),
    plugin_metadata.get_value("version"))
)

plugin_help_msg.add_msg("!!{}        顯示資訊".format(
    plugin_metadata.get_value("prefix")))
plugin_help_msg.add_msg("!!{} help   顯示幫助頁面".format(
    plugin_metadata.get_value("prefix")))

HELP_MSG = plugin_help_msg.get_value()

# * info msg
plugin_info_msg = pm.info_msg()
plugin_info_msg.add_msg(
    "=====================================================")
plugin_info_msg.add_msg("插件名稱: {}".format(plugin_metadata.get_value("name")))
plugin_info_msg.add_msg("版本: {}".format(plugin_metadata.get_value("version")))
plugin_info_msg.add_msg("作者: {}".format(plugin_metadata.get_value("author")))
plugin_info_msg.add_msg("敘述: {}".format(
    plugin_metadata.get_value("description")))
plugin_info_msg.add_msg(
    "=====================================================")

INFO_MSG = plugin_info_msg.get_value()
# ~ ======================== ~

# ^ MCDR event ^


def on_load(server: ServerInterface, old_module):

    global process
    process = Process(server)

    server.register_help_message(f'!!{plugin_metadata.get_value("prefix")}',
                                 {plugin_metadata.get_value("description")})
    server.register_command(
        # & .
        Literal(f'!!{plugin_metadata.get_value("prefix")}').
        requires(lambda src: src.has_permission(4)).
        on_error(RequirementNotMet, lambda server: server.reply(RTextTranslation("commands.help.failed", color=RColor.red))).
        runs(lambda server: server.reply(INFO_MSG)).
        # & help
        then(Literal("help").runs(lambda server: server.reply(HELP_MSG))).
        # & list
        then(Literal("list").runs(lambda src: process.get_list(src))).
        # & enable
        then(Literal("enable").runs(lambda: process.enable())).
        # & enable [list]
        then(List("opts").runs(lambda _, ctx: process.enable(ctx["opts"]))).
        # & disable
        then(Literal("disable").runs(lambda: process.disable()).
        # & disable [list]
        then(List("opts").runs(lambda _, ctx: process.disable(ctx["opts"]))))
    )


def on_unload(server: ServerInterface):
    pass

# ^ Process ^


class Process:
    spawningThread_list = []

    def __init__(self, server):
        self.server = server
        self.st = spawningManager(self.server, Yaml("specialMobs"))

    def get_list(self, src):
        self.st.get_info(src)

    def enable(self, options: list = None):
        self.st.enable(options)

    def disable(self, options: list = None):
        self.st.disable(options)

# ^ Spawning Thread ^

# TODO 執行緒控制


class spawningManager():

    # "<Func name>":
    #   Mobs:
    #       NBT: "<NBT data: str or dict>"
    #       chance: <chance%: int>
    #       loop: <sec: int> Trying spawn a mobs per <loop>
    #       entity: <entity id: str> target entity
    #   description: "<description: str>"
    #   is_activated: <is_activated: bool>

    def __init__(self, server, SETTINGS):
        self.server = server
        self.SETTINGS = SETTINGS
        self.spawningThread_list = []

    def enable(self, options: list = None):
        if options is None:
            for i in self.SETTINGS:
                i["is_activated"] = True
        else:
            for j in options:
                self.SETTINGS[j]["is+activated"] = True

    def disable(self, options: list = None):
        if options is None:
            for i in self.SETTINGS:
                i["is_activated"] = False
        else:
            for j in options:
                self.SETTINGS[j]["is+activated"] = False

    def get_info(self, src):
        self.SETTINGS.save()

        for i in self.SETTINGS:
            text_list = RTextList(RText("狀態："))
            if i["is_activated"] is True:
                text_list.append(
                    RText("啟用中", color=RColor.green, styles=RStyle.bold))
            else:
                text_list.append(
                    RText("禁用中", color=RColor.red, styles=RStyle.bold))

            self.server.tell(src.player, RText(
                i, color=RColor.yellow, styles=[RStyle.bold, RStyle.underlined]))
            self.server.tell(src.player, RText("敘述： " +
                                               self.SETTINGS[i]["description"], color=RColor.white))
            self.server.tell(src.player, RText(
                "週期:{}sec 嘗試生成一次  機率:{}%".format(self.SETTINGS[i]["Mobs"]["loop"], self.SETTINGS[i]["Mobs"]["chance"])))
            self.server.tell(text_list)
            self.server.tell(src.player, "")

    def save(self):
        self.SETTINGS.save()


# & custom


class List(ArgumentNode):
    '''
    List (yep just a list)
    '''

    def __init__(self, name, count=None):
        super().__init__(name)
        self.count = count

    def parse(self, text) -> ParseResult:
        arg = []
        if self.count is None:
            while True:
                arg.append(utils.get_element(text))
        else:
            for i in range(self.count):
                arg.append(utils.get_element(text))
        return ParseResult(arg, len(arg))


class Yaml(dict):
    """
    A inheritance class of dict, use save() to save data into file.
    """

    def __init__(self, plugin_name: str, file_name: str = None):
        # Dir
        self.dir = os.path.join('config', plugin_name)
        if not os.path.isdir(self.dir):
            os.mkdir(self.dir)
        # Path
        file_name = plugin_name if file_name is None else file_name
        self.path = os.path.join(self.dir, f'{file_name}.yaml')
        # Data
        if os.path.isfile(self.path):
            with open(self.path, encoding='utf-8') as f:
                super().__init__(yaml.load(f))
        else:
            super().__init__()
            self.save()

    def save(self):
        """Save data"""
        with open(self.path, 'w', encoding='utf-8') as f:
            yaml.dump(self.copy(), f, indent=4)
