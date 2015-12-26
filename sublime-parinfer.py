## Sublime Text plugin for Parinfer
## v0.1.0
## https://github.com/oakmac/sublime-text-parinfer
##
## More information about Parinfer can be found here:
## http://shaunlebron.github.io/parinfer/
##
## Copyright (c) 2015, Chris Oakman and other contributors
## Released under the ISC license
## https://github.com/oakmac/sublime-text-parinfer/blob/master/LICENSE.md

import sublime, sublime_plugin
import functools
import json
import os.path, shutil
from parinfer import indent_mode, paren_mode

# constants
DEBOUNCE_INTERVAL_MS = 50
STATUS_KEY = 'parinfer'
PAREN_STATUS = 'Parinfer: Paren'
INDENT_STATUS = 'Parinfer: Indent'
DEFAULT_CONFIG_FILE = './default-config.json'
CONFIG_FILE = './config.json'

# create the config file from the default if it is not there
if not os.path.isfile(CONFIG_FILE):
    shutil.copy(DEFAULT_CONFIG_FILE, CONFIG_FILE)

# load the config
with open(CONFIG_FILE) as config_json:
    CONFIG = json.load(config_json)

# Should we automatically start Parinfer on this file?
def should_start_parinfer(filename):
    # False if filename is not a string
    if isinstance(filename, basestring) is not True:
        return False

    # check the extensions in CONFIG
    for extension in CONFIG['file_extensions']:
        if filename.endswith(extension):
            return True

    # didn't find anything; do not automatically start Parinfer
    return False

class Parinfer(sublime_plugin.EventListener):
    def __init__(self):
        # stateful debounce counter
        self.pending = 0

        # stateful - holds our last update
        self.last_update_text = None

    # run Parinfer on the file
    def run_parinfer(self, view):
        current_status = view.get_status(STATUS_KEY)

        # exit early if Parinfer is not enabled on this view
        if current_status == '':
            return

        whole_region = sublime.Region(0, view.size())
        all_text = view.substr(whole_region)

        # exit early if there has been no change since our last update
        if all_text == self.last_update_text:
            return

        selections = view.sel()
        first_cursor = selections[0].begin()
        startrow, startcol = view.rowcol(first_cursor)
        options = {'cursorLine': startrow, 'cursorX': startcol}

        # specify the Parinfer mode
        mode = 'indent'
        parinfer_fn = indent_mode
        if current_status == PAREN_STATUS:
            # TODO: add options.cursorDx here
            mode = 'paren'
            parinfer_fn = paren_mode

        # run Parinfer on the text
        result = parinfer_fn(all_text, options)

        if result['success']:
            # begin edit
            e = view.begin_edit()

            # update the buffer
            view.replace(e, whole_region, result['text'])

            # update the cursor
            pt = view.text_point(startrow, startcol)
            view.sel().clear()
            view.sel().add(sublime.Region(pt))

            # end edit
            view.end_edit(e)

            # save the text of this update so we don't have to process it again
            self.last_update_text = result['text']

    # debounce intermediary
    def handle_timeout(self, view):
        self.pending = self.pending - 1
        if self.pending == 0:
            self.run_parinfer(view)

    # fires everytime the editor is modified; basically calls a debounced run_parinfer
    def on_modified(self, view):
        self.pending = self.pending + 1
        sublime.set_timeout(functools.partial(self.handle_timeout, view), DEBOUNCE_INTERVAL_MS)

    # fires when a file is finished loading
    def on_load(self, view):
        # exit early if we do not recognize this file extension
        if should_start_parinfer(view.file_name()) is not True:
            return

        print "TODO: start Parinfer here"

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
