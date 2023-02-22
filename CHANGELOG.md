# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.9.0] - 2023-02-22
### Added
* use python v3.8
* support multiple selections [PR-41] (thank you [s-clerc]!)

### Changed
* update parinfer.py to v3.12.0 (thank you [oconnor0]!)
* use EventListener for undo instead of keybinding ([oconnor0])
* use Sublime API to detect comment character ([oconnor0])
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
[Issue #19]:https://github.com/oakmac/sublime-text-parinfer/issues/19
[Issue #20]:https://github.com/oakmac/sublime-text-parinfer/issues/20
[Issue #25]:https://github.com/oakmac/sublime-text-parinfer/issues/25
[Issue #28]:https://github.com/oakmac/sublime-text-parinfer/issues/28
[PR-37]:https://github.com/oakmac/sublime-text-parinfer/pull/37
[PR-41]:https://github.com/oakmac/sublime-text-parinfer/pull/41

[Unreleased]: https://github.com/oakmac/sublime-text-parinfer/compare/v0.9.0...HEAD
[0.9.0]: https://github.com/oakmac/sublime-text-parinfer/releases/tag/v0.9.0
[0.8.1]: https://github.com/oakmac/sublime-text-parinfer/releases/tag/v0.8.1
[0.8.0]: https://github.com/oakmac/sublime-text-parinfer/releases/tag/v0.8.0
[0.7.0]: https://github.com/oakmac/sublime-text-parinfer/releases/tag/v0.7.0
[0.6.0]: https://github.com/oakmac/sublime-text-parinfer/releases/tag/v0.6.0
[0.5.0]: https://github.com/oakmac/sublime-text-parinfer/releases/tag/v0.5.0
[0.4.0]: https://github.com/oakmac/sublime-text-parinfer/releases/tag/v0.4.0
[0.3.0]: https://github.com/oakmac/sublime-text-parinfer/releases/tag/v0.3.0
[0.2.0]: https://github.com/oakmac/sublime-text-parinfer/releases/tag/v0.2.0
