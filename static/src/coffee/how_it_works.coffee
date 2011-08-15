# A very simple hardcoded hashchange aware tabview.
$(document).ready ->
  # If we have the relevant markup.
  $container = $ '.how-it-works-container'
  if $container.length
    # Get the tabs and panels.
    $window = $ window
    $document = $ document
    $tabs = $ '.tabs > li', $container
    $panels = $ '.panels > div', $container
    # Flag whether to ignore a hashchange or not.
    click_triggered_hashchange = false
    # Function to select a `slug`, e.g.: `overview`.
    select = (slug) ->
      # Update the tabs.
      $tabs.removeClass 'selected'
      $target_tab = $ ".step-#{slug}"
      $target_tab.addClass 'selected'
      # Update the panels.
      $panels.hide()
      $target_panel = $ "#step-#{slug}"
      $target_panel.show()
      
    
    # Function to select a `hash`, e.g.: `step-overview`.
    select_hash = (hash) ->
      if hash and hash.lastIndexOf '#step-' is 0
        slug = hash.slice 6
        select slug
        return true
      false
      
    
    # Handle tab clicks.
    $tabs.bind 'click', (event) ->
      # Get the slug.
      $target = $ event.target
      $tab = $target.closest 'li'
      if not $tab.hasClass 'selected'
        $link = $tab.find 'a'
        slug = $link.attr 'data-slug'
        # Update the location hash without triggering a hashchange.
        click_triggered_hashchange = true
        window.location.hash = "step-#{slug}"
        # Select the slug.
        select slug
      # Stop the event.
      false
      
    
    # Handle back button.
    $window.bind 'hashchange', ->
      if click_triggered_hashchange
        click_triggered_hashchange = false
      else
        select_hash window.location.hash
      
    
    # Select the first tab.
    if not select_hash window.location.hash
      slug = $tabs.first().find('a').attr 'data-slug'
      select slug
    
  

