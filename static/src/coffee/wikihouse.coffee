window.wikihouse ?= {}

$(document).ready ->
  
  progress = $ '#design-form-progress-indicator'
  form = $ '#submit-design-form'
  
  # Validate the submit design form.
  form.bind 'submit', (event) ->
      
      data = $.parseQuery form.serialize()
      valid = true
      
      # Title is required.
      error = $('#design-title').closest('.field').find('.error')
      if not data.title
        error.text 'You must provide a title'
        valid = false
      else
        error.text ''
      
      # Description is required.
      error = $('#design-description').closest('.field').find('.error')
      if not data.description
        error.text 'You must provide a description.'
        valid = false
      else
        error.text ''
      
      # Must select at least one series.
      error = $('#design-series').closest('.field').find('.error')
      if not data.series or data.series.length is 0
        error.text 'You must select at least one series.'
        valid = false
      else
        error.text ''
      
      # Stop the event if not valid.
      if not valid
        event.stopImmediatePropagation()
        return false
      
    
  
  
  # Call `wikihouse.show_progress()` to trigger the in-progress state.
  wikihouse.show_progress = ->
    # Clear any validation error message.
    error = form.find('.error').first()
    error.text ''
    # Show the progress indicator.
    progress.height form.height()
    form.hide()
    progress.show()
    
  
  
  # Call `wikihouse.show_error(error_string)` to show validation errors.
  wikihouse.show_error = (error_string) ->
    # Hide the progress indicator.
    progress.hide()
    form.show()
    # Display the error message.
    error = form.find('.error').first()
    error.text error_string
    
  
  


