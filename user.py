# -*- coding: UTF-8 -*-

import os
import xml.etree.cElementTree as ET

import functions
import workflow
from session import Session


class User:
    user_id = ''
    nickname = ''
    follows = []
    followed = []
    interest = []
    favors = []
    attended_meetings = []
    missed_meetings = []

    # reserved meeting
    schedule = []

    # user command
    def get_nickname(self, userid):
        path = os.path.join(workflow.user_data_folder, userid + ".xml")
        tree = ET.parse(path)
        user = tree.getroot()
        _nickname = user.find('nickname')
        return _nickname.text

    def setname(self, nickname):
        if not os.path.exists(workflow.user_data_folder):
            os.makedirs(workflow.user_data_folder)
        if not os.path.isfile(self.__user_file_path()):
            user = ET.Element('user')
            ET.SubElement(user, 'id').text = self.user_id
            ET.SubElement(user, 'nickname').text = nickname
            tree = ET.ElementTree(user)
            tree.write(self.__user_file_path(), encoding='UTF-8')

        tree = ET.parse(self.__user_file_path())
        user = tree.getroot()
        _nickname = user.find('nickname')
        _nickname.text = nickname
        tree.write(self.__user_file_path(), encoding="UTF-8")
        return 'set nickname done.'

    # group command
    def creategroup(self, group_name):
        path = workflow.group_data_folder + group_name
        usersfilename = "users.xml"
        meetingsfilename = "meetings.xml"
        fullusersfilename = os.path.join(path, usersfilename)
        fullmeetingsfilename = os.path.join(path, meetingsfilename)
        if not os.path.exists(path):
            os.makedirs(path)
        else:
            return 'group name used,choose a different group name.'
        if not os.path.isfile(fullusersfilename):
            users = ET.Element('users')
            ET.SubElement(users, 'user').text = self.user_id
            tree = ET.ElementTree(users)
            tree.write(fullusersfilename, encoding="UTF-8")
        if not os.path.isfile(fullmeetingsfilename):
            meetings = ET.Element('meetings')
            meeting = ET.SubElement(meetings, 'meeting')
            ET.SubElement(meeting, 'state').text = 'done'
            tree = ET.ElementTree(meetings)
            tree.write(fullmeetingsfilename, encoding="UTF-8")
        # add group to user's groups element
        tree = ET.parse(self.__user_file_path())
        user = tree.getroot()
        groups = user.find('groups')
        if ET.iselement(groups):
            ET.SubElement(groups, 'group').text = group_name
        else:
            groups = ET.SubElement(user, 'groups')
            ET.SubElement(groups, 'group').text = group_name
        tree.write(self.__user_file_path(), encoding='UTF-8')
        return "Created group " + group_name

    def joingroup(self, groupname):
        message = 'Joined ' + groupname
        userfilepath = self.__user_file_path()
        grouppath = workflow.group_data_folder + groupname
        if not os.path.exists(grouppath):
            return '查无此群，请先创建群。使用命令:creategroup ' + groupname
        else:
            # update user file
            self.current_session().current_group = groupname
            tree = ET.parse(userfilepath)
            user = tree.getroot()
            groups = user.find('groups')
            for group in groups.findall('group'):
                if group.text == groupname:
                    self.entergroup(groupname)
                    return 'You have joined this group.'
            ET.SubElement(groups, 'group').text = groupname
            tree.write(userfilepath, encoding='UTF-8')

            # update group file
            tree = ET.parse(self.__group_users_file_path(groupname))
            users = tree.getroot()
            for user in users.findall('user'):
                if user.text == self.user_id:
                    self.entergroup(groupname)
                    return 'You have joined this group.'
            ET.SubElement(users, 'user').text = self.user_id
            tree.write(self.__group_users_file_path(groupname), encoding='UTF-8')
        return message

    def entergroup(self, groupname):
        session = self.current_session()
        if groupname in self.__belonged_groups():
            session.current_group = groupname
            session.current_step = 'a'
            session.current_meeting = ''
            self.save_session(session)
            return 'Now in group ' + groupname
        else:
            return 'You do not belong to this group, or the group does not exist.'

    def showgroupmembers(self, groupname):
        users_list = ''
        if self.__checkgroupexist(groupname):
            group_user_path = self.__group_users_file_path(groupname)
            tree = ET.parse(group_user_path)
            users = tree.getroot()
            for user in users.findall('user'):
                if ET.iselement(user):
                    username = self.get_nickname(user.text)
                    users_list += username + ' '
            return users_list
        else:
            return groupname + " does not exist."

    ## meeting command
    def createmeeting(self, parameter):
        session = self.current_session()
        session.current_process = 'createmeeting'
        if session.current_group is None:
            return "Enter a group first, with command:entergroup [group name]"
        meetingfilepath = os.path.join(workflow.group_data_folder, session.current_group, 'meetings.xml')
        self.__checkgroupstructure(session.current_group)
        tree = ET.parse(meetingfilepath)
        meetings = tree.getroot()
        if session.current_step == 'a':
            meeting = ET.SubElement(meetings, 'meeting')
            ET.SubElement(meeting, 'name').text = parameter
            ET.SubElement(meeting, 'sponsor').text = self.user_id
            ET.SubElement(meeting, 'state').text = '1'
            # to do, unique id
            meetingid = functions.get_id()
            ET.SubElement(meeting, 'uuid').text = meetingid
            attendusers = ET.SubElement(meeting, 'attendusers')
            ET.SubElement(attendusers, 'user').text = self.user_id
            tree.write(meetingfilepath, encoding='UTF-8')
            session.current_step = 'b'
            session.current_meeting = meetingid
            self.save_session(session)
            return 'feel free to enter meeting place...'

        if session.current_step == 'b':
            for meeting in meetings.findall('meeting'):
                uuid = meeting.find('uuid')
                if ET.iselement(uuid):
                    if uuid.text == session.current_meeting:
                        place = ET.SubElement(meeting, 'place')
                        place.text = parameter
                        break
            tree.write(meetingfilepath, encoding='UTF-8')
            session.current_step = 'c'
            self.save_session(session)
            return 'choose a date...'

        if session.current_step == 'c':
            for meeting in meetings.findall('meeting'):
                uuid = meeting.find('uuid')
                if ET.iselement(uuid):
                    if uuid.text == session.current_meeting:
                        ET.SubElement(meeting, 'date').text = parameter
                        break
            tree.write(meetingfilepath, encoding='UTF-8')
            session.current_step = 'd'
            self.save_session(session)
            return 'Input meeting content?'

        if session.current_step == 'd':
            for meeting in meetings.findall('meeting'):
                uuid = meeting.find('uuid')
                if ET.iselement(uuid):
                    if uuid.text == session.current_meeting:
                        ET.SubElement(meeting, 'content').text = parameter
                        break
            tree.write(meetingfilepath, encoding='UTF-8')
            session.current_process = ''
            session.current_step = 'a'
            self.save_session(session)
            return "It's done."

        session.current_step = 'a'
        self.save_session(session)
        return 'Failed'

    def entermeeting(self, parameter):
        session = self.current_session()
        meetingspath = self.__meetings_file_path()
        if meetingspath == '':
            return 'Need to enter a group first.(command:entergroup <groupname>)'
        else:
            tree = ET.parse(self.__meetings_file_path())
            meetings = tree.getroot()
            for meeting in meetings.findall('meeting'):
                name = meeting.find('name')
                if ET.iselement(name) and name.text == parameter:
                    session.current_meeting = meeting.find('uuid').text
                    self.save_session(session)
                    return 'you now in meeting:' + parameter
                uuid = meeting.find('uuid')
                if ET.iselement(uuid) and uuid.text == parameter:
                    session.current_meeting = parameter
                    self.save_session(session)
                    return 'you now in meeting:' + parameter
        return parameter + " not found."

    # parameter should be meeting name or its id
    def joinmeeting(self, parameter):
        meetingspath = self.__meetings_file_path()
        if meetingspath == '':
            return 'need to enter a group first.(command:entergroup <groupname>)'
        else:
            tree = ET.parse(self.__meetings_file_path())
            meetings = tree.getroot()
            for meeting in meetings.findall('meeting'):
                name = meeting.find('name')
                if ET.iselement(name):
                    if name.text == parameter:
                        self.current_session().current_meeting = meeting.find('uuid').text
                        attendusers = meeting.find('attendusers')
                        for user in attendusers.findall('user'):
                            if user.text == self.user_id:
                                return 'you have joined, be calm.'
                        ET.SubElement(attendusers, 'user').text = self.user_id
                        tree.write(meetingspath, encoding='UTF-8')
                        return 'you now joined meeting:' + parameter

                uuid = meeting.find('uuid')
                if ET.iselement(uuid) and uuid.text == parameter:
                    self.current_session().current_meeting = parameter
                    attendusers = meeting.find('attendusers')
                    for user in attendusers.findall('user'):
                        if user.text == self.user_id:
                            return 'you have joined, be calm.'
                    ET.SubElement(attendusers, 'user').text = self.user_id
                    tree.write(meetingspath, encoding='UTF-8')
                    return 'you now joined meeting:' + parameter
        return parameter + " not found."

    def showallmeetings(self, groupname=None):
        session = self.current_session()
        try:
            tree = ET.parse(self.__meetings_file_path(groupname))
        except:
            return 'can not find the group.'
        meetings = tree.getroot()
        undonemeetings = []
        message = 'meetings:'
        for meeting in meetings:
            state = meeting.find('state')
            if state is not None:
                if state.text is '1':
                    undonemeetings.append(meeting)
        for meeting in undonemeetings:
            name = meeting.find('name').text
            date = meeting.find('date').text
            place = meeting.find('place').text
            content = meeting.find('content').text
            message += '聚会名:' + name + '\r\n' \
                                       '日期:' + date + '\r\n' \
                                                      '地点:' + place + '\r\n' \
                                                                      '活动:' + content + '\r\n\r\n'
        return message

    def showattendusers(self, meetingname):
        message = ''
        if self.current_session().current_group == None:
            return 'Enter a group first. With command: joingroup [groupname] OR entergroup [groupname]'
        elif self.current_session().current_meeting == None:
            return 'Enter a meeting first. With command: joinmeeting [meetingname] OR entermeeting [meetingname]'
        else:
            tree = ET.parse(self.__meetings_file_path())
            meetings = tree.getroot()
            for meeting in meetings.findall('meeting'):
                name = meeting.find('name')
                if ET.iselement(name) and name.text == meetingname:
                    if meeting.find('state').text == '1':
                        attendusers = meeting.find('attendusers')
                        for user in attendusers.findall('user'):
                            if ET.iselement(user):
                                name = self.get_nickname(user.text)
                                if name is not None:
                                    message += name + ' '
            if message == '':
                message = 'Meeting not found.'
        return message

    def __init__(self, id):
        self.user_id = id
        if not os.path.exists(workflow.user_data_folder):
            os.makedirs(workflow.user_data_folder)
        if not os.path.isfile(self.__user_file_path()):
            user = ET.Element('user')
            ET.SubElement(user, 'id').text = self.user_id
            ET.SubElement(user, 'nickname').text = self.user_id
            ET.SubElement(user, 'groups')
            tree = ET.ElementTree(user)
            tree.write(self.__user_file_path(), encoding='UTF-8')

    def __belonged_groups(self):
        tree = ET.parse(self.__user_file_path())
        user = tree.getroot()
        group_list = []
        for group in user.iter('group'):
            group_list.append(group.text)
        return group_list

    def save_session(self, new_session):
        try:
            tree = ET.parse(self.__session_path())
            root = tree.getroot()
            for sub in new_session.dic:
                node = root.find(sub)
                if node is not None:
                    node.text = new_session.__dict__[sub]
            # root.find('current_group').text = new_session.current_group
            # root.find('current_process').text = new_session.current_process
            # root.find('current_step').text = new_session.current_step
            # root.find('current_meeting').text = new_session.current_meeting
            tree.write(self.__session_path(), encoding='UTF-8')
        except:
            self.current_session().rebuild_session(self.__session_path())

    def __user_file_path(self):
        return os.path.join(workflow.user_data_folder, self.user_id + ".xml")

    def __group_users_file_path(self, groupname):
        return workflow.group_data_folder + groupname + '/users.xml'

    def __meetings_file_path(self, groupname=None):
        if groupname is not None:
            return workflow.group_data_folder + groupname + '/meetings.xml'
        else:
            return workflow.group_data_folder + self.current_session().current_group + '/meetings.xml'

    def __session_path(self):
        sessionpath = os.path.join(workflow.user_data_folder, self.user_id + ".session")
        if not os.path.isfile(sessionpath):
            session = ET.Element("session")
            ET.SubElement(session, 'current_group')
            ET.SubElement(session, 'current_process')
            ET.SubElement(session, 'current_step')
            ET.SubElement(session, 'current_meeting')
            tree = ET.ElementTree(session)
            tree.write(sessionpath, encoding='UTF-8')
        return sessionpath

    def __checknicknamevalid(self):
        if self.get_nickname(self.user_id) is None or '':
            return "请先设置您的用户名。命令为:setname 李蛋"

    def __checkgroupstructure(self, group_name):
        path = workflow.group_data_folder + group_name
        usersfilename = "users.xml"
        meetingsfilename = "meetings.xml"
        fullusersfilename = os.path.join(path, usersfilename)
        fullmeetingsfilename = os.path.join(path, meetingsfilename)
        if not os.path.isfile(fullusersfilename):
            users = ET.Element('users')
            ET.SubElement(users, 'user').text = self.user_id
            tree = ET.ElementTree(users)
            tree.write(fullusersfilename, encoding="UTF-8")
        if not os.path.isfile(fullmeetingsfilename):
            meetings = ET.Element('meetings')
            meeting = ET.SubElement(meetings, 'meeting')
            ET.SubElement(meeting, 'state').text = '0'
            tree = ET.ElementTree(meetings)
            tree.write(fullmeetingsfilename, encoding="UTF-8")

    def __checkgroupexist(self, groupname):
        path = workflow.group_data_folder + groupname
        if os.path.isdir(path):
            return True
        else:
            return False

    # public method
    def current_session(self):
        session = Session()
        session.load_session(self.__session_path())
        return session
