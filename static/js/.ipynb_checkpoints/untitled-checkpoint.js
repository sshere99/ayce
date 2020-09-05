      var socket = io.connect('http://' + document.domain + ':' + location.port);

      socket.on( 'connect', function() {
        
            socket.emit( 'my event', {
                  data: 'User Connected'
                    } )
        
            var form = $( 'form' ).on( 'submit', function( e ) {
              e.preventDefault()
              let user_name = $( 'input.username' ).val()
              let t_id = $( 'input.tableid' ).val()
              socket.emit( 'join', {
                username : user_name,
                tableId : t_id
              } )
              $( 'input.tableid' ).val( '' ).focus()
            } )

            var but = $('#start_game').on('click', function( e ) {
              e.preventDefault()
              socket.emit('start pause', {
                user_name : 'User',
                message : 'User X Pressed Start'
              })
            })
        } )

      socket.on( 'my response', function( msg ) {
        console.log( msg )
        if( typeof msg.user_name !== 'undefined' ) {
          $( 'h3' ).remove()
          $( 'div.message_holder' ).append( '<div><b style="color: #000">'+msg.user_name+'</b> '+msg.message+'</div>' )
        }
      })

       socket.on( 'get card resp', function( msg ) {
        console.log( msg )
        if( typeof msg.user_name !== 'undefined' ) {
          $( 'h3' ).remove()
          $( 'div.message_holder' ).append( '<div><b style="color: #000">'+msg.user_name+'</b> '+msg.tableId+'</div>' )
        }
      })

        socket.on('output', function(msg){
            $( 'div.message_holder' ).append( '<div><b style="color: #000">'+msg+'</b> '+msg+'</div>' )
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


          