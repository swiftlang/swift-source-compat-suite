### Pull Request Description

Replace with a description of this pull request. Instructions for adding
projects are available in the README.

### Acceptance Criteria

To be accepted into the Swift source compatibility test suite, a project must:

- [ ] be an *Xcode* or *swift package manager* project
- [ ] support building on either Linux or macOS
- [ ] target Linux, macOS, or iOS/tvOS/watchOS device
- [ ] be contained in a publicly accessible git repository
- [ ] maintain a project branch that builds against Swift 4.0 and passes any unit tests
- [ ] have maintainers who will commit to resolve issues in a timely manner
- [ ] be compatible with the latest GM/Beta versions of *Xcode* and *swiftpm*
- [ ] add value not already included in the suite
- [ ] be licensed with one of the following permissive licenses:
	* BSD
	* MIT
	* Apache License, version 2.0
	* Eclipse Public License
	* Mozilla Public License (MPL) 1.1
	* MPL 2.0
	* CDDL
- [ ] pass `./project_precommit_check` script run

Ensure project meets all listed requirements before submitting a pull request.
