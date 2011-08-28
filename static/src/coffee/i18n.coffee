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
