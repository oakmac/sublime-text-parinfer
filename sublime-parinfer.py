# Sublime Text Parinfer
# v0.9.0
# https://github.com/oakmac/sublime-text-parinfer
#
# More information about Parinfer can be found here:
# http://shaunlebron.github.io/parinfer/
#
# Copyright (c) 2015, Chris Oakman and other contributors
# Released under the ISC license
# https://github.com/oakmac/sublime-text-parinfer/blob/master/LICENSE.md

import functools
import re

import sublime
import sublime_plugin

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
SYNTAX_LANGUAGE_RE = r"([\w\d\s]*)(\.sublime-syntax)"

def get_syntax_language(view):
    regex_res = re.search(SYNTAX_LANGUAGE_RE, view.settings().get("syntax"))
    if regex_res:
        return regex_res.group(1)
    return None


# TODO: This is ugly, but I'm not sure how to avoid the ugly iteration lookup on each view.
comment_chars = {}

def get_comment_char(view):
    comment_char = ';'
    srclang = get_syntax_language(view)

    if srclang in comment_chars:
        comment_char = comment_chars[srclang]
    else:
        # Iterate over all shellVariables for the given view.
        # 0 is a position so probably should be the current cursor location,
        # but since we don't nest Clojure in other syntaxes, just use 0.
        for var in view.meta_info("shellVariables", 0):
            if var['name'] == 'TM_COMMENT_START':
                comment_char = var['value'].strip()
                comment_chars[srclang] = comment_char
                break

    return comment_char


def get_setting(view, key):
    settings = view.settings().get('Parinfer')
    if settings is None:
        settings = sublime.load_settings('Parinfer.sublime-settings')
    return settings.get(key)


def is_parent_expression(txt):
    return re.match(PARENT_EXPRESSION_RE, txt) is not None


def find_start_parent_expression(lines, line_no):
    line_no = line_no - 4
    if line_no < 0:
        return 0

    idx = line_no - 1
    while idx > 0:
        if is_parent_expression(lines[idx]):
            return idx
        idx = idx - 1

    return 0


def find_end_parent_expression(lines, line_no):
    max_idx = len(lines) - 1
    line_no = line_no + 4
    if line_no > max_idx:
        return max_idx

    idx = line_no + 1
    while idx < max_idx:
        if is_parent_expression(lines[idx]):
            return idx
        idx = idx + 1

    return max_idx


# this command applies the parinfer changes to the buffer
# NOTE: this needs to be in it's own command so we can override "undo"
class ParinferApplyCommand(sublime_plugin.TextCommand):
    def run(self, edit, start_line = 0, end_line = 0, result_text = ''):
        # get the current selection
        current_selections = [(self.view.rowcol(start), self.view.rowcol(end))
                              for start, end in self.view.sel()]

        # update the buffer
        start_point = self.view.text_point(start_line, 0)
        end_point = self.view.text_point(end_line, 0)
        region = sublime.Region(start_point, end_point)
        self.view.replace(edit, region, result_text)

        # re-apply their selection
        self.view.sel().clear()
        for start, end in current_selections:
            self.view.sel().add(
                sublime.Region(self.view.text_point(*start),
                               self.view.text_point(*end)))


# NOTE: This command inspects the text around the cursor to determine if we need
#       to run Parinfer on it. It does not modify the buffer directly.
class ParinferInspectCommand(sublime_plugin.TextCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # holds the text of the last update
        self.last_update_text = None
        self.comment_char = get_comment_char(self.view)

    def run(self, _edit):
        current_view = self.view
        current_status = current_view.get_status(STATUS_KEY)

        # exit if Parinfer is not enabled on this view
        if current_status not in (INDENT_STATUS, PAREN_STATUS):
            return

        whole_region = sublime.Region(0, current_view.size())
        all_text = current_view.substr(whole_region)
        lines = all_text.split("\n")
        # add a newline at the end of the file if there is not one
        if lines[-1] != "":
            lines.append("")

        selections = current_view.sel()
        first_cursor = selections[0].begin()
        cursor_row, cursor_col = current_view.rowcol(first_cursor)
        start_line = find_start_parent_expression(lines, cursor_row)
        end_line = find_end_parent_expression(lines, cursor_row)
        start_point = current_view.text_point(start_line, 0)
        end_point = current_view.text_point(end_line, 0)
        region = sublime.Region(start_point, end_point)
        text = current_view.substr(region)
        modified_cursor_row = cursor_row - start_line

        # exit early if there has been no change since our last update
        if text == self.last_update_text:
            return

        parinfer_options = {
            'cursorLine': modified_cursor_row,
            'cursorX': cursor_col,
            'commentChar': self.comment_char,
        }

        # specify the Parinfer mode
        parinfer_fn = indent_mode
        if current_status == PAREN_STATUS:
            # TODO: add parinfer_options.cursorDx here
            parinfer_fn = paren_mode

        # run Parinfer on the text
        result = parinfer_fn(text, parinfer_options)

        if result['success']:
            # save the text of this update so we don't have to process it again
            self.last_update_text = result['text']

            # update the buffer in a separate command if the text needs to be changed
            if result['text'] != text:
                cmd_options = {
                    'cursor_row': cursor_row,
                    'cursor_col': cursor_col,
                    'start_line': start_line,
                    'end_line': end_line,
                    'result_text': result['text'],
                }
                sublime.set_timeout(lambda: current_view.run_command('parinfer_apply', cmd_options), 1)


class ParinferParenOnOpen(sublime_plugin.TextCommand):
    def run(self, edit):
        # run Paren Mode on the whole file
        whole_region = sublime.Region(0, self.view.size())
        all_text = self.view.substr(whole_region)
        result = paren_mode(all_text, None)

        # TODO:
        # - what to do when paren mode fails on a new file?
        #   show them a message?
        # - warn them before applying Paren Mode changes?

        if result['success']:
            # update the buffer if we need to
            if all_text != result['text']:
                self.view.replace(edit, whole_region, result['text'])

            # drop them into Indent Mode
            self.view.set_status(STATUS_KEY, INDENT_STATUS)


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

        # check if this is a known file extension
        file_extensions = get_setting(view, 'file_extensions')
        try:
            for extension in file_extensions:
                if filename.endswith(extension):
                    return True
        except:
            None

        # didn't find anything; do not automatically start Parinfer
        return False

    # debounce intermediary
    def handle_timeout(self, view):
        self.pending = self.pending - 1
        if self.pending == 0:
            view.run_command('parinfer_inspect')

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
        view.run_command('parinfer_paren_on_open')


class ParinferToggleOnCommand(sublime_plugin.TextCommand):
    def run(self, _edit):
        # update the status bar
        current_status = self.view.get_status(STATUS_KEY)
        if current_status == INDENT_STATUS:
            self.view.set_status(STATUS_KEY, PAREN_STATUS)
        else:
            self.view.set_status(STATUS_KEY, INDENT_STATUS)


class ParinferToggleOffCommand(sublime_plugin.TextCommand):
    def run(self, _edit):
        # remove from the status bar
        self.view.erase_status(STATUS_KEY)


# override undo
class ParinferUndoListener(sublime_plugin.EventListener):
    def on_text_command(self, view, command_name, _args):
        # TODO: Only run in parinfer views?
        # TODO: Simplify duplicated logic?
        if command_name == 'undo':
            # check to see if the last command was a 'parinfer_apply'
            cmd_history = view.command_history(0)

            # if so, run an extra "undo" to erase the changes
            if cmd_history[0] == 'parinfer_apply':
                view.run_command('undo')

            # run "undo" as normal
        elif command_name == 'redo':
            # check to see if the command after next was a 'parinfer_apply'
            cmd_history = view.command_history(2)

            # if so, run an extra "redo" to erase the changes
            if cmd_history[0] == 'parinfer_apply':
                view.run_command('redo')

            # run "redo" as normal
