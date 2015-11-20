## Sublime Text plugin for Parinfer
## More information about Parinfer can be found here:
## http://shaunlebron.github.io/parinfer/

## This plugin is open source under the ISC License.
## https://github.com/oakmac/sublime-text-parinfer

import sublime, sublime_plugin
import os, functools
from subprocess import PIPE, Popen

proc = None

def start_process():
    cmd = ["/usr/bin/node", "-v"]
    env = os.environ.copy()
    proc = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    lines_iterator = iter(proc.stdout.readline, b"")
    for line in lines_iterator:
        print(line)

debounceIntervalMs = 50

class Parinfer(sublime_plugin.EventListener):

    ## stateful debounce counter
    pending = 0

    ## actually run Parinfer on the file
    def runParinfer(self, view):
        print "oh hai???"
        #start_process()
        #print "???BANANAS"

    ## debounce intermediary
    def handleTimeout(self, view):
        self.pending = self.pending - 1
        if self.pending == 0:
            self.runParinfer(view)

    ## fires everytime the editor is modified; basically calls a debounced runParinfer
    def on_modified(self, view):
        self.pending = self.pending + 1
        sublime.set_timeout(functools.partial(self.handleTimeout, view), debounceIntervalMs)
