#!/usr/bin/env python3
# ===--- runner.py --------------------------------------------------------===
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

"""Build and optionally compatibility test a collection of Swift projects."""

import argparse
import json
import sys

import common
import project


def parse_args():
    """Return parsed command line arguments."""
    parser = argparse.ArgumentParser()
    project.add_arguments(parser)
    parser.add_argument('--only-latest-versions', action='store_true')
    parser.add_argument('--default-timeout', type=int, help="override the default execute timeout (seconds)")
    return parser.parse_args()


def main():
    """Execute specified indexed project actions."""
    args = parse_args()

    if args.default_timeout:
        common.set_default_execute_timeout(args.default_timeout)

    # DISABLED DUE TO: rdar://59302454.
    # To track removing this line: rdar://59302467.
    xcodebuild_flags = args.add_xcodebuild_flags
    xcodebuild_flags += (' ' if xcodebuild_flags else '') + 'DEBUG_INFORMATION_FORMAT=dwarf'

    # Use clang for building xcode projects.
    if args.clang:
        xcodebuild_flags += ' CC=%s' % args.clang

    swift_flags = args.add_swift_flags

    time_reporter = None
    if args.report_time_path:
        time_reporter = project.TimeReporter(args.report_time_path)

    with open(args.projects) as projects:
        index = json.loads(projects.read())

    result = project.ProjectListBuilder(
        args.include_repos,
        args.exclude_repos,
        args.verbose,
        args.process_count,
        project.ProjectBuilder.factory(
            args.include_versions,
            args.exclude_versions,
            args.verbose,
            project.VersionBuilder.factory(
                args.include_actions,
                args.exclude_actions,
                args.verbose,
                project.CompatActionBuilder.factory(
                    args.swiftc,
                    args.swift_version,
                    args.swift_branch,
                    args.job_type,
                    args.sandbox_profile_xcodebuild,
                    args.sandbox_profile_package,
                    swift_flags,
                    xcodebuild_flags,
                    args.skip_clean,
                    args.build_config,
                    args.strip_resource_phases,
                    args.only_latest_versions,
                    args.project_cache_path,
                    time_reporter,
                    args.override_swift_exec
                ),
            ),
        ),
        index
    ).build()
    common.debug_print(str(result))

    if args.junit:
        with open('results.xml', 'w') as results:
            results.write(result.xml_string())

    return 0 if result.result in [project.ResultEnum.PASS,
                                  project.ResultEnum.XFAIL] else 1

if __name__ == '__main__':
    sys.exit(main())
