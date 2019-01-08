$(document).ready(function() {

  // fetch the stream
  frame_source = 'https://' + document.domain + ':' + location.port + '/stream';
  iframe = document.getElementById('player');
  iframe.src = frame_source;
  // assign rendered img tag a 100% width to make it resize to fit (hacky)
  var set_resize = window.setInterval(function() {
        iframe.contentDocument.getElementsByTagName('img')[0].style="width:100%";
        if (iframe.contentDocument.getElementsByTagName('img')[0]) {
          clearInterval(set_resize);
          console.log("cleared")
        }
    }, 1000);
  
  //request and render telemetry and then every x seconds
  get_and_render_tlm();
  window.setInterval(function() {
        get_and_render_tlm();
    }, 20000);

  function get_and_render_tlm() {
    $.ajax({
            url: 'https://' + document.domain + ':' + location.port + '/api/tlm',
            dataType: "json",
            timeout: 20000,
        }).then(function(data) {
          //console.log("received REST data");
          render_tlm(data);
        });
  }

  function render_tlm(tlm) {
    for (var key in tlm) {
        // render tlm in matching element
        $('#'+key).text(tlm[key]);
    }
  }

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