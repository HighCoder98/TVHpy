# TVHpy
Python client for the Tvheadend API

**NOTE: Only tested with Tvheadend version 4.08**

1. Installation
---------------
Installrequired python modules:
```
requests
simplejson
```
For example for Ubuntu install via pip:
`sudo pip install requests simplejson`

2. Configuration
----------------
Edit config.py

```python
API_USER = "<your-username-here>"
API_PASSWORD = "<your-password-here>"
API_ADDRESS = "http://<your-address-here>:9981/"
```

3. Use the code
---------------
Start by importing the ApiCore
```python
from ApiCore import ApiCore
API_CORE = ApiCore()
    for rec in API_CORE.get_finished_recordings():
        print rec["disp_title"]
```
