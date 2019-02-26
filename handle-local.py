# -*- coding: UTF-8 -*-

import workflow
from request import Request
from user import User


while 1:
    user = User('A-B-C-D')
    request = Request(user, raw_input())
    print workflow.make_response(request)
