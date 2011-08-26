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
    $navs_pre = $ '.navs-pre > div', $container
    $navs_next = $ '.navs-next > div', $container
    $descriptions = $ '.descriptions > div', $container
    # Flag whether to ignore a hashchange or not.
    click_triggered_hashchange = false
    # Get the current page hash if exists.
    # Function to select a `slug`, e.g.: `overview`.
    select = (slug, current_slug) ->
      # Update the tabs.
      $tabs.removeClass 'selected'
      $target_tab = $ ".step-#{slug}"
      $target_tab.addClass 'selected'
      # Update the panels.
      # To add effects to the current panel use: $root_panel = $ "#step-#{current_slug}"
      $panels.hide()
      $descriptions.hide()
      $navs_pre.hide()
      $navs_next.hide()
      $target_panel = $ "#step-#{slug}"
      $target_description = $ "#description-#{slug}"
      $target_nav_pre = $ "#nav-pre-#{slug}"
      $target_nav_next = $ "#nav-next-#{slug}"
      $target_panel.fadeIn 1000
      $target_description.show()
      $target_nav_pre.show()
      $target_nav_next.show()
    
    # Function to select a `hash`, e.g.: `step-overview`.
    select_hash = (hash) ->
      if hash and hash.lastIndexOf '#step-' is 0
        slug = hash.slice 6
        select slug
        return true
      false
      
    
    # Handle tab clicks.
    $tabs.bind 'click', (event) ->
      if window.location.hash.length
        current = window.location.hash
        current_slug = current.slice 6
      else
        current_slug = $tabs.first().find('a').attr 'data-slug'
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
        select slug, current_slug
      # Stop the event.
      false
      
    
    # Handle back button.
    $window.bind 'hashchange', ->
      if click_triggered_hashchange
        click_triggered_hashchange = false     
      else
        $panels = $ '.panels > div', $container
        $panels.hide()
        $descriptions = $ '.descriptions > div', $container
        $descriptions.hide()
        $navs_pre = $ '.navs-pre > div', $container
        $navs_pre.hide()
        $navs_next = $ '.navs-next > div', $container
        $navs_next.hide()
        select_hash window.location.hash
      
    
    # Select the first tab.
    if not select_hash window.location.hash
      slug = $tabs.first().find('a').attr 'data-slug'
      select slug
    
  

