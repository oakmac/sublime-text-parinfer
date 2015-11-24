## Sublime Text plugin for Parinfer
## https://github.com/oakmac/sublime-text-parinfer

## More information about Parinfer can be found here:
## http://shaunlebron.github.io/parinfer/

## Released under the ISC License:
## https://github.com/oakmac/sublime-text-parinfer/blob/master/LICENSE.md

import sublime, sublime_plugin
import functools
import json
import os, os.path, shutil
import socket
import subprocess

# constants
SOCKET_FILE = os.path.join(os.path.expanduser('~'), '.sublime-text-parinfer.sock')
DEBOUNCE_INTERVAL_MS = 50
PING_INTERVAL_MS = 20 * 1000
CONNECTION_RETRY_INTERVAL_MS = 100
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

# TODO: show them an error if their nodejs path is wrong

# start the node.js process
subprocess.Popen([CONFIG['nodejs_path'], "parinfer.js"])

class Parinfer(sublime_plugin.EventListener):
    def __init__(self):
        # stateful debounce counter
        self.pending = 0

        # holds our connection to the node.js server
        self.nodejs_socket = None

        self.connected_to_nodejs = False

        # stateful - holds our last update
        self.last_update_text = None

        # kick off the initial connection to nodejs
        self.connect_to_nodejs()

    # connect to the node.js server
    # NOTE: recursive function; will keep trying every CONNECTION_RETRY_INTERVAL_MS
    #       until it succeeds
    def connect_to_nodejs(self):
        self.nodejs_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        try:
            # try to connect to node.js
            self.nodejs_socket.connect(SOCKET_FILE)

            # start the pings on successful connection
            sublime.set_timeout(self.ping_nodejs, PING_INTERVAL_MS)

            self.connected_to_nodejs = True

        except socket.error as msg:
            # If at first you don't succeed, Try, try, try again.
            sublime.set_timeout(self.connect_to_nodejs, CONNECTION_RETRY_INTERVAL_MS)

    def ping_nodejs(self):
        self.nodejs_socket.sendall("PING")
        sublime.set_timeout(self.ping_nodejs, PING_INTERVAL_MS)

    # run Parinfer on the file
    def run_parinfer(self, view):
        # exit early if we are not connected to nodejs
        if self.connected_to_nodejs is not True:
            return

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

        # specify the Parinfer mode
        mode = 'indent'
        if current_status == PAREN_STATUS:
            mode = 'paren'

        # send JSON to node.js
        data = {'mode': mode,
                'row': startrow,
                'column': startcol,
                'text': all_text}
        data_string = json.dumps(data)
        self.nodejs_socket.sendall(data_string)

        # wait for the node response
        result_json = self.nodejs_socket.recv(4096)
        result = json.loads(result_json)

        ## DEBUG:
        # print "JSON response from node.js: ", result_json

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
