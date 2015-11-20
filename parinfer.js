var readline = require('readline');

var rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

rl.setPrompt('Parinfer> ');
rl.prompt();

function close() {
  console.log('Goodbye!');
  process.exit(0);
}

function onLine(l) {
  console.log('~~~~~~~~~~~~~~~ LINE');
}

function onPause() {
  console.log('~~~~~~~~~~~~~~ PAUSE');
}

function onResume() {
  console.log('~~~~~~~~~~~~~~ RESUME');
}

rl.on('line', onLine);
rl.on('pause', onPause);
rl.on('resume', onResume);
