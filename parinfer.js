// This file is part of the Parinfer Sublime Text plugin:
// https://github.com/oakmac/sublime-text-parinfer

// Released under the ISC License:
// https://github.com/oakmac/sublime-text-parinfer/blob/master/LICENSE.md

var fs = require('fs'),
    net = require('net'),
    os = require('os'),
    path = require('path'),
    parinfer = require('./parinfer-lib.js');

const socketFile = path.join(os.tmpdir(), 'sublime-text-parinfer.sock');

// remove the socket file if it exists
try {
  fs.unlinkSync(socketFile);
} catch(e) {
  // no-op
}

// the socket connection
var conn = null,
    lastConnectionTime = now();

// start the server and wait for Python to connect
var server = net.createServer(function(newConn) {
  console.log('Python is connected');
  conn = newConn;
  conn.on('data', receiveDataFromPython);
  conn.on('end', shutItDown);
});

server.listen(6660, function() {
  console.log('Waiting for Python to connect...');
});

function receiveDataFromPython(rawInput) {
  // convert input to string
  inputStr = rawInput.toString();

  // update the last connection time
  lastConnectionTime = now();

  // do nothing on a ping
  if (inputStr === 'PING') return;

  // TODO: wrap this parse in a try/catch
  var data = JSON.parse(inputStr);

  // pick indentMode or parenMode
  var parinferFn = parinfer.indentMode;
  if (data.mode === 'paren') {
    parinferFn = parinfer.parenMode;
  }

  // run parinfer on the text
  var result = parinferFn(data.text, {
    row: data.row,
    column: data.column
  });
  var returnObj = {isValid: false};

  if (typeof result === 'string') {
    returnObj.isValid = true;
    returnObj.text = result;
  }

  // send the result back to Python
  conn.write(JSON.stringify(returnObj));
}

// goodbye!
function shutItDown() {
  process.exit();
}

function now() {
  return Date.now();
}

// poll every minute to make sure the connection is still live
const oneMinute = 60 * 1000;
setInterval(checkLastUpdate, oneMinute);

function checkLastUpdate() {
  var currentTime = now();

  // shut down if we haven't heard anything from Python in a while
  if (currentTime - lastConnectionTime > oneMinute) {
    shutItDown();
  }
}
