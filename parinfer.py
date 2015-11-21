### Sublime Text plugin for Parinfer
### More information about Parinfer can be found here:
### http://shaunlebron.github.io/parinfer/

### This plugin is open source under the ISC License.
### https://github.com/oakmac/sublime-text-parinfer

import sublime, sublime_plugin
import functools
import socket
import os, os.path
import time

# constants
py_to_js_socket_file = '/tmp/py-to-js.sock'
js_to_py_socket_file = '/tmp/js-to-py.sock'
debounce_interval_ms = 50

class Parinfer(sublime_plugin.EventListener):

    # stateful debounce counter
    pending = 0

    py_to_js_socket = None
    js_to_py_socket = None

    # connect to the node.js server
    def connect_py_js_socket(self):
        self.py_to_js_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.py_to_js_socket.connect(py_to_js_socket_file)

    # start our Python server
    def start_js_py_server(self):
        # remove the JS -> PY socket file if it exists
        if os.path.exists(js_to_py_socket_file):
            os.remove(js_to_py_socket_file)
        self.js_to_py_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.js_to_py_socket.bind(js_to_py_socket_file)
        self.js_to_py_socket.listen(5)

    # actually run Parinfer on the file
    def run_parinfer(self, view):
        whole_region = sublime.Region(0, view.size())
        all_text = view.substr(whole_region)

        # connect to node.js if needed
        if self.py_to_js_socket is None:
            self.connect_py_js_socket()

        # start our server if needed
        if self.py_to_js_socket is None:
            self.connect_py_js_socket()

        # send text to node
        self.py_to_js_socket.send(all_text)

        # TODO: listen for node response

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
