      var socket = io.connect('http://' + document.domain + ':' + location.port, { query: 'tbl='+location.pathname });

      socket.on( 'connect', function() {
                
            $("#sit_stand2").hide();
            $("#main_user_panel").hide();
          
            var form = $( 'form' ).on( 'submit', function( e ) {
              e.preventDefault()
              let user_name = $( 'input.username' ).val()
              let tb_id = $( "h3#tblURI" ).get(0)
              socket.emit( 'join', {
                urname : user_name,
                tabId : $('#tblURI').html()
              } )
            } )              
        } )

        $("#sit_stand2").on('click', function( ) {
             $("#sit_stand2").hide();
            alert("The paragraph was clicked.");
            $( 'div.userinfo' ).html('');
            $("div.formholder").show(); 
            socket.emit('sit stand', {user_name : 'User'})
        });

      $("#tablestate").on('change',  function( ) {
              let tbl_state = $( "#tablestate" ).val();
              alert(tbl_state);
            socket.emit('start pause', {
                message: tbl_state,
                tbl: $('#tblURI').html()
              })
            });

       socket.on( 'get card resp', function( msg ) {
        console.log( msg )
        if( typeof msg.user_name !== 'undefined' ) {
          $( 'h3' ).remove()
          $( 'div.message_holder' ).append( '<div><b style="color: #000">'+msg.user_name+'</b> '+msg.tableId+'</div>' )
        }
      })

        socket.on('output', function(msg){
            $( 'div.message_holder' ).append( '<div><b style="color:white">'+msg+'</b> ')
          });

        socket.on('output_alert', function(msg){
            alert(msg);
          });

        socket.on('online', function(msg){
        //    $( 'div.message_holder' ).append( '<div><b style="color: #000">'+msg )
            $('div.msg_innr').html($('<span/>', {text: msg}))
            $("#main_user_panel").show();
          });

        socket.on('seat_user', function(msg){
          $("div.formholder").hide();  
          $( 'div.userinfo' ).html(
            '<br /><b style="color:white;font-size: 20px;">'+msg+
            ' you are seated<br /><br />'
          )
            $("#sit_stand2").show();
          });
     
       socket.on('table_state', function(msg){
            $('div.msg_innr').html(
                $('<span/>', {text: 'Some text'+msg.val1})
                )
            $('#bone').html(msg.box1)
            $('#btwo').html(msg.box2) 
            $('#bfour').html(msg.box4)
           $('#bfive').html(msg.box5)
           $('#bsix').html(msg.box6)
           $('#bseven').html(msg.box7)
           $('#beight').html(msg.box8)
          });


          