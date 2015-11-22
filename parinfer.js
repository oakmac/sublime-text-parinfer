// This file is part of the Parinfer Sublime Text plugin:
// https://github.com/oakmac/sublime-text-parinfer

// Released under the ISC License:
// https://github.com/oakmac/sublime-text-parinfer/blob/master/LICENSE.md

var net = require('net'),
    fs = require('fs'),
    parinfer = require('./parinfer-lib.js');

const socketFile = '/tmp/sublime-text-parinfer.sock';

// remove the socket file if it exists
try {
  fs.unlinkSync(socketFile);
} catch(e) {
  // no-op
}

// the socket connection
var conn = null;

// start the server and wait for Python to connect
var server = net.createServer(function(newConn) {
  console.log('Python is connected');
  conn = newConn;
  conn.on('data', receiveDataFromPython);
  conn.on('end', shutItDown);
});
server.listen(socketFile, function() {
  console.log('Waiting for Python to connect...');
});

function receiveDataFromPython(rawData) {
  // DEBUG:
  //console.log(rawData.toString());

  // TODO: wrap this parse in a try/catch
  var data = JSON.parse(rawData.toString());

  // run parinfer on the text
  var result = parinfer.indentMode(data.text, {
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

// client has disconnected; shut it down!
function shutItDown() {
  process.exit();
}
