# Parinfer for Sublime Text [WORK IN PROGRESS]

A [Parinfer] package for [Sublime Text].

## Status

This project is still a work in progress, but should be usable for the brave.

1. Clone this repo as `Parinfer` into your Sublime Text `Packages` folder.
1. Copy `default-config.json` to `config.json` and edit the `nodejs_path` if necessary.
1. Launch Sublime Text 2 and hope for the best! haha

I am working on the following steps before a first publish to [Package Control]:

* [x] Connect to the Sublime Text API when the text buffer is modified
* [x] Bi-directional communication between Python and the node.js process
* [x] Start a long-running node.js process from Python
* [x] Enable Paren Mode
* [x] Hotkeys to toggle between Indent and Paren mode
* [ ] Only enable for certain file extensions ([Issue #6](https://github.com/oakmac/sublime-text-parinfer/issues/6))
* [ ] Simple config file for editing file extensions ([Issue #6](https://github.com/oakmac/sublime-text-parinfer/issues/6))
* [ ] Improve speed with the "parent expression" hack ([Issue #9](https://github.com/oakmac/sublime-text-parinfer/issues/9))
* [ ] Run Paren Mode when a file is first opened ([Issue #14](https://github.com/oakmac/sublime-text-parinfer/issues/14))
* [ ] Set up [Package Control] ([Issue #4](https://github.com/oakmac/sublime-text-parinfer/issues/4))

## License

[ISC License]

[Parinfer]:http://shaunlebron.github.io/parinfer/
[Sublime Text]:http://www.sublimetext.com/
[Package Control]:https://packagecontrol.io/
[ISC License]:LICENSE.md
