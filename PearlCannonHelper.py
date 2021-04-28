# author hai_dan
# -*- coding: utf-8 -*-
import math

helpmessage = '''------MCDR PearlCannonHelper插件------
命令帮助如下:
§d!!pch§r -§e显示帮助§r
§d!!pch§r §a南模块tnt数 北模块tnt数 方向(s/w/e/n) 抛射or平射(p/h) 珍珠x 珍珠y（y无视小数点） 珍珠z 迭代次数 -§e计算珍珠位置§r
--------------------------------'''
# 南模块tnt数-n_south 北模块tnt数-n_north 珍珠x-x0 珍珠y(y无视小数点)-y0 珍珠z-z0 抛射or平射(p/h)-l 方向(s/w/e/n)-d 迭代次数-n
TNTX_h = 0.6025418158344771  # 平射TNT平均x动量
TNTZ_h = 0.6025418158344771  # 平射TNT平均z动量

TNTX_p = 0.6027148878083045  # 抛射TNT平均x动量
TNTY_p = 0.00660668038017551  # 抛射TNT平均y动量
TNTZ_p = 0.6027148878083045  # 抛射TNT平均z动量


def pch(n_south, n_north, d, l, x0, y0, z0, n, ground, server):
    if (d == 's'):
        d_1 = 0
        d_2 = 1
        d_3 = 0
        d_4 = 0
    elif (d == 'n'):
        d_1 = 0
        d_2 = 1
        d_3 = 1
        d_4 = 1
    elif (d == 'e'):
        d_1 = 0
        d_2 = 0
        d_3 = 1
        d_4 = 0
    elif (d == 'w'):
        d_1 = 1
        d_2 = 1
        d_3 = 1
        d_4 = 0

    if (l == 'h'):
        X_pearl = math.pow(-1, d_1) * n_north * TNTX_h + math.pow(-1, d_2) * n_south * TNTX_h
        Y_pearl = 0.17222175681389865 -(n_north + n_south - 1) * 0.00223550446065321
        Z_pearl = math.pow(-1, d_3) * n_north * TNTZ_h +math.pow(-1, d_4) * n_south * TNTZ_h
        xn = x0
        yn = y0 + 0.34569841881112
        Yn = Y_pearl
        zn = z0
    elif (l == 'p'):
        X_pearl = math.pow(-1, d_1) * n_north * TNTX_p + math.pow(-1, d_2) * n_south * TNTX_p
        Y_pearl = 0.20652248346913912 + (n_north + n_south) * TNTY_p
        Z_pearl = math.pow(-1, d_3) * n_north * TNTZ_p + math.pow(-1, d_4) * n_south * TNTZ_p
        xn = x0
        yn = y0 + 0.35776585772251
        Yn = Y_pearl
        zn = z0

    for i in range(n):
        xn = xn + X_pearl * math.pow(0.99, i - 1)
        yn = yn + Yn
        Yn = Yn * 0.99 - 0.03
        zn = zn + Z_pearl * math.pow(0.99, i - 1)
        if yn < ground:
            break
        server.broadcast('第§d%dt§r珍珠的坐标为(%f,%f,%f)' % (i+1, xn, yn, zn))


def on_info(server, info):
    if info.is_player:
        if info.content.startswith('!!pch'):
            cmdList = info.content.split(' ')
            cmdLen = len(cmdList)
            if cmdLen == 1:
                server.say(helpmessage)
            elif cmdLen == 10:
                pch(float(cmdList[1]), float(cmdList[2]), cmdList[3], cmdList[4], float(
                    cmdList[5]), int(math.floor(cmdList[6])), float(cmdList[7]), int(cmdList[8]), int(cmdList[9]), server)
            else:
                server.say('输入格式错误')


def on_load(server, old):
    server.register_help_message('!!pch', '一个珍珠炮助手插件')
