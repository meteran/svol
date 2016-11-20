#!/usr/bin/env python3
# coding: utf-8
import argparse
import datetime
import os
import sys

import subprocess

MUTE = 'off'
UNMUTE = 'on'
TOGGLE = 'toggle'
UP = '+'
DOWN = '-'
NOTIFY_TIME = 3000

now = lambda: datetime.datetime.now()


def parse():
    parser = argparse.ArgumentParser(description='Change master volume and send notification.', prog='svol')
    subparsers = parser.add_subparsers(title='commands', dest='command')

    subparsers.add_parser('mute', help='mute the sounds')
    subparsers.add_parser('unmute', help='unmute the sounds')
    subparsers.add_parser('toggle', help='toggle mute')
    subparsers.required = True

    up = subparsers.add_parser('up', help='rise the volume')
    up.add_argument('percent', metavar='V', help="percent to upper the volume", type=int)
    down = subparsers.add_parser('down', help='low the volume')
    down.add_argument('percent', metavar='V', help="percent to lower the volume", type=int)

    return vars(parser.parse_args())


class Mixer(object):
    def __init__(self, cache='~/.cache/svol/notify_id'):
        self.cache = os.path.expanduser(cache)

    @property
    def notify_id(self):
        try:
            with open(self.cache, 'r') as f:
                time, id = eval(f.read())
            if now() - time > datetime.timedelta(milliseconds=NOTIFY_TIME * 2):
                return None
            return id
        except:
            return None

    @notify_id.setter
    def notify_id(self, new_id):
        try:
            with open(self.cache, 'w') as f:
                f.write(repr((now(), new_id)))
        except FileNotFoundError:
            os.makedirs(os.path.dirname(self.cache))
            self.notify_id = new_id
        except:
            pass

    @staticmethod
    def execute(cmd):
        return subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()

    def notify(self, log):
        percent, muted = self.parse_amixer(log)
        if not percent:
            return
        notify_id = self.notify_id

        if muted:
            notify = '{:^37}'.format('[[[MUTED]]]')
        else:
            notify = '[{:37}]'.format('=' * int(percent * 37 / 100))
        cmd = ['notify-send.sh', '-p', '-t', str(NOTIFY_TIME), 'Volume:', repr(notify)]
        if notify_id:
            cmd += ['-r', str(notify_id)]
        self.notify_id = self.execute(cmd)

    @staticmethod
    def parse_amixer(log):
        try:
            data = log.split('\n')[5].split()
            percent = data[4]
            percent = int(percent[percent.find('[') + 1:-2])
            muted = data[6]
            muted = muted[muted.find('[') + 1:-1] == 'off'
            return percent, muted
        except:
            return None, None

    def amixer(self, *options):
        self.notify(self.execute(['amixer', 'sset', 'Master'] + list(options)))

    def mute(self, muting):
        self.amixer(muting)

    def change(self, percent, direction):
        self.amixer(str(percent) + '%' + direction)


def main(command, **kwargs):
    mixer = Mixer()
    commands = {
        'mute': lambda: mixer.mute(MUTE),
        'unmute': lambda: mixer.mute(UNMUTE),
        'toggle': lambda: mixer.mute(TOGGLE),
        'up': lambda x: mixer.change(x, UP),
        'down': lambda x: mixer.change(x, DOWN),
    }

    commands[command](*kwargs.values())


if __name__ == '__main__':
    main(**parse())
