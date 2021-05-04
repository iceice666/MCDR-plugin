
from mcdreforged.command.builder.exception import RequirementNotMet
from mcdreforged.minecraft.rtext import RColor, RText, RTextTranslation
from mcdreforged.plugin.server_interface import ServerInterface
from mcdreforged.command.builder.command_node import Literal, Number

from time import sleep

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
    def __init__(self) -> None:
        pass


class Request:
    Request_info = {"type": None, "posted_by": ""}

    def __init__(self, server):
        self.server = server

    def create(self, src, ctx, type):
        if self.Request_info["type"] != None:
            self.server.reply(RText("有已經一個請求了在執行了!!!", RColor=RColor.red))
            return

        self.Request_info["posted_by"] = src.player
        self.Request_info["type"] = type.lower()
        if type == "shutdown":
            self._shutdown(ctx["waiting"])
        elif type == "stop":
            self._stop(ctx["waiting"])
        else:
            self.Request_info = {"type": None, "posted_by": ""}
            return

    def _shutdown(self, waiting=10):
        for i in range(waiting):
            if waiting-i == 60:
                self.server.boardcast(
                    RText("Server will shutdown soon! {} secs remaining.".format(waiting-i), RColor=RColor.red))
            elif waiting-i == 30:
                self.server.boardcast(
                    RText("Server will shutdown soon! {} secs remaining.".format(waiting-i), RColor=RColor.red))
            elif waiting-i == 15:
                self.server.boardcast(
                    RText("Server will shutdown soon! {} secs remaining.".format(waiting-i), RColor=RColor.red))
            elif waiting-i == 10:
                self.server.boardcast(
                    RText("Server will shutdown soon! {} secs remaining.".format(waiting-i), RColor=RColor.red))
            elif waiting-i <= 10:
                self.server.boardcast(
                    RText("Countdown {} secs.".format(waiting-i), RColor=RColor.red))
            elif waiting-i<= 0:
                self.server.stop_exit()
            sleep(1)

    def _stop(self, waiting=10):
        for i in range(waiting):
            if waiting-i == 60:
                self.server.boardcast(
                    RText("Server will stop soon! {} secs remaining.".format(waiting-i), RColor=RColor.red))
            elif waiting-i == 30:
                self.server.boardcast(
                    RText("Server will stop soon! {} secs remaining.".format(waiting-i), RColor=RColor.red))
            elif waiting-i == 15:
                self.server.boardcast(
                    RText("Server will stop soon! {} secs remaining.".format(waiting-i), RColor=RColor.red))
            elif waiting-i == 10:
                self.server.boardcast(
                    RText("Server will stop soon! {} secs remaining.".format(waiting-i), RColor=RColor.red))
            elif waiting-i <= 10:
                self.server.boardcast(
                    RText("Countdown {} secs.".format(waiting-i), RColor=RColor.red))
            elif waiting-i <= 0:
                self.server.stop()
            sleep(1)
