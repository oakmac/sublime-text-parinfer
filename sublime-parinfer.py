# Sublime Text plugin for Parinfer
# v0.3.0
# https://github.com/oakmac/sublime-text-parinfer
#
# More information about Parinfer can be found here:
# http://shaunlebron.github.io/parinfer/
#
# Copyright (c) 2015, Chris Oakman and other contributors
# Released under the ISC license
# https://github.com/oakmac/sublime-text-parinfer/blob/master/LICENSE.md

import sublime
import sublime_plugin
import functools
import re

try:
    # Python 2
    from parinfer import indent_mode, paren_mode
except ImportError:
    from .parinfer import indent_mode, paren_mode

try:
    basestring
except NameError:
    basestring = str

# constants
DEBOUNCE_INTERVAL_MS = 50
STATUS_KEY = 'parinfer'
PAREN_STATUS = 'Parinfer: Paren'
INDENT_STATUS = 'Parinfer: Indent'
PARENT_EXPRESSION_RE = re.compile(r"^\([a-zA-Z]")


def get_setting(view, key):
    settings = view.settings().get('Parinfer')
    if settings is None:
        settings = sublime.load_settings('Parinfer.sublime-settings')
    return settings.get(key)


def is_parent_expression(txt):
    return re.match(PARENT_EXPRESSION_RE, txt) is not None


def find_start_parent_expression(lines, line_no):
    if line_no == 0:
        return line_no

    idx = line_no - 1
    while idx > 0:
        if is_parent_expression(lines[idx]):
            return idx
        idx = idx - 1

    return 0


def find_end_parent_expression(lines, line_no):
    max_idx = len(lines) - 1
    if line_no == max_idx:
        return max_idx

    idx = line_no + 1
    while idx < max_idx:
        if is_parent_expression(lines[idx]):
            return idx
        idx = idx + 1

    return max_idx


class ParinferCommand(sublime_plugin.TextCommand):
    # stateful - holds our last update
    last_update_text = None

    def should_start(self):
        # False if filename is not a string
        filename = self.view.file_name()
        if isinstance(filename, basestring) is not True:
            return False

        # check the extensions in settings
        for extension in get_setting(self.view, 'file_extensions'):
            if filename.endswith(extension):
                return True

        # didn't find anything; do not automatically start Parinfer
        return False

    def run(self, edit):
        if not self.should_start():
            return

        current_status = self.view.get_status(STATUS_KEY)

        # exit if Parinfer is not enabled on this view
        if current_status != INDENT_STATUS and current_status != PAREN_STATUS:
            return

        whole_region = sublime.Region(0, self.view.size())
        all_text = self.view.substr(whole_region)
        lines = all_text.split("\n")
        # add a newline at the end of the file if there is not one
        if lines[-1] != "":
            lines.append("")

        selections = self.view.sel()
        first_cursor = selections[0].begin()
        cursor_row, cursor_col = self.view.rowcol(first_cursor)
        start_line = find_start_parent_expression(lines, cursor_row)
        end_line = find_end_parent_expression(lines, cursor_row)
        start_point = self.view.text_point(start_line, 0)
        end_point = self.view.text_point(end_line, 0)
        region = sublime.Region(start_point, end_point)
        text = self.view.substr(region)
        modified_cursor_row = cursor_row - start_line

        # exit early if there has been no change since our last update
        if text == self.last_update_text:
            return

        options = {'cursorLine': modified_cursor_row, 'cursorX': cursor_col}

        # specify the Parinfer mode
        parinfer_fn = indent_mode
        if current_status == PAREN_STATUS:
            # TODO: add options.cursorDx here
            parinfer_fn = paren_mode

        # run Parinfer on the text
        result = parinfer_fn(text, options)

        if result['success']:
            # update the buffer
            self.view.replace(edit, region, result['text'])

            # update the cursor
            pt = self.view.text_point(cursor_row, cursor_col)
            self.view.sel().clear()
            self.view.sel().add(sublime.Region(pt))

            # save the text of this update so we don't have to process it again
            self.last_update_text = result['text']


class Parinfer(sublime_plugin.EventListener):
    def __init__(self):
        # stateful debounce counter
        self.pending = 0

    # Should we automatically start Parinfer on this file?
    def should_start(self, view):
        # False if filename is not a string
        filename = view.file_name()
        if isinstance(filename, basestring) is not True:
            return False

        # check the extensions in CONFIG
        for extension in get_setting(view, 'file_extensions'):
            if filename.endswith(extension):
                return True

        # didn't find anything; do not automatically start Parinfer
        return False

    # debounce intermediary
    def handle_timeout(self, view):
        self.pending = self.pending - 1
        if self.pending == 0:
            view.run_command('parinfer')

    # fires everytime the editor is modified; basically calls a
    # debounced run_parinfer
    def on_modified(self, view):
        self.pending = self.pending + 1
        sublime.set_timeout(
            functools.partial(self.handle_timeout, view), DEBOUNCE_INTERVAL_MS)

    # fires everytime the cursor is moved
    def on_selection_modified(self, view):
        self.on_modified(view)

    # fires when a file is finished loading
    def on_load(self, view):
        # exit early if we do not recognize this file extension
        if not self.should_start(view):
            return

        # run Paren Mode on the whole file
        whole_region = sublime.Region(0, view.size())
        all_text = view.substr(whole_region)

        result = paren_mode(all_text, None)

        # TODO:
        # - what to do when paren mode fails on a new file?
        #   show them a message?
        # - warn them before applying Paren Mode changes?

        if result['success']:
            # update the buffer if we need to
            if all_text != result['text']:
                e = view.begin_edit()
                view.replace(e, whole_region, result['text'])
                view.end_edit(e)

            # drop them into Indent Mode
            view.set_status(STATUS_KEY, INDENT_STATUS)


class ParinferToggleOnCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # update the status bar
        current_status = self.view.get_status(STATUS_KEY)
        if current_status == INDENT_STATUS:
            self.view.set_status(STATUS_KEY, PAREN_STATUS)
        else:
            self.view.set_status(STATUS_KEY, INDENT_STATUS)


class ParinferToggleOffCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # remove from the status bar
        self.view.erase_status(STATUS_KEY)
