# Provides `_()` translation function that expects `window.message_strings` to be
# a dictionary of translated message strings.
(->
  throw 'Underscore is already defined.' if window._?
  window._ = (msg) ->
    if msg of window.message_strings
      return window.message_strings[msg]
    else
      console.warn "Message not translated: #{msg}" if console? and console.warn?
      return msg
    
  
)()
# Handle the lang-nav by ajax to avoid people sharing urls with the
# `override_language` param in them.
$langlinks = $ '.lang-nav a'
$langlinks.bind 'click', (event) ->
  $target = $ event.target
  $link = $target.closest 'a'
  url = $link.attr 'href'
  $.ajax
    url: url
    success: window.location.reload
  false
  

