import re
with open(main.py, r) as f:
    content = f.read()
content = content.replace(WHERE hour >= NOW() - INTERVAL "24 hours", WHERE hour >= NOW() - INTERVAL "%s hours" % hours)
with open(main.py, w) as f:
    f.write(content)
print(Fixed)
