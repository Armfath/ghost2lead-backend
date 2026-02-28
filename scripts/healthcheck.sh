#!/bin/sh
python -c "
import urllib.request
r = urllib.request.urlopen('http://localhost:8000/health')
exit(0 if 200 <= r.status < 300 else 1)
" || exit 1
