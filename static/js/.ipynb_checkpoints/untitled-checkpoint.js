var socket = io.connect('http://' + document.domain + ':' + location.port);

      socket.on( 'connect', function() {
        
            socket.emit( 'my event', {
                  data: 'User Connected'
                    } )
        
            var form = $( 'form' ).on( 'submit', function( e ) {
              e.preventDefault()
              let user_name = $( 'input.username' ).val()
              let user_input = $( 'input.message' ).val()
              socket.emit( 'my event', {
                user_name : user_name,
                message : user_input
              } )
              $( 'input.message' ).val( '' ).focus()
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
          $( 'div.message_holder' ).append( '<div><b style="color: #000">'+msg.user_name+'</b> '+msg.message+'</div>' )
        }
      }) 