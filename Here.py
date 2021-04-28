# -*- coding: utf-8 -*-
import json
import re

PLUGIN_METADATA = {
    'id': 'here',
    'version': '1.0.1',
    'name': 'Here',
    'author': [
            'Fallen_Breath',
            'nathan21hz'
    ],
    'link': 'https://github.com/TISUnion/Here'
}

# set it to 0 to disable hightlight
# 将其设为0以禁用高亮
HIGHLIGHT_TIME = 15

here_user = 0


def process_coordinate(text):
    data = list((text.split(":")[-1].replace("d", "")
                 ).replace("[", "").replace("]", "").split(","))
    for i in range(len(data)):
        data[i] = float(data[i])
    return tuple(data)


def process_dimension(text):
    data = text.split(":")[-1].replace("\"", "")
    return data


def display(server, name, position, dimension):
    x, y, z = position


    _dimension=dimension

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

    texts = [
        '',

        '§e{}'.format(name),

        '§r @ ',
        # hacky fix for voxelmap yeeting text color in translated text
        {
            "translate": dimension_display[dimension],
            "color": dimension_color[dimension]
        },


        {
            'text': ' §b[x:{}, y:{}, z:{}]§r'.format(int(round(x)), int(round(y)), int(round(z))),
            'clickEvent':
                {
                'action': 'run_command',
                    'value': '!!tp {} {} {} {}'.format(x, y, z, _dimension)
            },
            "hoverEvent":{
                "action": "show_text",
                "contents":[
                    {"text":"點擊以傳送"}
                ]
            }
        }

    ]

    server.execute('tellraw @a {}'.format(json.dumps(texts)))
    global HIGHLIGHT_TIME
    if HIGHLIGHT_TIME > 0:
        server.execute('effect give {} minecraft:glowing {} 0 true'.format(
            name, HIGHLIGHT_TIME))


def on_info(server, info):
    global here_user
    if info.is_player and info.content == '!!here':
        if hasattr(server, 'MCDR') and server.is_rcon_running():
            name = info.player
            position = process_coordinate(re.search(
                r'\[.*\]', server.rcon_query('data get entity {} Pos'.format(name))).group())
            dimension = process_dimension(server.rcon_query(
                'data get entity {} Dimension'.format(name)))
            display(server, name, position, dimension)
        else:
            here_user += 1
            server.execute('data get entity ' + info.player)
    if not info.is_player and here_user > 0 and re.match(r'\w+ has the following entity data: ', info.content) is not None:
        name = info.content.split(' ')[0]
        dimension = re.search(r'(?<= Dimension: )(.*?),',
                              info.content).group().replace('"', '').replace(',', '')
        position_str = re.search(r'(?<=Pos: )\[.*?\]', info.content).group()
        position = process_coordinate(position_str)
        display(server, name, position, dimension)
        here_user -= 1


def on_load(server, old):
    server.register_help_message('!!here', '廣播坐標並發光玩家')
