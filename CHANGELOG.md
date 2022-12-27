# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

_Note: 'Unreleased' section below is used for untagged changes that will be issued with the next version bump_

### [Unreleased] - 2022-00-00
#### Added
#### Changed
#### Deprecated
#### Removed
#### Fixed
#### Security
__BEGIN-CHANGELOG__

### [0.2.2] - 2022-12-26
#### Added
 - Currency, account filtering to transaction query methods
 - Option to exclude repayments, currency selection for MvM
#### Fixed
 - File update timestamp wasn't updating on refresh
 - Logic for `is_posted` was invalid, as gnucash uses date `1969-12-31` for an unposted invoice instead of an empty variable
 - Timeseries plot failed when it ran out of pre-determined colors

### [0.2.1] - 2022-12-26
#### Added
 - Version at bottom of base template

### [0.2.0] - 2022-09-04
#### Added
 - Initialized new iteration

__END-CHANGELOG__
