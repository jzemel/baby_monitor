$(document).ready(function() {

    // fetch the stream
    frame_source = 'https://' + document.domain + ':' + location.port + '/stream';
    document.getElementById('player').src = frame_source;

    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io.connect('https://' + document.domain + ':' + location.port, {secure: true});
    console.log("socket created");
    console.log('to https://' + document.domain + ':' + location.port)
    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.
    socket.on('connect', function() {
        console.log("connected");
        socket.emit('my_event', {data: 'I\'m connected!'});
        socket.emit('get_tlm');
    });

    // request tlm
      window.setInterval(function() {
        var d = new Date();
        socket.emit('get_tlm',d.getTime());
        console.log("sent tlm request")
    }, 20000);

    // handle tlm input
    socket.on('tlm_json', function(msg) {
        var tlm = JSON.parse(msg);
        console.log("received msg with time" + tlm['timestamp']);
        $('#signal').text(tlm['signal']);
        $('#cpu').text(tlm['cpu']);
        $('#mem').text(tlm['mem']);
        $('#load').text(tlm['load']);
        $('#fps').text(tlm['fps']);
        $('#disk').text(tlm['disk']);
        $('#time').text(tlm['timestamp']);
    });


    $("#stop_btn").click(function() {
        console.log('stopping');
        window.frames[0].stop();
      });

    $("#restart_btn").click(function() {
        console.log("restarting video");
        document.getElementById('player').src = document.getElementById('player').src;
    });

    $("#play_btn").click(function() {
        console.log("restarting video");
        document.getElementById('player').src = document.getElementById('player').src;
    });

});