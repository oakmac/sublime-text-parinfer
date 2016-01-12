# Parinfer for Sublime Text

A [Parinfer] package for [Sublime Text].

## Installation

These instructions are for Mac and should work with minimal changes on Linux. I
will add instructions for Windows the next time I get a chance to use a Windows
machine. PRs welcome here :)

### Linux / OSX

```
cd ~
git clone git@github.com:oakmac/sublime-text-parinfer.git
ln -s ~/sublime-text-parinfer ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/Parinfer
```

### Windows

```
cd %APPDATA%\Sublime Text 2\Packages
git clone https://github.com/oakmac/sublime-text-parinfer.git Parinfer
```

That's it! This symlinks the parinfer repo to the Sublime Text Package directory.
Sublime Text should automatically detect the folder and activate the plugin.

## Usage

Once the package has been installed, it will automatically load in the
background and watch for file extensions found in a config
file. The default file extensions are: `.clj` `.cljs` `.cljc` `.lfe` `.rkt`

You can change these by open `Preferences>Package Settings>Parinfer>Settings - Default`

When a file is first opened, Parinfer runs [Paren Mode] on the entire file and
then turns on [Indent Mode] if Paren Mode succeeded (ie: the file contained
balanced parens). See [Fixing existing files] for more information on why this
happens.

Please be aware that - depending on the indentation and formatting in your Lisp
files - this initial processing may result in a large diff the first time it
happens. Once you start using Indent Mode regularly, this initial processing is
unlikely to result in a large diff (or any diff at all). You may even discover
that applying Paren Mode to a file can result in [catching very hard-to-find
bugs] in your existing code! As usual, developers are responsible for reviewing
their diffs before a code commit :)

Use hotkey <kbd>Ctrl</kbd>+<kbd>(</kbd> to turn Parinfer on and to toggle
between Indent Mode and Paren Mode.

Use hotkey <kbd>Ctrl</kbd>+<kbd>)</kbd> to disable Pariner.

The status bar will indicate which mode you are in or show nothing if Parinfer
is turned off.

More options and configuration settings are planned for future releases. Browse
the [issues] for an idea of future features. Create a new issue if you can think
of a useful feature :)

## Known Limitations

This extension uses a trick for performance reasons that may act oddly in
certain circumstances. It assumes that an open paren followed by an alpha
character - ie: regex `^\([a-zA-Z]` - at the start of a line is the start of a new
expression and tells the Parinfer algorithm to start analyzing from there until
the next line that matches the same regex. In 99% of cases, this is probably a
correct assumption, but might break inside multi-line strings or other
non-standard circumstances. This is tracked at [Issue #23]; please add to that if you
experience problems.

Please take note: this is a new extension and Parinfer itself is very new.
Please report bugs and feature requests in the [issues].

## License

[ISC license]

[Parinfer]:http://shaunlebron.github.io/parinfer/
[Sublime Text]:http://www.sublimetext.com/
[Package Control]:https://packagecontrol.io/
[Issue #24]:https://github.com/oakmac/sublime-text-parinfer/issues/24
[Issue #4]:https://github.com/oakmac/sublime-text-parinfer/issues/4
[Paren Mode]:http://shaunlebron.github.io/parinfer/#paren-mode
[Indent Mode]:http://shaunlebron.github.io/parinfer/#indent-mode
[Fixing existing files]:http://shaunlebron.github.io/parinfer/#fixing-existing-files
[issues]:https://github.com/oakmac/sublime-text-parinfer/issues
[Issue #23]:https://github.com/oakmac/sublime-text-parinfer/issues/23
[ISC License]:LICENSE.md
[catching very hard-to-find bugs]:https://github.com/oakmac/atom-parinfer/commit/d4b49ec2636fd0530f3f2fbca9924db6c97d3a8f
