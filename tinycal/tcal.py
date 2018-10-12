from __future__ import print_function

import calendar
import os.path

from . import CALRC
from .argparse import parser
from .config import TinyCalConfig
from .render import render


def read_config():
    calrcs = [rc for rc in map(os.path.expanduser, CALRC) if os.path.exists(rc)]
    if not calrcs:
        return []

    # read lines and strip
    lines = map(str.strip, open(calrcs[0]))
    # remove empty or commented lines
    lines_ = (line for line in lines if line and not line.startswith('#'))
    # parse configuration lines
    parse_line = lambda line: tuple(map(str.strip, line.split('=', 1)))
    config = map(parse_line, lines_)
    return [(k, v) for k, v in config if v is not None]  # TODO: internal variable is different


def get_command_arguments():
    """
    :rtype: [(str, str)]
    """
    return [(k, v) for k, v in vars(parser.parse_args()).items() if v is not None]


def main():
    # Ref: https://stackoverflow.com/questions/16878315/what-is-the-right-way-to-treat-python-argparse-namespace-as-a-dictionary
    cfg = dict(read_config() + get_command_arguments())
    config = TinyCalConfig(cfg)

    cal = calendar.Calendar(firstweekday=calendar.MONDAY if config.start_monday else calendar.SUNDAY)
    lines = render(cal, config)
    print(*lines, sep='\n')


if __name__ == '__main__':
    main()
