var net = require('net'),
    fs = require('fs');

//------------------------------------------------------------------------------
// Python --> JS
//------------------------------------------------------------------------------

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
  console.log('Python connected to our server!');
  conn = newConn;
  conn.on('data', receiveDataFromPython);
});
server.listen(socketFile, function() {
  console.log('Waiting for Python to connect...');
});

function receiveDataFromPython(rawData) {
  //console.log('Receiving data from Python:');
  //console.log(data.toString());

  var input = JSON.parse(rawData.toString());

  // TODO: run parinfer on the text
  console.log(input);

  // send the result back to Python
  conn.write('Bananas ' + Math.random());
}
