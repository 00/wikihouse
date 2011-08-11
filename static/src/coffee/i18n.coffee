# Provides `_()` translation function that expects `window.message_strings` to be
# a dictionary of translated message strings.
(->
  throw 'Underscore is already defined.' if window._?
  window._ = (msg) ->
    try
      window.message_strings[msg]
    catch err
      console.warn "Message not translated: #{msg}" if console? and console.warn?
      msg
    
  
)()
