window.wikihouse ?= {}

$(document).ready ->
  
  progress = $ '#design-form-progress-indicator'
  message = $ '.message', progress
  form = $ '#submit-design-form'
  
  # Validate the submit design form, show processing state and call sketchup.
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
      
      # If valid, show processing state and call sketchup.
      if valid
        wikihouse.show_progress('Processing SketchUp files ...')
        wikihouse.call_sketchup()
      
      # Either way, make sure we squish the event.
      event.stopImmediatePropagation()
      return false
      
    
  
  
  # XXX Tav, I'm presuming you'll override this and call `wikihouse_do_upload()`
  # when you've finished updating the `file` inputs.
  wikihouse.call_sketchup = ->
    # Fake the input values for now.
    $('#design-model').val 'SSBhbSBhIG1vZGVsLg=='
    $('#design-model-preview').val '_9j_4QAYRXhpZgAASUkqAAgAAAAAAAAAAAAAAP_sABFEdWNreQABAAQAAAAAAAD_4QMraHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLwA8P3hwYWNrZXQgYmVnaW49Iu-7vyIgaWQ9Ilc1TTBNcENlaGlIenJlU3pOVGN6a2M5ZCI_PiA8eDp4bXBtZXRhIHhtbG5zOng9ImFkb2JlOm5zOm1ldGEvIiB4OnhtcHRrPSJBZG9iZSBYTVAgQ29yZSA1LjAtYzA2MCA2MS4xMzQ3NzcsIDIwMTAvMDIvMTItMTc6MzI6MDAgICAgICAgICI-IDxyZGY6UkRGIHhtbG5zOnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyI-IDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiIHhtbG5zOnhtcD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLyIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bXA6Q3JlYXRvclRvb2w9IkFkb2JlIFBob3Rvc2hvcCBDUzUgTWFjaW50b3NoIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOjVBRDhDNjY3QjlDNDExRTA5Q0UzODdEMTc1MTQ5MDVEIiB4bXBNTTpEb2N1bWVudElEPSJ4bXAuZGlkOjVBRDhDNjY4QjlDNDExRTA5Q0UzODdEMTc1MTQ5MDVEIj4gPHhtcE1NOkRlcml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6NUFEOEM2NjVCOUM0MTFFMDlDRTM4N0QxNzUxNDkwNUQiIHN0UmVmOmRvY3VtZW50SUQ9InhtcC5kaWQ6NUFEOEM2NjZCOUM0MTFFMDlDRTM4N0QxNzUxNDkwNUQiLz4gPC9yZGY6RGVzY3JpcHRpb24-IDwvcmRmOlJERj4gPC94OnhtcG1ldGE-IDw_eHBhY2tldCBlbmQ9InIiPz7_7gAOQWRvYmUAZMAAAAAB_9sAhAAbGhopHSlBJiZBQi8vL0JHPz4-P0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHAR0pKTQmND8oKD9HPzU_R0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0f_wAARCAAKAAoDASIAAhEBAxEB_8QASwABAQAAAAAAAAAAAAAAAAAAAAUBAQAAAAAAAAAAAAAAAAAAAAAQAQAAAAAAAAAAAAAAAAAAAAARAQAAAAAAAAAAAAAAAAAAAAD_2gAMAwEAAhEDEQA_AJgAP__Z'
    # Fake an delayed call to `do_upload()`.
    setTimeout ->
        wikihouse.do_upload()
      , 1500
    
    
  
  
  # Show upload state and post the form by ajax, redirect on success / show error.
  wikihouse.do_upload = ->
    # Show upload state.
    wikihouse.show_progress('Uploading ...')
    # Post form by ajax.
    url = form.attr 'action'
    data = form.serialize()
    $.ajax
      type: 'POST'
      url: url
      data: data
      dataType: 'json'
      success: (data) ->
        if data.success?
          # Redirect on success.
          window.location.replace data.success
        else 
          # Show error.
          wikihouse.show_error data.error
      
      error: ->
        # Show error.
        wikihouse.show_error 'Upload failed.  Please try again.'
      
    
  
  
  # Call `wikihouse.show_progress(msg)` to trigger the in-progress state.
  wikihouse.show_progress = (msg) ->
    # Clear any validation error message.
    error = form.find('.error').first()
    error.text ''
    # Show the progress indicator.
    progress.height form.height()
    form.hide()
    message.text msg
    progress.show()
    
  
  
  # Call `wikihouse.show_error(error_string)` to show validation errors.
  wikihouse.show_error = (error_string) ->
    # Hide the progress indicator.
    progress.hide()
    form.show()
    # Display the error message.
    error = form.find('.error').first()
    error.text error_string
    
  
  


