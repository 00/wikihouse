$(document).ready ->
  
  # Validate the submit design form.
  target = $('#submit-design-form')
  target.bind 'submit', (event) ->
      
      data = $.parseQuery target.serialize()
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
      
    
  
  


