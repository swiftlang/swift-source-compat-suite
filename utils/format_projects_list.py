#!/usr/bin/env python3
# ===--- format_projects_list.py ------------------------------------------===
#
#  This source file is part of the Swift.org open source project
#
#  Copyright (c) 2014 - 2022 Apple Inc. and the Swift project authors
#  Licensed under Apache License v2.0 with Runtime Library Exception
#
#  See https://swift.org/LICENSE.txt for license information
#  See https://swift.org/CONTRIBUTORS.txt for the list of Swift project authors
#
# ===----------------------------------------------------------------------===

"""Check for JSON syntax errors and format a given project index file or directory."""

import argparse
import os
import json
import sys
import collections
import re


def strip_trailing_whitespace(text):
    """Return text stripped of trailing whitespace."""
    return re.sub(r'\s+$', '', text, flags=re.M)


def parse_args():
    """Return parsed command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "project_index",
        help="a project index file or directory of per-project JSON files",
        type=os.path.abspath
    )
    return parser.parse_args()


def format_file(path):
    with open(path) as f:
        parsed = json.JSONDecoder(
            object_pairs_hook=collections.OrderedDict
        ).decode(f.read())

    if isinstance(parsed, list):
        parsed = sorted(parsed, key=lambda repo: repo['path'])

    json_string = strip_trailing_whitespace(
        json.dumps(parsed, sort_keys=False, indent=2)
    )

    with open(path, 'w') as f:
        f.write(json_string)


def main():
    # pylint: disable=I0011,C0111
    args = parse_args()

    if os.path.isdir(args.project_index):
        for filename in os.listdir(args.project_index):
            if filename.endswith('.json'):
                format_file(os.path.join(args.project_index, filename))
    else:
        format_file(args.project_index)

    return 0


if __name__ == "__main__":
    sys.exit(main())
