$(document).ready ->
  # Submit donate forms when "fund this goal" is clicked.
  $links = $ '.challenge-fund-link a'
  $links.bind 'click dblclick', ->
      form_selector = $(this).data 'target'
      $target = $ form_selector + ' .campaign-submit'
      $target.click()
      false
  # Flag the doc as webkit.
  if $.browser.webkit
      $(document.body).addClass 'webkit'
  if $.browser.msie
      $(document.body).addClass 'msie'
  if $.browser.mozilla
      $(document.body).addClass 'moz'

