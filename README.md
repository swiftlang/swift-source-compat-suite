# Swift Source Compatibility Suite

Source compatibility is a strong goal for future Swift releases. To aid in this
goal, a community owned source compatibility test suite serves to regression
test changes to the compiler against a (gradually increasing) corpus of Swift
source code. Projects added to this test suite are periodically built against
the latest development versions of Swift as part of [Swift's continuous
integration system](https://ci.swift.org), allowing Swift compiler developers to
understand the compatibility impact their changes have on real-world Swift
projects.

## Python Support
The Source compatibility suite currently supports Python 3.8+. You may experience performance issues if you attempt to execute any of the associated files with a lesser version of Python 3.

## Current List of Projects

The <a href="https://swift.org/source-compatibility/#current-list-of-projects">current list of projects</a> can be viewed on Swift.org.

## Adding Projects

The Swift source compatibility test suite is community driven, meaning that open
source Swift project owners are encouraged to submit their projects that meet
the acceptance criteria for inclusion in the test suite. Projects added to the
suite serve as general source compatibility tests and are afforded greater
protection against unintentional source breakage in future Swift releases.

### Acceptance Criteria

To be accepted into the Swift source compatibility test suite, a project must:

1. Target Linux, macOS, or iOS/tvOS/watchOS device
2. Be an *Xcode* or *Swift Package Manager* project (Carthage and CocoaPods are currently unsupported but are being explored to be supported in the future)
3. Support building on either Linux or macOS
4. Be contained in a publicly accessible git repository
5. Maintain a project branch that builds against Swift 4.2 compatibility mode
   and passes any unit tests
6. Have maintainers who will commit to resolve issues in a timely manner
7. Be compatible with the latest GM/Beta versions of *Xcode* and *swiftpm*
8. Add value not already included in the suite
9. Be licensed with one of the following permissive licenses:
	* BSD
	* MIT
	* Apache License, version 2.0
	* Eclipse Public License
	* Mozilla Public License (MPL) 1.1
	* MPL 2.0
	* CDDL

Note: Linux compatibility testing in continuous integration is not available
yet, but Linux projects are being accepted now.

### Adding a Project

To add a project meeting the acceptance criteria to the suite, perform the
following steps:

1. Ensure the project builds successfully at a chosen commit against
   Swift 4.2 GM
2. Create a pull request against the [source compatibility suite
   repository](https://github.com/apple/swift-source-compat-suite),
   modifying **projects.json** to include a reference to the project being added
   to the test suite.

The project index is a JSON file that contains a list of repositories containing
Xcode and/or Swift Package Manager target actions.

To add a new Swift Package Manager project, use the following template:

~~~json
{
  "repository": "Git",
  "url": "https://github.com/example/project.git",
  "path": "project",
  "branch": "master",
  "maintainer": "email@example.com",
  "compatibility": [
    {
      "version": "4.2",
      "commit": "195cd8cde2bb717242b3081f9c367ccd0a2f0121"
    }
  ],
  "platforms": [
    "Darwin"
  ],
  "actions": [
    {
      "action": "BuildSwiftPackage",
      "configuration": "release"
    },
    {
      "action": "TestSwiftPackage"
    }
  ]
}
~~~

The `compatibility` field contains a list of version dictionaries, each
containing a Swift version and a commit. Commits are checked out before
building a project in the associated Swift version compatibility mode. The
Swift version is the earliest version of Swift known to compile the project at
the given commit. The goal is to have multiple commits at different points in a
project's history that are compatible with all supported Swift version
compatibility modes.

The `platforms` field specifies the platforms that can be used to build the
project. Linux and Darwin can currently be specified.

If tests aren't supported, remove the test action entry.

To add a new Swift Xcode workspace, use the following template:

~~~json
{
  "repository": "Git",
  "url": "https://github.com/example/project.git",
  "path": "project",
  "branch": "master",
  "maintainer": "email@example.com",
  "compatibility": [
    {
      "version": "4.2",
      "commit": "195cd8cde2bb717242b3081f9c367ccd0a2f0121"
    }
  ],
  "platforms": [
    "Darwin"
  ],
  "actions": [
    {
      "action": "BuildXcodeWorkspaceScheme",
      "workspace": "project.xcworkspace",
      "scheme": "project OSX",
      "destination": "platform=macOS",
      "configuration": "Release"
    },
    {
      "action": "BuildXcodeWorkspaceScheme",
      "workspace": "project.xcworkspace",
      "scheme": "project iOS",
      "destination": "generic/platform=iOS",
      "configuration": "Release"
    },
    {
      "action": "BuildXcodeWorkspaceScheme",
      "workspace": "project.xcworkspace",
      "scheme": "project tvOS",
      "destination": "generic/platform=tvOS",
      "configuration": "Release"
    },
    {
      "action": "BuildXcodeWorkspaceScheme",
      "workspace": "project.xcworkspace",
      "scheme": "project watchOS",
      "destination": "generic/platform=watchOS",
      "configuration": "Release"
    },
    {
      "action": "TestXcodeWorkspaceScheme",
      "workspace": "project.xcworkspace",
      "scheme": "project OSX",
      "destination": "platform=macOS"
    },
    {
      "action": "TestXcodeWorkspaceScheme",
      "workspace": "project.xcworkspace",
      "scheme": "project iOS",
      "destination": "platform=iOS Simulator,name=iPhone 7"
    },
    {
      "action": "TestXcodeWorkspaceScheme",
      "workspace": "project.xcworkspace",
      "scheme": "project tvOS",
      "destination": "platform=tvOS Simulator,name=Apple TV 1080p"
    }
  ]
}
~~~

To add a new Swift Xcode project, use the following template:

~~~json
{
  "repository": "Git",
  "url": "https://github.com/example/project.git",
  "path": "project",
  "branch": "master",
  "maintainer": "email@example.com",
  "compatibility": [
    {
      "version": "4.2",
      "commit": "195cd8cde2bb717242b3081f9c367ccd0a2f0121"
    }
  ],
  "platforms": [
    "Darwin"
  ],
  "actions": [
    {
      "action": "BuildXcodeProjectTarget",
      "project": "project.xcodeproj",
      "target": "project",
      "destination": "generic/platform=iOS",
      "configuration": "Release"
    }
  ]
}
~~~

After adding a new project to the index, ensure it builds successfully at the
pinned commits against the specified versions of Swift. In the examples,
the commits are specified as being compatible with Swift 4.2, which is included
in Xcode 10.

~~~bash
# Select Xcode 10 GM
sudo xcode-select -s /Applications/Xcode.app
# Build project at pinned commit against selected Xcode
./project_precommit_check project-path-field --earliest-compatible-swift-version 4.2
~~~

On Linux, you can build against the Swift 4.2 release toolchain:

~~~bash
curl -O https://swift.org/builds/swift-4.2-release/ubuntu1604/swift-4.2-RELEASE/swift-4.2-RELEASE-ubuntu16.04.tar.gz
tar xzvf swift-4.2-RELEASE-ubuntu16.04.tar.gz
./project_precommit_check project-path-field --earliest-compatible-swift-version 4.2 --swiftc swift-4.2-RELEASE-ubuntu15.10/usr/bin/swiftc
~~~

## Maintaining Projects

In the event that Swift introduces a change that breaks source compatibility
with a project (e.g., a compiler bug fix that fixes wrong behavior in the
compiler), project maintainers are expected to update their projects and submit
a new pull request with the updated commit hash within two weeks of being
notified. Otherwise, unmaintained projects may be removed from the project
index.

## Pull Request Testing

Pull request testing against the Swift source compatibility suite can be
executed by commenting with `@swift-ci Please test source compatibility` in a
Swift pull request.

## Building Projects

To build all projects against a specified Swift compiler locally, use the
`runner.py` utility as shown below.

~~~bash
./runner.py --swift-branch main --projects projects.json --include-actions 'action.startswith("Build")' --swiftc path/to/swiftc
~~~

Use the `--include-repos` flag to build a specific project.

~~~bash
./runner.py --swift-branch main --projects projects.json --include-actions 'action.startswith("Build")' --include-repos 'path == "Alamofire"' --swiftc path/to/swiftc
~~~

By default, build output is redirected to per-action `.log` files in the current
working directory. To change this behavior to output build results to standard
out, use the `--verbose` flag.

## Marking actions as expected failures

When an action is expected to fail for an extended period of time, it's
important to mark the action as an expected failure to make new failures more
visible.

To mark an action as an expected failure, add an `xfail` entry for the correct
Swift version and branch to the failing actions, associating each with a link
to a JIRA issue reporting the relevant failure. The following is an example of
an action that's XFAIL'd when building against Swift main branch in 4.2
compatibility mode.

~~~json
{
  "repository": "Git",
  "url": "https://github.com/example/project.git",
  "path": "project",
  "branch": "master",
  "maintainer": "email@example.com",
  "compatibility": [
    {
      "version": "4.2",
      "commit": "195cd8cde2bb717242b3081f9c367ccd0a2f0121"
    }
  ],
  "platforms": [
    "Darwin"
  ],
  "actions": [
    {
      "action": "BuildXcodeProjectTarget",
      "project": "project.xcodeproj",
      "target": "project",
      "destination": "generic/platform=iOS",
      "configuration": "Release",
      "xfail": {
        "issue": "https://github.com/apple/swift/issues/9999",
        "compatibility": "4.2",
        "branch": "main"
      }
    }
  ]
}
~~~

Additional Swift branches and versions can be added to XFAIL different
configurations. The currently supported fields for XFAIL entries are:

- `"compatibility"`: the Swift version(s) it fails with, e.g. `"4.0"`
- `"branch"`: the branch(es) of the swift compiler it fails with, e.g.
  `"swift-5.1-branch"`
- `"platform"`: the platform(s) it fails on, e.g. `"Darwin"` or `"Linux"`
- `"configuration"`: the build configuration(s) if fails with, i.e. `"release"`
  or `"debug"`)
- `"job"`: Allows XFailing the project for only the source compatibility build 
  or the SourceKit Stress Tester. Use `"source-compat"` to only XFail the Source 
  Compatibility Suite CI job and `"stress-test"` to only stress test the 
  SourceKit Stress Tester CI job.

Values can either be a single string literal or a list of alternative string
literals to match against. For example the below action is expected to fail on
both main and swift-5.1-branch in both 4.0 and 5.1 compatibility modes:

~~~json
...
{
  "action": "BuildXcodeProjectTarget",
  "project": "project.xcodeproj",
  "target": "project",
  "destination": "generic/platform=iOS",
  "configuration": "Release",
  "xfail": {
    "issue": "https://github.com/apple/swift/issues/9999",
    "compatibility": ["4.0", "5.1"],
    "branch": ["main", "swift-5.1-branch"]
  }
}
...
~~~

If an action is failing for different reasons in different configurations, the
value of the action's `"xfail"` entry can also become a list rather than
a single entry. In this case the `"issue"` of the first item that matches will
be reported. In the below example any failure on Linux would be reported as
*SR-7777*, while a failure on other platforms would be reported as *SR-8888*
using a toolchain built from the *master* branch and *SR-9999* using a
toolchain built from *swift-5.1-branch*. If the entries were in the reverse
order, *SR-7777* would only be reported for Linux failures with toolchains built
from a branch other than *main* or *swift-5.1-branch*.

~~~json
...
{
  "action": "BuildXcodeProjectTarget",
  "project": "project.xcodeproj",
  "target": "project",
  "destination": "generic/platform=iOS",
  "configuration": "Release",
  "xfail": [
    {
      "issue": "https://github.com/apple/swift/issues/7777",
      "platform": "Linux"
    },
    {
      "issue": "https://github.com/apple/swift/issues/8888",
      "branch": "main"
    },
    {
      "issue": "https://github.com/apple/swift/issues/9999",
      "branch": "swift-5.1-branch"
    }
  ]
}
...
~~~
