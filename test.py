#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Test module
"""

from ApiCore import ApiCore

if __name__ == "__main__":
    API_CORE = ApiCore()
    for rec in API_CORE.get_finished_recordings():
        print rec["disp_title"]
