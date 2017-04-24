#!/usr/bin/env python
# ===--- format_projects_list.py ------------------------------------------===
#
#  This source file is part of the Swift.org open source project
#
#  Copyright (c) 2014 - 2017 Apple Inc. and the Swift project authors
#  Licensed under Apache License v2.0 with Runtime Library Exception
#
#  See https://swift.org/LICENSE.txt for license information
#  See https://swift.org/CONTRIBUTORS.txt for the list of Swift project authors
#
# ===----------------------------------------------------------------------===

"""Check for JSON syntax errors and format a given project index file."""

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
        help="a project index file to check (e.g. projects.json)",
        type=os.path.abspath
    )
    return parser.parse_args()


def main():
    # pylint: disable=I0011,C0111
    args = parse_args()

    parsed_project_index = sorted(
        json.JSONDecoder(
            object_pairs_hook=collections.OrderedDict
        ).decode(open(args.project_index).read()),
        key=lambda repo: repo['path']
    )

    json_string = strip_trailing_whitespace(
        json.dumps(parsed_project_index, sort_keys=False, indent=2)
    )

    open(args.project_index, 'w').write(json_string)

    return 0


if __name__ == "__main__":
    sys.exit(main())
