#!/usr/bin/env python3
# ===--- build_incremental.py ---------------------------------------------===
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

"""Build a collection of Swift projects in incremental mode, collecting stats."""

import argparse
import json
import sys

import common
import project


def parse_args():
    """Return parsed command line arguments."""
    parser = argparse.ArgumentParser()
    project.add_arguments(parser)
    return parser.parse_args()


def main():
    """Execute specified indexed project actions."""
    args = parse_args()

    with open(args.projects) as projects:
        index = json.loads(projects.read())

    result = project.ProjectListBuilder(
        args.include_repos,
        args.exclude_repos,
        args.verbose,
        args.process_count,
        project.ProjectBuilder.factory(
            args.include_actions,
            args.exclude_actions,
            args.verbose,
            project.IncrementalActionBuilder.factory(
                args.swiftc,
                args.swift_version,
                args.swift_branch,
                args.job_type,
                args.sandbox_profile_xcodebuild,
                args.sandbox_profile_package,
                args.add_swift_flags,
                args.build_config,
                args.strip_resource_phases
            ),
        ),
        index
    ).build()
    common.debug_print(str(result))
    return 0 if result.result in [project.ResultEnum.PASS,
                                  project.ResultEnum.XFAIL] else 1

if __name__ == '__main__':
    sys.exit(main())
