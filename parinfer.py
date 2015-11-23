## Sublime Text plugin for Parinfer
## https://github.com/oakmac/sublime-text-parinfer

## More information about Parinfer can be found here:
## http://shaunlebron.github.io/parinfer/

## Released under the ISC License:
## https://github.com/oakmac/sublime-text-parinfer/blob/master/LICENSE.md

import sublime, sublime_plugin
import functools
import json
import os, os.path
import socket
import subprocess

# constants
SOCKET_FILE = '/tmp/sublime-text-parinfer.sock'
DEBOUNCE_INTERVAL_MS = 50
STATUS_KEY = 'parinfer'
PAREN_STATUS = 'Parinfer: Paren'
INDENT_STATUS = 'Parinfer: Indent'

# do "which node" to find out where their node path is
# TODO: this won't work on Windows; also need to handle the case where this fails
#       or doesn't find node
which_process = subprocess.Popen(["which", "node"], stdout=subprocess.PIPE)
which_output, which_err = which_process.communicate()
node_path = which_output.strip()

# start the node.js process
subprocess.Popen([node_path, "parinfer.js"])

class Parinfer(sublime_plugin.EventListener):

    # stateful debounce counter
    pending = 0

    # holds our connection to the node.js server
    socket = None
    conn = None

    # stateful - holds our last update
    last_update = None

    # connect to the node.js server
    def connect_to_node(self):
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.connect(SOCKET_FILE)

    # actually run Parinfer on the file
    def run_parinfer(self, view):
        current_status = view.get_status(STATUS_KEY)

        # exit early if Parinfer is not enabled on this view
        if current_status == '':
            return

        whole_region = sublime.Region(0, view.size())
        all_text = view.substr(whole_region)

        # exit early if there has been no change since our last update
        if all_text == self.last_update:
            return

        selections = view.sel()
        first_cursor = selections[0].begin()
        startrow, startcol = view.rowcol(first_cursor)

        # connect to node.js if needed
        if self.socket is None:
            self.connect_to_node()

        # send JSON to node
        mode = 'indent'
        if current_status == PAREN_STATUS:
            mode = 'paren'

        data = {'mode': mode,
                'row': startrow,
                'column': startcol,
                'text': all_text}
        data_string = json.dumps(data)
        self.socket.sendall(data_string)

        # wait for the node response
        result_json = self.socket.recv(4096)
        result = json.loads(result_json)

        ## DEBUG:
        # print "Result from node: ", result['text']

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

        # save this update
        self.last_update = result['text']

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
        # view_id = self.view.id()
        # update the status bar
        current_status = self.view.get_status(STATUS_KEY)
        if current_status == INDENT_STATUS:
            self.view.set_status(STATUS_KEY, PAREN_STATUS)
        else:
            self.view.set_status(STATUS_KEY, INDENT_STATUS)

class ParinferToggleOffCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        #view_id = self.view.id()
        # remove from the status bar
        self.view.erase_status(STATUS_KEY)
