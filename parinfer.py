### Sublime Text plugin for Parinfer
### More information about Parinfer can be found here:
### http://shaunlebron.github.io/parinfer/

### This plugin is open source under the ISC License.
### https://github.com/oakmac/sublime-text-parinfer

import sublime, sublime_plugin
import functools
import socket
import os, os.path

# constants
socket_file = '/tmp/sublime-text-parinfer.sock'
debounce_interval_ms = 50

# TODO: start the node.js process in a background thread

class Parinfer(sublime_plugin.EventListener):

    # stateful debounce counter
    pending = 0

    socket = None
    conn = None

    # connect to the node.js server
    def connect_to_node(self):
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.connect(socket_file)

    # actually run Parinfer on the file
    def run_parinfer(self, view):
        whole_region = sublime.Region(0, view.size())
        all_text = view.substr(whole_region)

        # connect to node.js if needed
        if self.socket is None:
            self.connect_to_node()

        # send text to node
        self.socket.sendall('{"foo":"bar"}')

        # wait for the node response
        result = self.socket.recv(1024)
        print "Result from node: ", result

        # TODO: update the buffer
        #e = view.begin_edit()
        #view.replace(e, wholeRegion, out)
        #view.end_edit(e)
        #print out

    # debounce intermediary
    def handle_timeout(self, view):
        self.pending = self.pending - 1
        if self.pending == 0:
            self.run_parinfer(view)

    # fires everytime the editor is modified; basically calls a debounced run_parinfer
    def on_modified(self, view):
        self.pending = self.pending + 1
        sublime.set_timeout(functools.partial(self.handle_timeout, view), debounce_interval_ms)
