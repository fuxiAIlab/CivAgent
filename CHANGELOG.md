# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]


## [0.1.0-rc.1] - 2024-10-22

### Fixes
- Resolved an issue where the config variable was missing deepcopy causing unforeseen problems.
- Fixed a bug in the response model for propose_trade.
- Addressed the Chinese encoding issue in responses.
- Fixed the misalignment issue with the memory file path.
- Removed city-states from the civilizations (civs).
- Increased timeout duration for mq_listener.


## [0.1.0-rc] - 2024-08-20

### Added
- Project initialization
- Update docs and README for the first release.
- Integrated Poetry for package management.
- Use pre-commit for commit management.
- Utilized isort, black, and ruff for code formatting.
