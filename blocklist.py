"""
blocklist.py

This file just contains the blocklist of the JWT tokens. It will be imported by
app and the logout resource so that tokens can be added to the blocklist when
the user logs out.
"""

# Ideally we don't want to use this since it won't persist. Would prefer to use readis or a database
BLOCKLIST = set()
