import * as io from 'socket.io-client'

var socket = null

/**
 * Connects to the socket on the backend.
 */
function connect () {
  window.io = io
  socket = io.connect('http://' + window.location.hostname + ':5000')
}

export { socket, connect }
