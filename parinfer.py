### Sublime Text plugin for Parinfer
### More information about Parinfer can be found here:
### http://shaunlebron.github.io/parinfer/

### This plugin is open source under the ISC License.
### https://github.com/oakmac/sublime-text-parinfer

import sublime, sublime_plugin
import functools
import socket
import os, os.path
import json

# constants
socket_file = '/tmp/sublime-text-parinfer.sock'
debounce_interval_ms = 50

# TODO: start the node.js process in a background thread

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
        self.socket.connect(socket_file)

    # actually run Parinfer on the file
    def run_parinfer(self, view):
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
        data = {'mode': 'indent',
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
        sublime.set_timeout(functools.partial(self.handle_timeout, view), debounce_interval_ms)
