#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from os.path import dirname, join as join_path

def sys_path():
    """ Add `./third_party` to `sys.path`.
    """
    
    third_party_dir = join_path(dirname(__file__), 'third_party')
    if not third_party_dir in sys.path:
        sys.path.insert(1, third_party_dir)
        
    
    


