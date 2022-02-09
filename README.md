# 1. Info

This Project is an example implementation of pyusermanager as api and frontend to authenticate users!

## 1.2 Table of Contents

- [1. Info](#1-info)
  - [1.2 Table of Contents](#12-table-of-contents)
- [2. Features](#2-features)
- [3. Misc](#3-misc)
- [4. Requirements](#4-requirements)
  - [4.1 Api](#41-api)
  - [4.2 Frontend](#42-frontend)
- [5. Notes](#5-notes)


# 2. Features

* login
* registration
* permission management
* editing users

# 3. Misc

Feel free to exchange bjoern as webserver! you do that by changing it in base.py in the bottom

```python
app.run(host="0.0.0.0", port=8080, debug=True, server="bjoern")
```

you can also remove the server part to use the reference WSGI Server which should do fine for testing!

# 4. Requirements

## 4.1 Api

* pyusermanager > 2.0.2
* sanic (current release should do)

## 4.2 Frontend

* bottle
* bjoern (as webserver for the frontend)

# 5. Notes

blub