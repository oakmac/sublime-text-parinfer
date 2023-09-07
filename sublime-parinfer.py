"""
Sublime Text Parinfer
v1.2.0
https://github.com/oakmac/sublime-text-parinfer

More information about Parinfer can be found here:
http://shaunlebron.github.io/parinfer/

Copyright (c) 2015, Chris Oakman and other contributors
Released under the ISC license
https://github.com/oakmac/sublime-text-parinfer/blob/master/LICENSE.md
"""

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

# dev flag
DEBUG_LOGGING = False

# constants
DEBOUNCE_INTERVAL_MS = 50
STATUS_KEY = 'parinfer'
PENDING_STATUS = 'Parinfer: Waiting'
INDENT_STATUS = 'Parinfer: Indent'
PAREN_STATUS = 'Parinfer: Paren'
ALL_STATUSES = [PENDING_STATUS, INDENT_STATUS, PAREN_STATUS]
PARENT_EXPRESSION_RE = re.compile(r"^\([a-zA-Z]")
SYNTAX_LANGUAGE_RE = r"([\w\d\s]*)(\.sublime-syntax)"


def debug_log(x):
    if DEBUG_LOGGING == True:
        print("DEBUG:", x)


def get_syntax_language(view):
    try:
        regex_res = re.search(SYNTAX_LANGUAGE_RE, view.settings().get("syntax"))
        return regex_res.group(1)
    except:
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
    idx = line_no - 1
    while idx > 0:
        if is_parent_expression(lines[idx]):
            return idx
        idx = idx - 1
    return 0


def find_end_parent_expression(lines, line_no):
    max_idx = len(lines) - 1
    idx = line_no + 1
    while idx < max_idx:
        if is_parent_expression(lines[idx]):
            return idx
        idx = idx + 1
    return max_idx


class ParinferApplyCommand(sublime_plugin.TextCommand):
    """
    This command applies the Parinfer changes to the buffer.
    NOTE: this needs to be a separate command from other operations so
    we have an accurate history stack for "undo" and "redo"
    """
    def run(self, edit, start_line = 0, end_line = 0, cursor_row = 0, cursor_col = 0, result_text = ''):
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


class ParinferInspectCommand(sublime_plugin.TextCommand):
    """
    This command inspects the text around the cursor to determine if we need
    to run Parinfer on it. It does not modify the buffer directly.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # holds the text of the last update
        self.last_update_text = None
        self.comment_char = get_comment_char(self.view)

    def run(self, _edit):
        current_view = self.view
        current_status = current_view.get_status(STATUS_KEY)

        # exit if Parinfer is not enabled on this view
        if current_status not in ALL_STATUSES:
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


class Parinfer(sublime_plugin.EventListener):
    def __init__(self):
        debug_log('Parinfer plugin init')

        # stateful debounce counter
        self.pending = 0

        self.buffers_with_modifications = {}

    # Should we automatically start Parinfer on this file?
    def should_start(self, view):
        # False if filename is not a string
        filename = view.file_name()
        if isinstance(filename, basestring) is not True:
            return False

        # check if this is a known file extension
        # NOTE: I was occasionally seeing a runtime error here about file_extensions
        # not being an Iterable, so wrapped in try/catch to be defensive.
        # -- C. Oakman, 22 Feb 2023
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

    # fires everytime a buffer receives a modification
    def on_modified(self, view):
        # Flag this buffer as being modified
        buffer_id = view.buffer_id()
        self.buffers_with_modifications[buffer_id] = True

        # flip from "Pending" to "Indent Mode" on the first buffer modification
        if view.get_status(STATUS_KEY) == PENDING_STATUS:
            view.set_status(STATUS_KEY, INDENT_STATUS)

        # run Parinfer
        self.pending = self.pending + 1
        sublime.set_timeout(
            functools.partial(self.handle_timeout, view), DEBOUNCE_INTERVAL_MS)

    # fires everytime a selection changes (ie: the cursor is moved)
    def on_selection_modified(self, view):
        # do nothing if Parinfer is not enabled
        status = view.get_status(STATUS_KEY)
        if status not in ALL_STATUSES:
            return

        # run Parinfer if this is a buffer that has been modified
        buffer_id = view.buffer_id()
        if buffer_id in self.buffers_with_modifications and self.buffers_with_modifications[buffer_id] == True:
            debug_log("selection change, buffer has been modified, run Parinfer")
            self.on_modified(view)
        else:
            debug_log("selection change, buffer has NOT been modified, do nothing")

    # fires when a file is finished loading
    def on_load(self, view):
        if self.should_start(view):
            debug_log("File has been loaded, automatically start Parinfer")

            run_paren_mode_on_open = get_setting(view, "run_paren_mode_when_file_opened")
            if run_paren_mode_on_open == True:
                view.run_command('parinfer_run_paren_current_buffer', { 'drop_into_indent_mode_after': True })
            else:
                # start Waiting mode
                view.set_status(STATUS_KEY, PENDING_STATUS)
        else:
            debug_log("File has been loaded, but do not start Parinfer")

    # called when a view is closed
    def on_close(self, view):
        buffer_id = view.buffer_id()
        clones = view.clones()

        # clear the buffers_with_modifications cache if this is the last view into that Buffer
        if len(clones) == 0 and buffer_id in self.buffers_with_modifications:
            del self.buffers_with_modifications[buffer_id]

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


class ParinferRunParenCurrentBuffer(sublime_plugin.TextCommand):
    """
    Runs paren_mode on the entire current buffer
    """
    def run(self, _edit, drop_into_indent_mode_after = False):
        current_view = self.view
        whole_region = sublime.Region(0, current_view.size())
        all_text = current_view.substr(whole_region)

        lines = all_text.split("\n")
        # add a newline at the end of the file if there is not one
        if lines[-1] != "":
            lines.append("")

        result = paren_mode(all_text, { 'comment': get_comment_char(self.view) })

        if result['success']:
            cmd_options = {
                'start_line': 0, ## first line
                'end_line': len(lines) - 1, ## last line
                'result_text': result['text'],
            }
            ## apply their change to the buffer
            current_view.run_command('parinfer_apply', cmd_options)

            ## optionally drop them into Indent Mode afterward
            if drop_into_indent_mode_after == True:
                current_view.set_status(STATUS_KEY, INDENT_STATUS)

        else:
            ## TODO: it would be nice to show them the line number / character where this failed
            sublime.status_message('Paren mode failed. Do you have unbalanced parens?')


class ParinferUndoListener(sublime_plugin.EventListener):
    """
    Listen for "undo" and "redo" commands. If they occur for Parinfer operations,
    then reverse (or re-apply) accordingly.
    Has no effect for non-Parinfer applied changes.
    """
    def on_text_command(self, view, command_name, _args):
        if command_name == 'undo':
            # check to see if the last command was a 'parinfer_apply'
            cmd_history = view.command_history(0)

            # if so, run an extra "undo" to erase the changes
            if cmd_history[0] == 'parinfer_apply':
                view.run_command('undo')

        elif command_name == 'redo':
            # check to see if the command after next was a 'parinfer_apply'
            cmd_history = view.command_history(2)

            # if so, run an extra "redo" to erase the changes
            if cmd_history[0] == 'parinfer_apply':
                view.run_command('redo')
