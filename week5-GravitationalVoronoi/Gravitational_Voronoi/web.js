var http = require('http');
var fs = require('fs');
net = require('net');

var webserver = http.createServer(function (request, response)
{
  fs.readFile('index.html', 'utf-8', function (error, data)
  {
    response.writeHead(200, {'Content-Type': 'text/html'})
    response.end(data);
  });
}).listen(10000);

var io = require('socket.io')(webserver);

// ----------------------------------------------------------------------------

const dgram = require('dgram');
const server = dgram.createSocket('udp4');
const StringDecoder = require('string_decoder').StringDecoder;
const decoder = new StringDecoder('utf8');

server.bind(8080, '');

server.on('error', function(err){
  console.log('server error:\n${err.stack}');
  server.close();
});

let buffer;

server.on('message', function(msg, rinfo){

  msg = decoder.write(msg);
  if (msg === 'reset') {
    io.sockets.emit('reset', '')
  } else if (msg === 'start') {
    buffer = '';
  } else if (msg === 'end') {
    io.sockets.emit('to_client', buffer);
  } else {
    buffer += msg;
  }
});

server.on('listening', function(){
  var address = server.address();
  console.log('server listening');
});
