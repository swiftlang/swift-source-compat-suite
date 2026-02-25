# Swift Source Compatibility Suite

## Table of Contents

- [Overview](#overview)
- [Why Add Your Project?](#why-add-your-project)
- [Continuous Integration](#continuous-integration)
- [Python Support](#python-support)
- [Platform Support](#platform-support)
- [Adding Projects](#adding-projects)
  - [Acceptance Criteria](#acceptance-criteria)
  - [Adding a Project](#adding-a-project)
- [Maintaining Projects](#maintaining-projects)
- [Building Projects](#building-projects)
  - [macOS](#building-on-macos)
  - [Linux](#building-on-linux)
  - [Windows](#building-on-windows)
- [Marking Actions as Expected Failures](#marking-actions-as-expected-failures)
- [Contributing](#contributing)
  - [Pull Request Testing](#pull-request-testing)

## Overview

Source compatibility is a strong goal for future Swift releases. To aid in this
goal, a community owned source compatibility test suite serves to regression
test changes to the compiler against a (gradually increasing) corpus of Swift
source code. Projects added to this test suite are periodically built against
the latest development versions of Swift as part of Swift's continuous
integration system, allowing Swift compiler developers to
understand the compatibility impact their changes have on real-world Swift
projects.

## Why Add Your Project?

Adding your project to the Swift Source Compatibility Suite allows you to catch source-breaking changes in upcoming Swift releases before they're officially released, giving you time to adapt your codebase. Additionally, your project helps Swift compiler developers understand the real-world impact of their changes, ensuring that the evolution of Swift considers practical use cases from the community.

## Continuous Integration

The Swift Source Compatibility Suite runs as part of Swift's continuous integration infrastructure:

- **macOS and Linux**: [https://ci.swift.org](https://ci.swift.org)
- **Windows**: [https://ci-external.swift.org](https://ci-external.swift.org)

## Python Support

The Source compatibility suite currently supports Python 3.8+. You may experience performance issues if you attempt to execute any of the associated files with a lesser version of Python 3.

## Platform Support

The Swift Source Compatibility Suite supports building projects on:

- **macOS** (Darwin) - Full support including Xcode projects and Swift Package Manager
- **Linux** - Full support for Swift Package Manager projects
- **Windows** - Support for Swift Package Manager projects

Platform-specific features like `xcodebuild` are only available on macOS.

## Adding Projects

The Swift source compatibility test suite is community driven, meaning that open
source Swift project owners are encouraged to submit their projects that meet
the acceptance criteria for inclusion in the test suite. Projects added to the
suite serve as general source compatibility tests and are afforded greater
protection against unintentional source breakage in future Swift releases.

### Acceptance Criteria

To be accepted into the Swift source compatibility test suite, a project must:

1. Target Linux, Windows, macOS, or iOS/tvOS/watchOS device
2. Be an *Xcode* or *Swift Package Manager* project
3. Support building on either Linux, Windows, or macOS
4. Be contained in a publicly accessible git repository
5. Maintain a project branch that builds against all specified compatibility modes
   with recent compilers
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

### Adding a Project

To add a project meeting the acceptance criteria to the suite, perform the
following steps:

1. Ensure the project builds successfully at each chosen commit using the Swift compatibility version you wish to validate (e.g., 4.2, 5.0, 6.0)
2. Create a pull request against the [source compatibility suite
   repository](https://github.com/swiftlang/swift-source-compat-suite),
   modifying **projects.json** to include a reference to the project being added
   to the test suite.

The project index is a JSON file that contains a list of repositories containing
Xcode and/or Swift Package Manager target actions.

#### Swift Package Manager Project Template

To add a new Swift Package Manager project, use the following template:

```json
{
  "repository": "Git",
  "url": "https://github.com/example/project.git",
  "path": "project",
  "branch": "main",
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
```

**Field Descriptions:**

- `repository`: Must be "Git"
- `url`: The HTTPS URL to your Git repository
- `path`: A unique identifier for your project (typically the repo name)
- `branch`: The default branch to track (e.g., "main" or "master")
- `maintainer`: Contact email for the project maintainer
- `compatibility`: List of Swift versions and commits that build successfully
  - `version`: The earliest Swift version compatible with this commit (e.g., "4.2", "5.0", "6.0")
  - `commit`: The 40-character Git SHA that builds with this Swift version
- `platforms`: List of supported platforms: "Darwin", "Linux", or "Windows"
- `actions`: List of build/test actions to perform

**Optional Fields:**

- `build_tests`: When set to `"true"` on a `BuildSwiftPackage` action, the build will also compile test targets (equivalent to `swift build --build-tests`). This is useful for verifying that test code compiles without actually running the tests.

Example with `build_tests`:

```json
{
  "action": "BuildSwiftPackage",
  "build_tests": "true",
  "configuration": "release"
}
```

The `compatibility` field contains a list of version dictionaries, each
containing a Swift version and a commit. Commits are checked out before
building a project in the associated Swift version compatibility mode. The
Swift version is the earliest version of Swift known to compile the project at
the given commit. Ideally, projects should provide multiple compatibility 
entries spanning different Swift versions, allowing the test suite to 
validate that the project builds successfully across various points in its 
development history.

The `platforms` field specifies the platforms that can be used to build the
project. Linux, Darwin, and Windows can currently be specified.

If tests aren't supported, remove the test action entry.

#### Xcode Workspace Template

To add a new Swift Xcode workspace, use the following template:

```json
{
  "repository": "Git",
  "url": "https://github.com/example/project.git",
  "path": "project",
  "branch": "main",
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
```

#### Xcode Project Template

To add a new Swift Xcode project, use the following template:

```json
{
  "repository": "Git",
  "url": "https://github.com/example/project.git",
  "path": "project",
  "branch": "main",
  "maintainer": "email@example.com",
  "compatibility": [
    {
      "version": "6.0",
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
```

## Maintaining Projects

In the event that Swift introduces a change that breaks source compatibility
with a project (e.g., a compiler bug fix that fixes wrong behavior in the
compiler), the Swift team will notify the project maintainer via the email address listed in the project's entry. Project maintainers are expected to update their projects and submit a new pull request with the updated commit hash within two weeks of being
notified. Otherwise, unmaintained projects may be removed from the project
index.

## Building Projects

To build projects locally against a specified Swift compiler, use the
`runner.py` utility.

### Building on macOS

Build all projects:
```bash
./runner.py --swift-branch main --projects projects.json \
  --include-actions 'action.startswith("Build")' \
  --swiftc $(which swiftc)
```

Build a specific project:
```bash
./runner.py --swift-branch main --projects projects.json \
  --include-actions 'action.startswith("Build")' \
  --include-repos 'path == "Alamofire"' \
  --swiftc $(which swiftc)
```

Build with verbose output:
```bash
./runner.py --swift-branch main --projects projects.json \
  --include-actions 'action.startswith("Build")' --verbose \
  --swiftc $(which swiftc)
```

### Building on Linux

Build all projects:
```bash
./runner.py --swift-branch main --projects projects.json \
  --include-actions 'action.startswith("BuildSwiftPackage")' \
  --swiftc $(which swiftc)
```

Build a specific project:
```bash
./runner.py --swift-branch main --projects projects.json \
  --include-actions 'action.startswith("BuildSwiftPackage")' \
  --include-repos 'path == "Alamofire"' \
  --swiftc $(which swiftc)
```

### Building on Windows

Build all projects:
```batch
python runner.py --swift-branch main --projects projects.json ^
  --include-actions "action.startswith('BuildSwiftPackage')" ^
  --swiftc %LOCALAPPDATA%\Programs\Swift\Toolchains\0.0.0+Asserts\usr\bin\swiftc.exe
```

Or using PowerShell:
```powershell
python runner.py --swift-branch main --projects projects.json `
  --include-actions "action.startswith('BuildSwiftPackage')" `
  --swiftc (where.exe swiftc)
```

Build a specific project:
```batch
python runner.py --swift-branch main --projects projects.json ^
  --include-actions "action.startswith('BuildSwiftPackage')" ^
  --include-repos "path == 'SyndiKit'" ^
  --swiftc %LOCALAPPDATA%\Programs\Swift\Toolchains\0.0.0+Asserts\usr\bin\swiftc.exe
```

Or using PowerShell:
```powershell
python runner.py --swift-branch main --projects projects.json `
  --include-actions "action.startswith('BuildSwiftPackage')" `
  --include-repos "path == 'SyndiKit'" `
  --swiftc (where.exe swiftc)
```

**Note:** On Windows, use `where.exe swiftc` in PowerShell to locate the Swift compiler automatically, or specify the full path if Swift is not in your PATH.

By default, build output is redirected to per-action `.log` files in the current
working directory. To change this behavior to output build results to standard
out, use the `--verbose` flag.

## Marking Actions as Expected Failures

When an action is expected to fail for an extended period of time, it's
important to mark the action as an expected failure to make new failures more
visible.

To mark an action as an expected failure, add an `xfail` entry for the correct
Swift version and branch to the failing actions, associating each with a link
to a GitHub issue reporting the relevant failure. The following is an example of
an action that's XFAIL'd when building against Swift main branch in 6.0
compatibility mode.

```json
{
  "repository": "Git",
  "url": "https://github.com/example/project.git",
  "path": "project",
  "branch": "main",
  "maintainer": "email@example.com",
  "compatibility": [
    {
      "version": "6.0",
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
        "issue": "https://github.com/swiftlang/swift/issues/9999",
        "compatibility": "6.0",
        "branch": "main"
      }
    }
  ]
}
```

Additional Swift branches and versions can be added to XFAIL different
configurations. The currently supported fields for XFAIL entries are:

- `"compatibility"`: the Swift version(s) it fails with, e.g. `"4.0"`
- `"branch"`: the branch(es) of the swift compiler it fails with, e.g.
  `"release/6.0"`
- `"platform"`: the platform(s) it fails on, e.g. `"Darwin"` or `"Linux"`
- `"configuration"`: the build configuration(s) if fails with, i.e. `"release"`
  or `"debug"`)
- `"job"`: Allows XFailing the project for only the source compatibility build
  or the SourceKit Stress Tester. Use `"source-compat"` to only XFail the Source
  Compatibility Suite CI job and `"stress-test"` to only stress test the
  SourceKit Stress Tester CI job.

Values can either be a single string literal or a list of alternative string
literals to match against. For example the below action is expected to fail when building with
both main and release/6.0 branches of swift in both 4.0 and 5.1 compatibility modes:

```json
...
{
  "action": "BuildXcodeProjectTarget",
  "project": "project.xcodeproj",
  "target": "project",
  "destination": "generic/platform=iOS",
  "configuration": "Release",
  "xfail": {
    "issue": "https://github.com/swiftlang/swift/issues/9999",
    "compatibility": ["4.0", "5.1"],
    "branch": ["main", "release/6.0"]
  }
}
...
```

If an action is failing for different reasons in different configurations, the
value of the action's `"xfail"` entry can also become a list rather than
a single entry. In this case the `"issue"` of the first item that matches will
be reported. In the below example any failure on Linux would be reported as
*SR-7777*, while a failure on other platforms would be reported as *SR-8888*
using a toolchain built from the *main* branch and *SR-9999* using a
toolchain built from *release/6.0*. If the entries were in the reverse
order, *SR-7777* would only be reported for Linux failures with toolchains built
from a branch other than *main* or *release/6.0*.

```json
...
{
  "action": "BuildXcodeProjectTarget",
  "project": "project.xcodeproj",
  "target": "project",
  "destination": "generic/platform=iOS",
  "configuration": "Release",
  "xfail": [
    {
      "issue": "https://github.com/swiftlang/swift/issues/7777",
      "platform": "Linux"
    },
    {
      "issue": "https://github.com/swiftlang/swift/issues/8888",
      "branch": "main"
    },
    {
      "issue": "https://github.com/swiftlang/swift/issues/9999",
      "branch": "release/6.0"
    }
  ]
}
...
```

## Contributing

Welcome to the Swift community!

Contributions to swift-source-compat-suite are welcomed and encouraged! Please see the [Contributing to Swift guide](https://swift.org/contributing).

To be a truly great community, Swift needs to welcome developers from all walks of life, with different backgrounds, and with a wide range of experience. A diverse and friendly community will have more great ideas, more unique perspectives, and produce more great code. We will work diligently to make the Swift community welcoming to everyone.

To give clarity of what is expected of our members, Swift has adopted the code of conduct defined by the Contributor Covenant. This document is used across many open source communities, and we think it articulates our values well. For more, see the [Code of Conduct](https://www.swift.org/code-of-conduct/).

### Pull Request Testing

**Testing changes to the Swift compiler:**

Pull request testing of Swift compiler changes against the Swift source compatibility suite can be
executed by commenting with `@swift-ci Please test source compatibility` in a
Swift pull request.

**Testing changes to this repository:**

To test changes to the source compatibility suite infrastructure itself (changes to this repository), comment with `@swift-ci test` in your pull request to this repository.
