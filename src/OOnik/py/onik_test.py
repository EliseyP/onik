#!/usr/bin/python3
# _*_ coding: utf-8
import sys
from onik import get_string_converted
for line in sys.stdin:
    sys.stdout.write(get_string_converted(line, titles_flag='on'))