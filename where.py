from __future__ import unicode_literals

from mcdreforged.api.decorator.new_thread import new_thread

from mcdreforged.command.builder.command_node import Literal, Text
from mcdreforged.command.builder.exception import RequirementNotMet
from mcdreforged.command.command_source import CommandSource
from mcdreforged.minecraft.rtext import RColor, RText, RTextList, RTextTranslation
from mcdreforged.plugin.server_interface import ServerInterface


PLUGIN_METADATA = {
    'id': 'where',
    'version': '1.0.0',
    'name': 'Where',
    'author': [
            'KSHSlime'
    ]
}

help_msg =\
    f'''
==========where v{PLUGIN_METADATA["version"]}==========
!!where        顯示資訊
!!where help   顯示幫助頁面

!!where <player>  顯示<player>的座標
'''
info_msg =\
    f'''
插件名稱: {PLUGIN_METADATA["name"]}
版本: {PLUGIN_METADATA["version"]}
作者: {PLUGIN_METADATA["author"]}

輸入!!where help 獲得此插件的用法
'''


def on_load(server: ServerInterface, old_module):

    process = Process(server)

    server.register_help_message('!!where', '查看其他玩家的坐标')
    server.register_command(
        # & !!where
        Literal("!!where").
        requires(lambda src: src.has_permission(3)).
        on_error(RequirementNotMet, lambda server: server.reply(RTextTranslation("commands.help.failed", color=RColor.red))).
        runs(lambda server: server.reply(info_msg)).
        # & !!where help
        then(
            Literal("help").runs(lambda server: server.reply(help_msg))
        ).
        # & !!where <player>
        then(

            Text("player").runs(lambda src, ctx: process.get_player(src, ctx))
        )
    )


class Process:
    def __init__(self, server):
        self.server = server

        self.OnlinePlayerAPI = server.get_plugin_instance("online_player_api")

    @new_thread("where.get_player")
    def get_player(self, src: CommandSource, ctx: dict):
        if not self.OnlinePlayerAPI.check_online(ctx["player"]):
            self.server.tell(src.player, RText("此玩家不存在或未上線",color=RColor.red))
            return

        x, y, z = self._process_coordinate(self.server.rcon_query(
            'data get entity {} Pos'.format(ctx["player"])))

        dimension = self._process_dimension(self.server.rcon_query(
            'data get entity {} Dimension'.format(ctx["player"])))

        dimension_convert = {
            "overworld": RTextTranslation("createWorld.customize.preset.overworld", color=RColor.dark_green),
            "the_nether": RTextTranslation("advancements.nether.root.title", color=RColor.dark_red),
            "the_end": RTextTranslation("advancements.end.root.title", color=RColor.dark_purple)
        }

        text_list = RTextList(RText(ctx["player"], color=RColor.yellow), RText(
            " "), RText("@"), RText(" "))
        text_list.append(dimension_convert[dimension])
        text_list.append(RText(" "))
        text_list.append(RText("[{}, {}, {}]".format(
            int(round(x)), int(round(y)), int(round(z))), color=RColor.aqua))

        self.server.tell(src.player, text_list)

    def _process_coordinate(self, text):
        data = list((text.split(":")[-1].replace("d", "")
                     ).replace("[", "").replace("]", "").split(","))
        for i in range(len(data)):
            data[i] = float(data[i])
        return tuple(data)

    def _process_dimension(self, text):
        data = text.split(":")[-1].replace("\"", "")
        return data
