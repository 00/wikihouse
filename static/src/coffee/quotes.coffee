# Cycle through quotes.
$(document).ready ->
  $widget = $ '.quote-contents'
  $widget.show()
  $widget.cycle
    delay: 3000
    timeout: 7000
    speed: 1000
    after: ->
        $target = $ this
        key = $target.data 'quote-key'
        $li = $ "##{key}-quote-logo"
        $li.addClass 'active'
    
    before: ->
        $lis = $ '.quote-logos li'
        $lis.removeClass 'active'
    

