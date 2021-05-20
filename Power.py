
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
        then(Literal("shutdown").runs(lambda src: request.create(src, 30, "shutdown")).
             then(Number("waiting").runs(lambda src, ctx: request.create(src, ctx, "shutdown")))).
        # & stop
        # ~ Close Minecraft Server
        then(Literal("stop").runs(lambda src: request.create(src, 30, "stop")).
             then(Number("waiting").runs(lambda src, ctx: request.create(src, ctx, "stop")))).
        # & start
        # ~ Start Minecraft Server
        then(Literal("start").runs(lambda src: request.create(src, 0, "start"))).
        # & restart
        # ~ Restart Minecraft Server
        then(Literal("restart").runs(lambda src:request.create(src,30,"restart")).
             then(Number("waiting").runs(lambda src, ctx: request.create(src, ctx, "restart")))).

        # & confirm
        then(Literal("confirm").runs(lambda :request.confirm())).
        # & cancel
        then(Literal("cancel").runs(lambda :request.cancel())).
        # & abort
        # ! Only server owner or request creator can abort it
        then(Literal("abort").
             requires(lambda src: (src.has_permission(4) | src.player == request.Request_info["posted_by"])).
             runs(lambda :request.abort()))
    )


# ^ Processing commands here

class Process:
    def __init__(self, server) -> None:
        self.server = server


class Request:
    Request_info = {"type": None, "posted_by": ""}
    Request_callback:callable = None
    Request_is_running=False
    Request_need_confirm=False

    def __init__(self, server):
        self.server = server
        self.server.execute("/bossbar add MCDR_Plugin.Power._counting")
        self.server.execute(
            "/bossbar set MCDR_Plugin.Power._counting color red")
        self.server.execute(
            "/bossbar set MCDR_Plugin.Power._counting style progress")

    def create(self, src, ctx, _type):
        if self.Request_is_running == True:
            self.server.reply(RText("已經有一個請求在執行了!!!", RColor=RColor.red))
            return
        elif self.Request_need_confirm==True:
            self.server.reply(RText("有一個請求待確認!，如果要執行新的請求，請先cancel目前的請求。", RColor=RColor.red))
            return

        self.Request_info["posted_by"] = src.player
        self.Request_info["type"] = _type.lower()
        self._waiting=ctx["waiting"]
        self.Request_need_confirm = True
        if _type == "shutdown":
            self.Request_callback = self.server.stop_exit()
        elif _type == "stop":
            self.Request_callback = self.server.stop()
        elif _type == "start":
            self.Request_callback = self.server.start()
        elif _type == "restart":
            self.Request_callback = self.server.restart()
        else:
            self.Request_info = {"type": None, "posted_by": ""}
            self.Request_need_confirm = False
            return


    def confirm(self):
        _type = self.Request_info["type"]
        _callback = self.Request_args
        self.Request_is_running=True
        self.Request_need_confirm=False

        self._COUNTING = _counting(self.server, _type, _callback, self._waiting)

    def cancel(self):
        self.Request_callback=None
        self.Request_need_confirm=False

    def abort(self):
        if self.Request_is_running == False:
            self.server.reply(RText("無請求在執行中!!!", RColor=RColor.red))
            return
        self.COUNTING.stop()
        while self.COUNTING.is_alive() is not True:
            pass
        self.Request_info = {"type": None, "posted_by": ""}
        self.Request_is_running = False
        self.Request_need_confirm = False
        self.server.execute(
            "/bossbar set MCDR_Plugin.Power._counting visible false")

    # TODO Counting Thread unfinished


class _counting(threading.Thread):
    def __init__(self, server, _type: str, _callback: callable, waiting: int = 10):
        super().__init__()
        self.setDaemon(True)
        self.setName("Power")
        self._stop_event = threading.Event()

        self.server = server

        self._type = _type
        self._callback = _callback
        self.waiting = waiting

    def run(self):
        self.server.execute(
            "/bossbar set MCDR_Plugin.Power._counting max {}".format(self.waiting))
        self.server.execute(
            "/bossbar set MCDR_Plugin.Power._counting visible true")
        for i in range(self.waiting):
            if (self.waiting-i == 60 | self.waiting-i == 30 | self.waiting-i == 15 | self.waiting-i == 10):
                self.server.boardcast(
                    RText("Server will {} soon! {} secs remaining.".format(self._type, self.waiting-i), RColor=RColor.red))
            elif self.waiting-i <= 10:
                self.join()
            elif self.waiting-i <= 5:
                self.server.boardcast(
                    RText("Countdown {} secs.".format(self.waiting-i), RColor=RColor.red))
            elif self.waiting-i <= 0:
                self._callback()
                break

            cd_rj = ["", {"text": self._type, "underlined": True, "color": "red"}, " in ", {
                "text": self.waiting-i, "bold": True, "color": "gold"}, " secs"]

            self.server.execute(
                "/bossbar set MCDR_Plugin.Power._counting value {}".format(self.waiting-i))
            self.server.execute(
                "/bossbar set MCDR_Plugin.Power._counting name {}".format(
                    str(cd_rj))
            )
            sleep(1)

    def stop(self):
        self._stop_event.set()
        self.join()
