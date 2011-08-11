# Public Domain (-) 2011 The WikiHouse Authors.
# See the WikiHouse UNLICENSE file for details.

window.wikihouse ?= {}

window.wikihouse.init = (id) ->

  # Exit early if it's not the same SketchUp WebDialog.
  if id is not SKETCHUP_SESSION_ID
    return

  # Setup the controls and methods for the upload page.
  if WIKIHOUSE_UPLOAD_PAGE?

    $progress = $ '#progress-indicator'
    $message = $ '.message', $progress
    $form = $ '#submit-design-form'

    # Validate the submit design form, show processing state and call sketchup.
    $form.bind 'submit', (event) ->

      data = $.parseQuery $form.serialize()
      valid = true

      # Title is required.
      $error = $('#design-title').closest('.field').find('.error')
      if not data.title
        $error.text 'You must provide a title'
        valid = false
      else
        $error.text ''

      # Description is required.
      $error = $('#design-description').closest('.field').find('.error')
      if not data.description
        $error.text 'You must provide a description.'
        valid = false
      else
        $error.text ''

      # Must select at least one series.
      $error = $('#design-series').closest('.field').find('.error')
      if not data.series or data.series.length is 0
        $error.text 'You must select at least one series.'
        valid = false
      else
        $error.text ''

      # If valid, show processing state and call SketchUp.
      if valid
        wikihouse.showProgress 'Processing SketchUp files ...'
        window.location = 'skp:process'

      # Either way, make sure we squish the event.
      event.stopImmediatePropagation()
      return false

    # Show upload state and post the form by ajax, redirect on success / show error.
    wikihouse.upload = ->
      # Show upload state.
      wikihouse.showProgress 'Uploading ...'
      # Post form by ajax.
      url = $form.attr 'action'
      data = $form.serialize()
      $.ajax
        type: 'POST'
        url: url
        data: data
        dataType: 'json'
        success: (data) ->
          if data.success?
            # Redirect on success.
            window.location = 'skp:uploaded@success'
            setTimeout ->
              window.location.replace data.success,
              1500
          else
            # Show error.
            window.location = 'skp:uploaded@error'
            wikihouse.showError data.error
        error: ->
          # Show error.
          window.location = 'skp:uploaded@error'
          wikihouse.showError 'Upload failed. Please try again.'

    # Call `wikihouse.showProgress(msg)` to trigger the in-progress state.
    wikihouse.showProgress = (msg) ->
      # Clear any validation error message.
      $form.find('.error').text ''
      # Show the progress indicator.
      $progress.height $form.height()
      $form.hide()
      $message.text msg
      $progress.show()

    # Call `wikihouse.showError(errmsg)` to show validation errors.
    wikihouse.showError = (errmsg) ->
      # Hide the progress indicator.
      $progress.hide()
      $form.show()
      # Display the error message.
      $error = $form.find('.error').first()
      $error.text errmsg

    # Inform SketchUp to preload input variables.
    window.location = 'skp:load'

  # Setup the controls and methods for a download page.
  if WIKIHOUSE_DOWNLOAD_PAGE?

    $progress = $ '#progress-indicator'
    $message = $ '.message', $progress

    $download = $ '#design-download'
    if !$download.get(0)
      return

    # Get the design's title and download urls.
    designTitle = $('#design-title').text()
    designURL = $download.attr 'href'
    designBase64 = $('#design-download-base64').attr 'href'
    isComponent = $download.attr 'rel'

    # Strip the filename from the URL.
    designURL = designURL.split "/"
    designURL = designURL.slice(0, designURL.legnth-1)
    designURL = designURL.join "/"

    wikihouse.download = (id, url) ->
      # Grab the model data over ajax.
      $.ajax
        type: 'GET'
        url: url
        dataType: 'text'
        success: (data) ->
          # Set the data into the hidden textarea.
          $('#design-download-data').text(data)
          # Inform SketchUp of the available data.
          window.location = "skp:save@#{id}"
        error: ->
          # Inform SketchUp of the failed download.
          window.location = "skp:error@#{id}"

    # Call SketchUp when the download link is clicked.
    $download.click ->
      window.location = "skp:download@#{isComponent},#{designBase64},#{designURL},#{designTitle}"
      return false

$(document).ready ->

  if WIKIHOUSE_UPLOAD_PAGE? or WIKIHOUSE_DOWNLOAD_PAGE?

    # Attempt to generate a unique session id to distinguish potential SketchUp
    # WebDialogs.
    id = "#{(new Date).getTime()}:#{Math.random()}"
    window.SKETCHUP_SESSION_ID = id

    # Create an iframe.
    iframe = document.createElement 'iframe'
    iframe.src = "skp:init@#{id}"
    iframe.style.display = 'none'

    # Append the iframe and thus try and call SketchUp.
    document.body.appendChild iframe
