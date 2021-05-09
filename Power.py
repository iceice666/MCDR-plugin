
from mcdreforged.command.builder.exception import RequirementNotMet
from mcdreforged.minecraft.rtext import RColor, RText, RTextTranslation
from mcdreforged.plugin.server_interface import ServerInterface
from mcdreforged.command.builder.command_node import Literal, Number

from time import sleep
import threading

import lib.plugin_metadata as pm

# ~ plugin metadata config ~

# * Metadata
plugin_metadata = pm.metadata()
plugin_metadata.set_value("id", "power")
plugin_metadata.set_value("author", "KSHSlime")
plugin_metadata.set_value("version", "1.0.0")
plugin_metadata.set_value("name", "Power")
plugin_metadata.set_value("prefix", "power")
plugin_metadata.set_value(
    "description", "A MCDR plugin help you start/stop MCDR/Minecraft Server")


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
plugin_info_msg.add_msg("==================")
plugin_info_msg.add_msg("插件名稱: {}".format(plugin_metadata.get_value("name")))
plugin_info_msg.add_msg("版本: {}".format(plugin_metadata.get_value("version")))
plugin_info_msg.add_msg("作者: {}".format(plugin_metadata.get_value("author")))
plugin_info_msg.add_msg("敘述: {}".format(
    plugin_metadata.get_value("description")))
plugin_info_msg.add_msg("==================")

INFO_MSG = plugin_info_msg.get_value()
# ~ ======================== ~


def on_load(server: ServerInterface, old_module):

    process = Process(server)
    request = Request(server)

    # ^ Command System
    server.register_help_message(f'!!{plugin_metadata.get_value("prefix")}',
                                 {plugin_metadata.get_value("description")})
    server.register_command(
        # &
        Literal(f'!!{plugin_metadata.get_value("prefix")}').
        requires(lambda src: src.has_permission(3)).
        on_error(RequirementNotMet, lambda server: server.reply(RTextTranslation("commands.help.failed", color=RColor.red))).
        runs(lambda server: server.reply(INFO_MSG)).
        # & help
        then(Literal("help").runs(lambda server: server.reply(HELP_MSG))).

        # & shutdown
        # ~ Close MCDR and Minecraft Server
        then(Literal("shutdown").runs().
             then(Number("waiting").runs())).
        # & stop
        # ~ Close Minecraft Server
        then(Literal("stop").runs().
             then(Number("waiting").runs())).
        # & start
        # ~ Start Minecraft Server
        then(Literal("start").runs()).

        # & confirm
        then(Literal("confirm").runs()).
        # & cancel
        then(Literal("cancel").runs()).
        # & abort
        # ! Only server owner or request creator can abort it
        then(Literal("abort").
             requires(lambda src: (src.has_permission(4) | src.player == request.Request_info["posted_by"])).
             runs())
    )


# ^ Processing commands here

class Process:
    def __init__(self, server) -> None:
        self.server = server


class Request:
    Request_info = {"type": None, "posted_by": ""}



    def __init__(self, server):
        self.server = server
        self.server.execute("/bossbar add MCDR_Plugin.Power._counting")
        self.server.execute(
            "/bossbar set MCDR_Plugin.Power._counting color red")
        self.server.execute(
            "/bossbar set MCDR_Plugin.Power._counting visible true")
        self.server.execute(
            "/bossbar set MCDR_Plugin.Power._counting style progress")




    def create(self, src, ctx, _type):
        if self.Request_info["type"] != None:
            self.server.reply(RText("有已經一個請求了在執行了!!!", RColor=RColor.red))
            return

        self.Request_info["posted_by"] = src.player
        self.Request_info["type"] = _type.lower()
        if _type == "shutdown":
            CObj_STDN=_counting(self.server)
            CObj_STDN.start(("SHUTDOWN", self.server.stop_exit, ctx["waiting"],))
        elif _type == "stop":
            self._counting("STOP", self.server.stop, ctx["waiting"])
        else:
            self.Request_info = {"type": None, "posted_by": ""}
            return

        self.Request_info["posted_by"] = src.player~
        self.Request_info["type"] = _type.lower()
        if _type == "shutdown":
            self._counting()
        elif _type == "stop":
            self._stop(ctx["waiting"])
        else:
            self.Request_info = {"type": None, "posted_by": ""}
            return

    # TODO Counting Thread unfinished


class _counting(threading.Thread):
    def __init__(self, server):
        super().__init__()
        self.server = server

    def run(self, _type: str, _callback: callable, waiting: int = 10):
        self.server.execute(
            "/bossbar set MCDR_Plugin.Power._counting max {}".format(waiting))

        for i in range(waiting):
            if (waiting-i == 60 | waiting-i == 30 | waiting-i == 15 | waiting-i == 10):
                self.server.boardcast(
                    RText("Server will {} soon! {} secs remaining.".format(_type, waiting-i), RColor=RColor.red))
            elif waiting-i <= 10:
                self.join()
            elif waiting-i <= 5:
                self.server.boardcast(
                    RText("Countdown {} secs.".format(waiting-i), RColor=RColor.red))
            elif waiting-i <= 0:
                _callback()
                break
            self.server.execute(
                "/bossbar set MCDR_Plugin.Power._counting value {}".format(waiting-i))
            cd_rj = ["", {"text": _type, "underlined": True, "color": "red"}, " in ", {
                "text": waiting-i, "bold": True, "color": "gold"}, " secs"]
            self.server.execute(
                "/bossbar set MCDR_Plugin.Power._counting name {}".format(
                    str(cd_rj))
            )
            sleep(1)
