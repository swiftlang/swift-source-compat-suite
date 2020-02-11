#!/usr/bin/env python
# ===--- runner.py --------------------------------------------------------===
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

"""Build and optionally compatibility test a collection of Swift projects."""

import argparse
import json
import sys

import common
import project_future


def parse_args():
    """Return parsed command line arguments."""
    parser = argparse.ArgumentParser()
    project_future.add_arguments(parser)
    parser.add_argument('--only-latest-versions', action='store_true')
    parser.add_argument('--default-timeout', type=int, help="override the default execute timeout (seconds)")
    return parser.parse_args()


def main():
    """Execute specified indexed project actions."""
    args = parse_args()

    if args.default_timeout:
        common.set_default_execute_timeout(args.default_timeout)

    index = json.loads(open(args.projects).read())
    result = project_future.ProjectListBuilder(
        args.include_repos,
        args.exclude_repos,
        args.verbose,
        project_future.ProjectBuilder.factory(
            args.include_versions,
            args.exclude_versions,
            args.verbose,
            project_future.VersionBuilder.factory(
                args.include_actions,
                args.exclude_actions,
                args.verbose,
                project_future.CompatActionBuilder.factory(
                    args.swiftc,
                    args.swift_version,
                    args.swift_branch,
                    args.sandbox_profile_xcodebuild,
                    args.sandbox_profile_package,
                    args.add_swift_flags,
                    args.add_xcodebuild_flags,
                    args.skip_clean,
                    args.build_config,
                    args.strip_resource_phases,
                    args.only_latest_versions
                ),
            ),
        ),
        index
    ).build()
    common.debug_print(str(result))
    return 0 if result.result in [project_future.ResultEnum.PASS,
                                  project_future.ResultEnum.XFAIL] else 1

if __name__ == '__main__':
    sys.exit(main())
