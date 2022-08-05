#!/usr/bin/env python3
# ===--- reproduce.py -----------------------------------------------------===
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

"""Easily reproduce project compatibility failures.

Usage:
    # Build main Swift and execute all Alamofire build targets
    ./reproduce.py main --project-path Alamofire

    # Execute all Alamofire build targets using existing Swift
    ./reproduce.py main --project-path Alamofire --swiftc path/to/swiftc
"""

import argparse
import os
import sys

import common


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument("swift_branch")
    parser.add_argument("--project-path",
                        metavar="PATH",
                        help="relative repo path to specific project to build "
                             "(default: build all)")
    parser.add_argument("--swiftc",
                        metavar="PATH",
                        help="use specified swiftc instead of building "
                             "(default: build Swift)")
    parser.add_argument("--add-swift-flags",
                        metavar="FLAGS",
                        help='add flags to each Swift invocation',
                        default='')
    parser.add_argument("--skip-cleanup",
                        help="don't delete source and build directories",
                        action="store_true")
    parser.add_argument("--skip-swift-build",
                        help="don't invoke build-script",
                        action="store_true")
    parser.add_argument("--no-prompt",
                        help="default yes to all prompts",
                        action="store_true")
    parser.add_argument('--sandbox-profile-xcodebuild',
                        metavar='FILE',
                        help='sandbox xcodebuild build and test operations '
                             'with profile',
                        type=os.path.abspath)
    parser.add_argument('--sandbox-profile-package',
                        metavar='FILE',
                        help='sandbox package build and test operations with '
                             'profile',
                        type=os.path.abspath)
    parser.add_argument("--assertions",
                        help='Build Swift with asserts',
                        action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()
    common.set_swift_branch(args.swift_branch)
    common.debug_print('** REPRODUCE **')

    skip_swift_build = args.skip_swift_build
    if args.swiftc:
        skip_swift_build = True

    if not skip_swift_build:
        # Only prompt for deletion if directories exist
        have_existing_dirs = False
        if os.path.exists('./build') or os.path.exists('./swift') or \
           os.path.exists('./cmark'):
            have_existing_dirs = True

        # Optionally clean up previous source/build directories
        should_cleanup = False
        should_clone = False
        if have_existing_dirs and not args.skip_cleanup:
            if not args.no_prompt:
                response = input(
                    'Delete all build and source directories '
                    'in current working directory? (y/n): '
                ).strip().lower()
                if response == 'y':
                    should_cleanup = True
            else:
                should_cleanup = True
            if should_cleanup:
                common.check_execute(
                    ['./cleanup', args.swift_branch, '--skip-ci-steps']
                )
                should_clone = True
        else:
            should_clone = True

        # Build and install Swift and associated projects
        run_command = ['./run', args.swift_branch,
                       '--skip-ci-steps', '--skip-runner']
        if not should_clone:
            run_command += ['--skip-clone']
        if args.assertions:
            run_command += ['--assertions']
        common.check_execute(run_command, timeout=3600)

    # Build specified indexed project. Otherwise, build all indexed projects
    runner_command = [
        './runner.py',
        '--projects', 'projects.json',
        '--swift-branch', args.swift_branch,
        '--swift-version', '3',
        '--include-actions', 'action.startswith("Build")',
        '--verbose',
    ]
    if args.swiftc:
        runner_command += ['--swiftc', args.swiftc]
    else:
        runner_command += [
            '--swiftc', './build/compat_macos/install/toolchain/usr/bin/swiftc'
        ]
    if args.add_swift_flags: 
        runner_command += ['--add-swift-flags=%s' % args.add_swift_flags]
    if args.project_path:
        runner_command += ['--include-repos',
                           'path == "%s"' % args.project_path]
    if args.sandbox_profile_xcodebuild:
        runner_command += ['--sandbox-profile-xcodebuild',
                           args.sandbox_profile_xcodebuild]
    if args.sandbox_profile_package:
        runner_command += ['--sandbox-profile-package',
                           args.sandbox_profile_package]
    common.check_execute(runner_command)

    return 0

if __name__ == '__main__':
    sys.exit(main())
