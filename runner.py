#!/usr/bin/env python3
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
import multiprocessing
import sys

import common
import project

from concurrent import futures


# We create factories in the async function rather then pass them in because they are not pickle-able.
# A better solution should be developed.
def build_project_async(_project, args, xcodebuild_flags, time_reporter):
    action_builder = project.CompatActionBuilder.factory(
        args.swiftc,
        args.swift_version,
        args.swift_branch,
        args.job_type,
        args.sandbox_profile_xcodebuild,
        args.sandbox_profile_package,
        args.add_swift_flags,
        xcodebuild_flags,
        args.skip_clean,
        args.build_config,
        args.strip_resource_phases,
        args.only_latest_versions,
        args.project_cache_path,
        time_reporter,
        args.override_swift_exec
    )

    version_builder = project.VersionBuilder.factory(
        args.include_actions,
        args.exclude_actions,
        args.verbose,
        action_builder,
    )

    project_builder = project.ProjectBuilder(
        args.include_versions,
        args.exclude_versions,
        args.verbose,
        version_builder,
        target=_project
    )
    return project_builder.build()

def parse_args():
    """Return parsed command line arguments."""
    # There is no arg for process count yet. There should be
    parser = argparse.ArgumentParser()
    project.add_arguments(parser)
    parser.add_argument('--only-latest-versions', action='store_true')
    parser.add_argument('--default-timeout', type=int, help="override the default execute timeout (seconds)")
    return parser.parse_args()


def main():
    """Execute specified indexed project actions."""
    thread_pool = futures.ProcessPoolExecutor(max_workers=multiprocessing.cpu_count())
    submited_futures = []

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

    project_list_builder = project.ProjectListBuilder(
        args.include_repos,
        args.exclude_repos,
        args.verbose,
        None,  # Just don't worry about building with this object. We use this for inclusion/exclusion for now
        index)

    # Setup results object
    results = project_list_builder.new_result()

    ###################################
    # PARALLELIZE builds for projects across worker pool. We parallelize at the project level to avoid conflicting
    # git operations and to avoid the need for multiple source checkouts of a project.
    for _project in project_list_builder.subtargets():
        # Call async worker function. Within that function
        #   1.) Create ProjectBuilder Object which is primed for building
        #   2.) Build the project and all associated versions
        #   3.) Return the result object which will be examined later
        if not project_list_builder.included(_project):
            continue
        worker = thread_pool.submit(build_project_async, _project, args, xcodebuild_flags, time_reporter)
        submited_futures.append(worker)
    ###################################

    # Cleanup in main process
    futures.wait(submited_futures)
    for _future in submited_futures:
        results.add(_future.result())

    common.debug_print(str(results))
    return 0 if results.result in [project.ResultEnum.PASS,
                                   project.ResultEnum.XFAIL] else 1

if __name__ == '__main__':
    sys.exit(main())
