# -*- coding: UTF-8 -*-

import xml.etree.ElementTree as ET


class Session:
    current_group = ''
    current_process = ''
    current_meeting = ''
    current_step = 'a'
    dic = {'current_group', 'current_process', 'current_meeting', 'current_step'}

    def load_session(self, path):
        try:
            tree = ET.parse(path)
            session = tree.getroot()
            self.current_group = session.find('current_group').text
            self.current_process = session.find('current_process').text
            self.current_meeting = session.find('current_meeting').text
            self.current_step = session.find('current_step').text
        except:
            self.rebuild_session(path)
            self.current_group = ''
            self.current_process = ''
            self.current_meeting = ''
            self.current_step = ''
        finally:
            return self

    def rebuild_session(self, path):
        session = ET.Element('session')
        ET.SubElement(session, 'current_group')
        ET.SubElement(session, 'current_process')
        ET.SubElement(session, 'current_meeting')
        ET.SubElement(session, 'current_step')
        tree = ET.ElementTree(session)
        tree.write(path, encoding='UTF-8')
