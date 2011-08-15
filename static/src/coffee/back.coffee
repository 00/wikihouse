# Handle back links.
$(document).ready ->
  $('a[rel="back"]').bind 'click', (event) ->
      history.back()
      false
    
  
  
