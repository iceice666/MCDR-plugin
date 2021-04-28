import json
import re
from time import sleep
from mcdreforged.api.decorator import new_thread

Prefix = "!!home"
help_msg = \
    '''==========MCDR-Home==========
§6{0} help §r顯示幫助
§6{0} sethome §r將目前位置設為家
§6{0} tp §r傳送回家
§6{0} cancel §r取消傳送
'''.format(Prefix)
format_error_msg = f"§c格式错误！请输入§6{Prefix} help§c查看帮助！"
data_path = "./config/home/data.json"

is_tp_canceled = False


def get_data(target):
    global data_path
    data = json.load(open(data_path))
    if data.get(target):
        return data[target]
    return None


def add_data(target, dim, x, y, z):
    global data_path
    data = json.load(open(data_path))
    data.update({target: {"dim": dim, "x": x, "y": y, "z": z}})
    print(data)
    open(data_path, 'w').write(json.dumps(data))


def on_info(server, info):
    global Prefix
    content = info.content
    cmd = content.split()

    MinecraftDataApi = server.get_plugin_instance('minecraft_data_api')

    if len(cmd) == 0 or cmd[0] != Prefix:
        return

    del cmd[0]

    if len(cmd) == 0 or (len(cmd)!=0 and cmd[0] == "help"):
        if len(cmd) != 1:
            server.reply(info, format_error_msg)
            return
        server.reply(info, help_msg)
        return

    if cmd[0] == "tp":
        _tp(server, info)

    if cmd[0] == "cancel":
        _cancel()

    if cmd[0] == "sethome":
        if len(cmd) != 1:
            server.reply(info, format_error_msg)
            return
        name = info.player
        position = process_coordinate(re.search(
            r'\[.*\]', server.rcon_query('data get entity {} Pos'.format(name))).group())
        dimension = process_dimension(server.rcon_query(
            'data get entity {} Dimension'.format(name)))

        _dimension = dimension

        dimension_convert = {
            'overworld': '0',
            'the_nether': '-1',
            'the_end': '1'
        }
        dimension_color = {
            '0': 'dark_green',
            '-1': 'dark_red',
            '1': 'dark_purple'
        }
        dimension_display = {
            '0':  'createWorld.customize.preset.overworld',
            '-1':  'advancements.nether.root.title',
            '1':  'advancements.end.root.title'
        }
        if dimension in dimension_convert:  # convert from 1.16 format to pre 1.16 format
            dimension = dimension_convert[dimension]

        x, y, z = position

        Text = [
            "",
            "設置",
            '§e{}'.format(name),
            "的家",
            "§r @ ",
            {
                "translate": dimension_display[dimension],
                "color": dimension_color[dimension]
            },
            {
                'text': f' §b[x:{int(round(x))}, y:{int(round(y))}, z:{int(round(z))}]§r',
            }
        ]

        server.execute(f"tellraw {name} {json.dumps(Text)}")
        add_data(info.player, _dimension, x, y, z)
        return


@new_thread("home.tp")
def _tp(server, info):
    if get_data(info.player) == None:
        server.reply(info, f"§c请先使用§6{Prefix} sethome§c设置家！")
        return

    global is_tp_canceled
    is_tp_canceled = False

    data = get_data(info.player)
    server.reply(info, "§a5秒後傳送...")
    server.reply(info, "輸入 !!home cancel 以取消")
    dim = data["dim"]
    x = data["x"]
    y = data["y"]
    z = data["z"]

    sleep(4)

    if is_tp_canceled:
        server.execute(
            f"execute at {info.player} run effect clear {info.player} minecraft:slowness")
        server.reply(info, "§c傳送已取消!")
        return

    server.execute(
        f"effect give {info.player} minecraft:slowness 2 255")
    sleep(1)
    server.execute(
        f"execute in {dim} run teleport {info.player} {x} {y} {z}")
    return


@new_thread("home.cancel")
def _cancel():
    global is_tp_canceled
    is_tp_canceled = True


def on_load(server, old_module):
    global Prefix
    server.register_help_message(Prefix + " help", "家插件的帮助")


def process_coordinate(text):
    data = list((text.split(":")[-1].replace("d", "")
                 ).replace("[", "").replace("]", "").split(","))
    for i in range(len(data)):
        data[i] = float(data[i])
    return tuple(data)


def process_dimension(text):
    data = text.split(":")[-1].replace("\"", "")
    return data
