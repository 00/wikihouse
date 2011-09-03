# Show hide preview image.  The "algorithm" is predicated on there being
# only two preview images.
$(document).ready ->

  $link = $ '.preview-image-reverse-link a'
  $link.bind 'click', ->

    $images = $ '.model-content .preview-image'

    $visible = $images.filter(':visible')
    $hidden = $images.filter(':hidden')

    $visible.hide()
    $hidden.show()

    false




