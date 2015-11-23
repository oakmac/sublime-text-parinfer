# Parinfer for Sublime Text [WORK IN PROGRESS]

A [Parinfer] package for [Sublime Text].

## Status

This project is still heavily a work in progress, but indent mode should be
usable for most folks if you have Node.js installed at `/usr/bin/node`

More to come soon :)

I am working on the following steps:

* [x] Connect to the Sublime Text API when the text buffer is modified
* [x] Bi-directional communication between Python and the node.js process
* [x] Start a long-running node.js process from Python
* [ ] Only enable for certain file extensions (Issue #6)
* [ ] Simple config file for editing file extensions (Issue #6)
* [ ] Set up [Package Control] (Issue #4)
* [ ] Enable Paren Mode
* [x] Hotkeys to toggle between Indent and Paren mode

## License

[ISC License]

[Parinfer]:http://shaunlebron.github.io/parinfer/
[Sublime Text]:http://www.sublimetext.com/
[Package Control]:https://packagecontrol.io/
[ISC License]:LICENSE.md
