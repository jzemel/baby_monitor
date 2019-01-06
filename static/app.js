$(document).ready(function() {

    // fetch the stream
    frame_source = 'https://' + document.domain + ':' + location.port + '/stream';
    document.getElementById('player').src = frame_source;

    var d = new Date();
    $.ajax({
        url: 'https://' + document.domain + ':' + location.port + '/api/tlm',
        dataType: "json",
        timeout: 20000,
    }).then(function(data) {
        console.log("received REST data");
       $('#signal').text(data['signal']);
       $('#cpu').text(data['cpu']);
       $('#mem').text(data['mem']);
       $('#fps').text(data['fps']);
       $('#disk').text(data['disk']);
       $('#time').text(data['time']);
    });

    // request tlm
      window.setInterval(function() {
        
        $.ajax({
            url: 'https://' + document.domain + ':' + location.port + '/api/tlm',
            dataType: "json",
            timeout: 20000,
        }).then(function(data) {
            console.log("received REST data");
           $('#signal').text(data['signal']);
           $('#cpu').text(data['cpu']);
           $('#mem').text(data['mem']);
           $('#fps').text(data['fps']);
           $('#disk').text(data['disk']);
           $('#time').text(data['time']);
        });
        console.log("sent tlm GET request")
    }, 20000);


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