var net = require('net'),
    fs = require('fs');

//------------------------------------------------------------------------------
// Python --> JS
//------------------------------------------------------------------------------

const pyToJsSocketFile = '/tmp/py-to-js.sock';

// remove the py->js socket file if it exists
try {
  fs.unlinkSync(pyToJsSocketFile);
} catch(e) {
  // no-op
}

// create the py->js server
var pyJsServer = net.createServer(function(client) {
  console.log('Python connected to our socket!');
  client.on('data', receiveDataFromPython);
});
pyJsServer.listen(pyToJsSocketFile, function() {
  console.log('Waiting for Python to connect...');
});

function receiveDataFromPython(data) {
  console.log('Receiving data from Python:');
  console.log(data.toString());
}

//------------------------------------------------------------------------------
// JS --> Python
//------------------------------------------------------------------------------

const jsToPySocketFile = '/tmp/js-to-py.sock',
      retryTimeMs = 100;

// connect to the js->py socket
connectToPython();

var pythonClient = null;

// attempts to connect to the js->py socket
// will keep re-trying every retryTimeMs until it succeeds
function connectToPython() {
  //console.log('Attempting to connect to the Python -> JS socket...');
  pythonClient = net.connect({path: jsToPySocketFile}, jsToPyConnected);
  pythonClient.on('error', jsToPyError);
}

function jsToPyError() {
  //console.log('Could not connect to the JS -> Python Socket. Retrying in 100ms...');
  setTimeout(connectToPython, retryTimeMs);
}

function jsToPyConnected() {
  console.log('Connected to JS -> Python socket!');
  // client.send('bananas!');
}
