# -*- coding: UTF-8 -*-

import xml.etree.ElementTree as ET

import workflow


class Group:
    group_id = ''

    def __init__(self, groupname):
        self.group_id = groupname

    def meeting_records_folder(self):
        return workflow.group_data_folder + self.group_id

    def group_file_path(self):
        return workflow.group_data_folder + self.group_id

    def add_user(self, user):
        pass

    def createmeeting(self):
        pass

    def meetings(self):
        group = ET.parse(self.group_file_path())
        meeting_list = []
        for meeting in group.iter('meeting'):
            meeting_list.append(meeting)
        return meeting_list

    def load_group(self):
        tree = ET.parse(self.group_file_path())
