
from mcdreforged.plugin.server_interface import ServerInterface
from mcdreforged.command.builder.command_node import Literal
import lib.plugin_metadata as pm

# ~ plugin metadata config ~

# * Metadata
plugin_metadata = pm.metadata()
plugin_metadata.set_value("id", "my_plugin")
plugin_metadata.set_value("author", "Myself")
plugin_metadata.set_value("version", "1.0.0")
plugin_metadata.set_value("name", "My Plugin")
plugin_metadata.set_value("prefix", "prefix")
plugin_metadata.set_value("description", "A MCDR plugin")
plugin_metadata.set_value("dependencies", {})
plugin_metadata.set_value("link", None)

PLUGIN_METADATA = plugin_metadata.get_settings()

# * help msg
plugin_help_msg = pm.help_msg()
plugin_help_msg.add_msg("=========={} v{}==========".format(
    plugin_metadata.get_value("prefix"),
    plugin_metadata.get_value("version"))
)

plugin_help_msg.add_msg("!!{}        顯示資訊".format(plugin_metadata.get_value("prefix")))
plugin_help_msg.add_msg("!!{} help   顯示幫助頁面".format(plugin_metadata.get_value("prefix")))

HELP_MSG = plugin_help_msg.get_value()

# * info msg
plugin_info_msg = pm.info_msg()
plugin_info_msg.add_msg("==================")
plugin_info_msg.add_msg("插件名稱: {}".format(plugin_metadata.get_value("name")))
plugin_info_msg.add_msg("版本: {}".format(plugin_metadata.get_value("version")))
plugin_info_msg.add_msg("作者: {}".format(plugin_metadata.get_value("author")))
plugin_info_msg.add_msg("敘述: {}".format(plugin_metadata.get_value("description")))
plugin_info_msg.add_msg("==================")

INFO_MSG = plugin_info_msg.get_value()
# ~ ======================== ~


def on_load(server: ServerInterface, old_module):

    process = Process(server)

    # ^ Command System
    server.register_help_message(f'!!{plugin_metadata.get_value("prefix")}',
                                 {plugin_metadata.get_value("description")})
    server.register_command(
        # &
        Literal(f'!!{plugin_metadata.get_value("prefix")}').runs(lambda server: server.reply(INFO_MSG)).
        # & help
        then(
            Literal("help").runs(lambda server: server.reply(HELP_MSG))
        )
    )

# ^ Processing commands here
class Process:
    def __init__(self, server):
        self.server = server
