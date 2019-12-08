# -*- coding: utf-8 -*-

import sys

reload(sys)
sys.setdefaultencoding('utf8')

app_folder = "/root/appdata/"
group_data_folder = app_folder + "group_data/"
user_data_folder = app_folder + "user_data/"

help_dict = {"help": "显示帮助文档。",
             "setname YOUR_NICKNAME": "设置nickname。eg. setname 王富贵",
             "creategroup GROUP_NAME": "创建群。eg. creategroup 约饭群",
             "createmeeting MEETING_NAME": "创建聚会。eg. createmeeting 一起吃饭",
             "entergroup GROUP_NAME": "进如群看看。eg. entergroup 吃饭群",
             "entermeeting MEETING_NAME": "进入聚会看看。eg. entermeeting 一起吃饭",
             "joingroup GROUP_NAME": "加入群。eg. joingroup 吃饭群",
             "joinmeeting MEETING_NAME": "加入聚会。eg. joinmeeting 一起吃饭",
             "showattendusers MEETING_NAME": "在一个聚会中查看参加的人。eg. showattendusers 一起吃饭",
             "showallmeetings [GROUP_NAME]": "显示当前定位的群里的聚会。",
             "follow NICKNAME": "跟随一个人，随行参加聚会。",
             "showgroupmembers GROUPNAME": "显示群内成员。"}


def help():
    help_doc = ''
    for command in sorted(help_dict):
        help_doc += command + ":" + help_dict[command] + "\r\n"
    return help_doc


def undone():
    return "Sorry, function undone."


def make_response(request):
    session = request.user.current_session()
    command = request.content
    parameter = ''
    if ' ' in request.content:
        command = request.content.split(' ', 1)[0]
        parameter = request.content.split(' ', 1)[1]

        # if request.user.get_nickname(request.user.user_id) is None or '':
        #   return "请先设置您的用户名。命令为:setname Li lei"

    if command == "help":
        return help()

    if parameter is not '':
        if command == "setname":
            return request.user.setname(parameter)

        if command == "creategroup":
            return request.user.creategroup(parameter)

        if command == "createmeeting":
            return request.user.createmeeting(parameter)

        if command == "entergroup":
            return request.user.entergroup(parameter)

        if command == "entermeeting":
            return request.user.entermeeting(parameter)

        if command == "joingroup":
            return request.user.joingroup(parameter)

        if command == "joinmeeting":
            return request.user.joinmeeting(parameter)

        if command == "showattendusers":
            return request.user.showattendusers(parameter)

        if command == "showallmeetings":
            return request.user.showallmeetings(parameter)

        if command == "follow":
            return undone()

        # group function
        if command == "showgroupmembers":
            return request.user.showgroupmembers(parameter)
    else:
        if command == "showallmeetings":
            return request.user.showallmeetings()

        if (session.current_process == 'createmeeting'):
            return request.user.createmeeting(command)

    return help()
