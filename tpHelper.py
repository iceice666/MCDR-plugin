from __future__ import unicode_literals

from mcdreforged.api.all import *
from time import sleep


PLUGIN_METADATA = {
    'id': 'tph',
    'version': '1.0.0',
    'name': 'tpHelper',
    'author': [
            'KSHSlime'
    ]
}

help_msg =\
    f'''
==========tp v{PLUGIN_METADATA["version"]}==========
!!tp        顯示資訊
!!tp help   顯示幫助頁面

!!tp player <player>  傳送到<player>
!!tp <x> <y> <z> <overworld |the_nether | the_end | all | custom>  傳送到<dimension>維度中的座標

'''
info_msg =\
    f'''
插件名稱: {PLUGIN_METADATA["name"]}
版本: {PLUGIN_METADATA["version"]}
作者: {PLUGIN_METADATA["author"]}

輸入!!tp help 獲得此插件的用法
'''


def on_load(server: ServerInterface, old_module):

    process = Process(server)

    server.register_help_message('!!tp', '查看其他玩家的坐标')
    server.register_command(
        # & !!tp
        Literal("!!tp").runs(lambda server: server.reply(info_msg)).
        # & !!tp help
        then(
            Literal("help").runs(lambda server: server.reply(help_msg))
        ).
        # & !!tp player <player>
        then(
            Literal("player").
            then(
                Text("player").runs(lambda src,
                                    ctx: process.tp_player(src.player, ctx["player"]))
            )
        ).
        # & !!tp <x> <y> <z> <dimension>
        then(Text("x").then(Text("y").then(Text("z").runs(lambda src, ctx: process.tp_pos(src.player, tuple([ctx["x"], ctx["y"], ctx["z"]]))).
        then(Text("dim").runs(lambda src, ctx: process.tp_pos(src.player, tuple([ctx["x"], ctx["y"], ctx["z"]]), ctx["dim"]))
        ))))
    )


class Process:
    def __init__(self, server):
        self.server = server
        self.OnlinePlayerAPI = server.get_plugin_instance("online_player_api")

    @ new_thread(PLUGIN_METADATA["name"])
    def tp_pos(self, player, pos: tuple, dim=None):
        if dim == None:
            cmd = f"/execute at {player} as {player} run tp {pos[0]} {pos[1]} {pos[2]}"
        else:
            cmd = f"/execute in {dim} as {player} run tp {pos[0]} {pos[1]} {pos[2]}"
        self.server.execute(cmd)

    @ new_thread(PLUGIN_METADATA["name"])
    def tp_player(self, from_player, to_player):
        if self.OnlinePlayerAPI.check_online(to_player):
            self.server.tell(from_player, f"將在5秒後傳送到{to_player}!")
            self.server.tell(to_player, f"{from_player}將在5秒後傳送到你身邊")
            for i in range(5):
                self.server.tell(from_player, f"倒數{5-i}秒")
                sleep(1)
                if i == 3:
                    self.server.execute(
                        f"effect give {from_player} minecraft:slowness 2 255")
            self.server.execute(f"/tp {from_player} {to_player}")
        else:

            self.server.tell(from_player, RText(
                f"請求的玩家 {to_player} 不存在或未上限", RColor.red))
