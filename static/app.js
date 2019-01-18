$(document).ready(function() {

  // fetch the stream, params as list
  function fetch_stream(params=[]) {
    //find the div, delete iframe, insert iframe, do setwindowinterval
    var param_string = "?";
    console.log(params);  
    for (i = 0; i < params.length; i++) {
      param_string = param_string + '&' + params[i];
    }
    console.log(param_string)
    frame_source = 'https://' + document.domain + ':' + location.port + '/stream' + param_string;
    $("#player").attr('src', frame_source);
    // assign rendered img tag a 100% width to make it resize to fit (hacky)
    var set_resize = window.setInterval(function() {
          $("#player").contents().find("img").css( "width","100%");
          if ($("#player").contents().find("img").length > 0) {
            if ($("#player").contents().find("img").css('width') == '100%') {
              clearInterval(set_resize);
              console.log("cleared");
            }
          }
      }, 1000);
  }

  fetch_stream();
  
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

  function resize_stream() {
    width = $("#resolution").val();
    rotation = $("#rotation").val();
    params = ['width='+width,'rotation='+rotation];
    window.frames[0].stop();
    fetch_stream(params);
  }

  $("#resolution").change(function() {
    console.log("resolution changed");
    resize_stream();
  });

  $("#rotation").change(function() {
    console.log("rotation changed");
    resize_stream();
  });

});