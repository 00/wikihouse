
# Todo

* edit and delete design, inc:
  - RESTful `Design` handler
  - save metadata vs save and overwrite model (n.b.: will require moderation)
  - direct edit through the browser with blob store routed file inputs for admin (i.e.: to brute override files, n.b.: means fixing ZZ country code via internal redirect issue)
  - in handler, only overwrite files if provided (either it will be all from sketchup, or just a specific file from the browser)
  - on edit if files have changed and not an admin, set status to 'pending' and trigger moderation
  - for delete
    - add 'deleted' status
    - set to deleted via confirmation
  

