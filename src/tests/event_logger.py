#######################################################################################
#    Title: event_logger source code
#    Author: Valentin Khaydarov
#    Date: 23.01.2021
#    Code version:  61db8c1
#    Availability: https://github.com/Praktikum-PvAS/planteye-common/blob/d3c44f18c880714189e12bc01217ef948ccc05ad/event_logger.py
#
#
#    MIT License
#
#    Copyright (c) 2021 Valentin Khaydarov
#    Copyright (c) 2021 Max Kirchner, Patrick Suwinski
#
#    Permission is hereby granted, free of charge, to any person obtaining a copy
#    of this software and associated documentation files (the "Software"), to deal
#    in the Software without restriction, including without limitation the rights
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the Software is
#    furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in all
#    copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#    SOFTWARE.
#
#######################################################################################

from datetime import datetime


def log_event(cfg, module, event, type, text_message):
    output_threshold = cfg['event_logger']['print_level']
    if output_threshold == 'DEBUG':
        print(compose_msg(module, type, text_message))
    elif output_threshold == 'INFO' and type in ['INFO', 'WARN', 'ERR']:
        print(compose_msg(module, type, text_message))
    elif output_threshold == 'WARN' and type in ['WARN', 'ERR']:
        print(compose_msg(module, type, text_message))
    elif output_threshold == 'ERR' and type in ['ERR']:
        print(compose_msg(module, type, text_message))

    if cfg['event_logger']['publish']:
        publish_event(event)


def compose_msg(module, type, text_message):
    msg_str = ''
    msg_str += str(datetime.now())
    msg_str += ' ['+module+']'
    msg_str += get_color(type) + '[' + type + '] ' + '\033[0m'
    msg_str += text_message
    return msg_str


def get_color(type):
    if type == 'INFO':
        return '\033[1m'
    elif type == 'WARN':
        return '\033[93m'
    elif type == 'ERR':
        return '\033[91m'
    else:
        return '\033[0m'


def publish_event(event):
    pass