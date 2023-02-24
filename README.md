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

You can symlink this repo to the Sublime Text Packages directory:

```sh
cd ~
git clone git@github.com:oakmac/sublime-text-parinfer.git
ln -s ~/sublime-text-parinfer ~/Library/Application\ Support/Sublime\ Text/Packages/Parinfer
```

### Windows

```
cd %APPDATA%\Sublime Text 2\Packages
git clone https://github.com/oakmac/sublime-text-parinfer.git Parinfer
```

## Usage

### File Extensions

Once installed, Parinfer will automatically activate when you open a file with
a [known file extension].

You can change the list of watched file extensions by going to Preferences -->
Package Settings --> Parinfer --> Settings.

[known file extension]:https://github.com/oakmac/sublime-text-parinfer/blob/master/Parinfer.sublime-settings#L2-L9

### Opening a File

When a file with a recognized extension is opened, Parinfer will enter
`Parinfer: Waiting` mode and wait for the **first edit to the buffer**. When
the first edit occurs, Parinfer will enter `Parinfer: Indent` mode and begin
controlling closing parenthesis based on indentation.

### Behavior Change for v1.0.0

Before v1.0.0, when a file was opened Parinfer would run Paren Mode on the
entire file first before entering Indent Mode (see [Fixing existing files]
for more details). This was not a problem for regular users of Parinfer
because running Paren Mode on a file written using Parinfer will not result
in any changes.

However, this behavior was [sometimes confusing] for users new to Parinfer
when they would open a file not written using Parinfer and see edits in
places they did not intend to make.

[sometimes confusing]:https://github.com/oakmac/sublime-text-parinfer/issues/43

Starting with v1.0.0, Parinfer will first enter "Waiting" mode and only begin
controlling closing parens after the first modification to the buffer. If you
desire the pre-v1.0.0 behavior, set the config setting
`run_paren_mode_when_file_opened` to `true`.

Additionally, there is a new `Parinfer: Run Paren Mode on Current Buffer`
command that can be executed at anytime and will run Paren Mode over the
entire active buffer.

### Hotkeys and Status Bar

|  Command              | Windows/Linux                | Mac                         |
|-----------------------|-----------------------------:|-----------------------------|
| Turn on / Toggle Mode | <kbd>Ctrl</kbd>+<kbd>(</kbd> | <kbd>Cmd</kbd>+<kbd>(</kbd> |
| Turn off              | <kbd>Ctrl</kbd>+<kbd>)</kbd> | <kbd>Cmd</kbd>+<kbd>)</kbd> |

The status bar will indicate which mode you are in or show nothing if Parinfer
is turned off.

## The "parent expression" hack

This extension uses a hack for performance reasons that may result in odd
behavior in rare cases. It assumes that an open paren followed by an alpha
character - ie: regex `^\([a-zA-Z]` - at the start of a line is the beginning
of a new "parent expression" and tells the Parinfer algorithm to start
analyzing from there until the next line that matches the same regex. Most of
the time this is probably a correct assumption, but might break inside
multi-line strings or other non-standard circumstances. This is tracked at
[Issue #23]; please add to that if you experience problems.

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
