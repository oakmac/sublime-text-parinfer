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
SOCKET_FILE = ("127.0.0.1", 6660) #os.path.join(os.path.expanduser('~'), '.sublime-text-parinfer.sock')
DEBOUNCE_INTERVAL_MS = 50
PING_INTERVAL_MS = 20 * 1000
CONNECTION_RETRY_INTERVAL_MS = 100
STATUS_KEY = 'parinfer'
PAREN_STATUS = 'Parinfer: Paren'
INDENT_STATUS = 'Parinfer: Indent'
PLUGIN_PATH = os.path.join(sublime.packages_path(), "sublime-text-parinfer")
DEFAULT_CONFIG_FILE = os.path.join(PLUGIN_PATH, 'default-config.json')
CONFIG_FILE = os.path.join(PLUGIN_PATH, 'config.json')


# create the config file from the default if it is not there
if not os.path.isfile(CONFIG_FILE):
    shutil.copy(DEFAULT_CONFIG_FILE, CONFIG_FILE)

# load the config
with open(CONFIG_FILE) as config_json:
    CONFIG = json.load(config_json)

# TODO: show them an error if their nodejs path is wrong

# start the node.js process
subprocess.Popen([CONFIG['nodejs_path'], "parinfer.js"], cwd=PLUGIN_PATH)

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

        # holds our connection to the node.js server
        self.nodejs_socket = None

        # connected flag
        self.connected_to_nodejs = False

        # stateful - holds our last update
        self.last_update_text = None

        # kick off the initial connection to nodejs
        self.connect_to_nodejs()

    # NOTE: recursive function; will keep trying every CONNECTION_RETRY_INTERVAL_MS
    #       until it succeeds
    def connect_to_nodejs(self):
        self.nodejs_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # try to connect to node.js
            self.nodejs_socket.connect(SOCKET_FILE)

            # start the pings on successful connection
            sublime.set_timeout(self.ping_nodejs, PING_INTERVAL_MS)

            # toggle connected flag
            self.connected_to_nodejs = True

        except socket.error as msg:
            print(msg)
            # If at first you don't succeed, Try, try, try again.
            sublime.set_timeout(self.connect_to_nodejs, CONNECTION_RETRY_INTERVAL_MS)
 
    # ping the node.js server every PING_INTERVAL_MS to prevent it from shutting down
    def ping_nodejs(self):
        self.nodejs_socket.sendall("PING".encode('utf-8'))
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
        self.nodejs_socket.sendall(data_string.encode('utf-8'))

        # wait for the node response
        result_json = self.nodejs_socket.recv(4096).decode('utf-8')
        
        result = json.loads(result_json)
        print(result)
        if (result['isValid'] == True):
            view.run_command("parinfer_edit_view", {"result": result})

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

        print("TODO: start Parinfer here")

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

class ParinferEditViewCommand(sublime_plugin.TextCommand):
    def run(self, edit, result):
        oldsel = []
        for region in self.view.sel(): oldsel.append(region)

        # update the buffer
        self.view.replace(edit, sublime.Region(0, self.view.size()), result['text'])

        self.view.sel().clear()
        for region in oldsel: self.view.sel().add(region)

