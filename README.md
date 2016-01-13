# Parinfer for Sublime Text

A [Parinfer] package for [Sublime Text].

## What is Parinfer?

Parinfer is a text editing mode that can infer Lisp code structure from
indentation (and vice versa). A detailed explanation of Parinfer can be found
[here].

Put simply: the goal of Parinfer is to make it so you never have to think about
"balancing your parens" when writing or editing Lisp code. Just indent your code
as normal and Parinfer will infer the intended paren structure.

## Installation

### Package Control

If you have [Package Control] installed, you can easily install the
[Parinfer](https://packagecontrol.io/packages/Parinfer) package:

1. In Sublime Text, open the Command Palette by typing <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>p</kbd>
   (<kbd>Cmd</kbd>+<kbd>Shift</kbd>+<kbd>p</kbd> on Mac)
2. Type `install` and select `Package Control: Install Package`
3. A text prompt should appear shortly after Package Control loads a list of
   packages from the Internet.
4. Type `parinfer` and press <kbd>Enter</kbd>
5. That's it! Parinfer is now installed.

### Linux / OSX

You can symlink the the parinfer repo to the Sublime Text Packages directory.

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

## Usage

### File Extensions

Once the package has been installed, it will automatically load in the
background when you open Sublime Text and watch for file extensions found in a
config file. The default file extensions are: `.clj` `.cljs` `.cljc` `.lfe`
`.rkt`

You can edit these file extensions by going to Preferences --> Package Settings -->
Parinfer --> Settings - Default

### Opening a File

When a file with a recognized extension is first opened, Parinfer runs [Paren
Mode] on the entire file and one of three things will happen (in order of
likelihood):

* **The file was unchanged.** You will be automatically dropped into Indent
  Mode. This is the most likely scenario once you start using Parinfer
  regularly.
* **Paren Mode changed the file.** The buffer will receive the changes and you
  will be dropped into Indent Mode. This is most likely to happen when you first
  start using Parinfer on an existing file.
* **Paren Mode failed.** This is almost certainly caused by having unbalanced
  parens in your file (ie: it will not compile). The text will not be changed
  and you will be dropped into Paren Mode in order to fix the problem.

Running Paren Mode is a necessary first step before Indent Mode can be safely
turned on. See [Fixing existing files] for more information.

Please be aware that - depending on the indentation and formatting in your Lisp
files - this initial processing may result in a large diff the first time it
happens. Once you start using Indent Mode regularly, this initial processing is
unlikely to result in a large diff (or any diff at all). You may even discover
that applying Paren Mode to a file can result in [catching very hard-to-find
bugs] in your existing code! As usual, developers are responsible for reviewing
their diffs before a code commit :)

### Hotkeys and Status Bar

Use hotkey <kbd>Ctrl</kbd>+<kbd>(</kbd> to turn Parinfer on and to toggle
between Indent Mode and Paren Mode.

Use hotkey <kbd>Ctrl</kbd>+<kbd>)</kbd> to disable Pariner.

The status bar will indicate which mode you are in or show nothing if Parinfer
is turned off.

### Future Features

More options and configuration settings are planned for future releases. Browse
the [issues] for an idea of future features. Create a new issue if you can think
of a useful feature :)

## Known Limitations

This extension uses a hack for performance reasons that may act oddly in certain
circumstances. It assumes that an open paren followed by an alpha character -
ie: regex `^\([a-zA-Z]` - at the start of a line is the beginning of a new
"parent expression" and tells the Parinfer algorithm to start analyzing from
there until the next line that matches the same regex. Most of the time this is
probably a correct assumption, but might break inside multi-line strings or
other non-standard circumstances. This is tracked at [Issue #23]; please add to
that if you experience problems.

Please take note: this is a new extension and Parinfer itself is very new.
Please report bugs and feature requests in the [issues].

## License

[ISC license]

[here]:http://shaunlebron.github.io/parinfer/
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
[catching very hard-to-find bugs]:https://github.com/oakmac/atom-parinfer/commit/d4b49ec2636fd0530f3f2fbca9924db6c97d3a8f
[ISC License]:LICENSE.md
