# -*- coding: utf-8 -*-
"""
Defining some global system variables!
"""

Dynamic_param = []
Global_param = []
Static_param = []

class Param:

def initialize_Dynamic_param(data):
    global Dynamic_param
    Dynamic_param = data.set_index('Name')


def initialize_Global_param(data):
    global Global_param
    Global_param = data


def initialize_Static_param(data):
    global Static_param
    Static_param = data.set_index('Name')


def get_Global_param():
    return Global_param


def get_Static_param():
    return Static_param


def get_Dynamic_param():
    return Dynamic_param
