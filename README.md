# TVHpy
Python client for the Tvheadend API

**NOTE: tested with Tvheadend version 4.08 and 4.09**

1. Installation
---------------
Install required python modules:
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
API_IS_SELFSIGNED = <True or False> # True for selfsigned SSL certificate
```

3. Use the code
---------------
```python
import TVHApiClient
for rec in TVHApiClient.get_finished_recordings():
    print rec["disp_title"]
```

For all values of the models see [the wiki](https://github.com/HighCoder98/TVHpy/wiki/Models)
