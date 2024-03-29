# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [1.2.0] - 2023-09-07
### Fixed
* Prevent runtime error when unable to get language syntax setting [Issue #47]

## [1.1.0] - 2023-03-14
### Fixed
* Remove debug logging [Issue #45] (thank you [oconnor0])

## [1.0.0] - 2023-02-23
### Added
* add command "Parinfer: Run Paren Mode on Current Buffer"
* add config flag `run_paren_mode_when_file_opened`

### Changed
* do not run Paren Mode on the full file when it is first opened
* drop the user into "Waiting" mode when a file is opened where Parinfer should be enabled
* enable Indent Mode after the first buffer modification
* reduce the range that Parinfer looks for parent expressions (with the goal of minimizing changes to longer files)

### Fixed
* added some defensive code to prevent an occasional runtime error
* fix some [pylint] errors

## [0.9.0] - 2023-02-22
### Added
* use python v3.8
* support multiple selections [PR-41] (thank you [s-clerc]!)

### Changed
* update parinfer.py to v3.12.0 [PR-39] (thank you [oconnor0]!)
* use EventListener for undo instead of keybinding ([oconnor0])
* use Sublime API to detect comment character [PR-40] ([oconnor0])
* Run paren mode on opening file via view.run_command ([oconnor0])

## [0.8.1] - 2019-10-03
### Added
* Add dynamic comment character [PR-37] (thank you [sepisoad]!)

## [0.8.0] - 2016-02-12
### Changed
* Drop support for <kbd>Ctrl</kbd> hotkeys on Mac

## [0.7.0] - 2016-02-12
### Added
* Use <kbd>Cmd</kbd> hotkeys on Mac (thank you [Shaun LeBron]!)

## [0.6.0] - 2016-02-11
### Fixed
* Fix a bug with the parent expression hack [Issue #19]
* Fix "undo" [Issue #20]
* Do not break selection [Issue #25] and [Issue #28]

## [0.5.0] - 2016-02-03
### Changed
* Update to [parinfer.py] v0.7.0

## [0.4.0] - 2016-01-16
### Changed
* Update to [parinfer.py] v0.5.0

## [0.3.0] - 2015-12-29
### Changed
* Add support for Windows and Sublime Text 3 (thank you [Joakim Löfgren]!)

## [0.2.0] - 2015-12-27 - First Release
### Added
* Initial release! [Parinfer] now usable from [Sublime Text] :)

[Parinfer]:https://shaunlebron.github.io/parinfer/
[Sublime Text]:http://www.sublimetext.com/
[Joakim Löfgren]:https://github.com/JoakimLofgren
[Shaun LeBron]:https://github.com/shaunlebron
[sepisoad]:https://github.com/sepisoad
[s-clerc]:https://github.com/s-clerc
[oconnor0]:https://github.com/oconnor0

[parinfer.py]:https://github.com/oakmac/parinfer.py
[pylint]:https://pypi.org/project/pylint/
[Issue #19]:https://github.com/oakmac/sublime-text-parinfer/issues/19
[Issue #20]:https://github.com/oakmac/sublime-text-parinfer/issues/20
[Issue #25]:https://github.com/oakmac/sublime-text-parinfer/issues/25
[Issue #28]:https://github.com/oakmac/sublime-text-parinfer/issues/28
[Issue #45]:https://github.com/oakmac/sublime-text-parinfer/issues/45
[Issue #47]:https://github.com/oakmac/sublime-text-parinfer/issues/47
[PR-37]:https://github.com/oakmac/sublime-text-parinfer/pull/37
[PR-39]:https://github.com/oakmac/sublime-text-parinfer/pull/39
[PR-40]:https://github.com/oakmac/sublime-text-parinfer/pull/40
[PR-41]:https://github.com/oakmac/sublime-text-parinfer/pull/41

[Unreleased]: https://github.com/oakmac/sublime-text-parinfer/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/oakmac/sublime-text-parinfer/releases/tag/v1.2.0
[1.1.0]: https://github.com/oakmac/sublime-text-parinfer/releases/tag/v1.1.0
[1.0.0]: https://github.com/oakmac/sublime-text-parinfer/releases/tag/v1.0.0
[0.9.0]: https://github.com/oakmac/sublime-text-parinfer/releases/tag/v0.9.0
[0.8.1]: https://github.com/oakmac/sublime-text-parinfer/releases/tag/v0.8.1
[0.8.0]: https://github.com/oakmac/sublime-text-parinfer/releases/tag/v0.8.0
[0.7.0]: https://github.com/oakmac/sublime-text-parinfer/releases/tag/v0.7.0
[0.6.0]: https://github.com/oakmac/sublime-text-parinfer/releases/tag/v0.6.0
[0.5.0]: https://github.com/oakmac/sublime-text-parinfer/releases/tag/v0.5.0
[0.4.0]: https://github.com/oakmac/sublime-text-parinfer/releases/tag/v0.4.0
[0.3.0]: https://github.com/oakmac/sublime-text-parinfer/releases/tag/v0.3.0
[0.2.0]: https://github.com/oakmac/sublime-text-parinfer/releases/tag/v0.2.0
