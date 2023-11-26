# README
To use, download the latest release from GitHub, the dependencies should automatically download. If they don't, run this:
```
python -m pip install -r source/dependencies/requirements.txt
```

Then, load the shell by running:
```
$ python source/piinappl.py
```

You can run an external file by running:
```
$ python source/piinappl.py example.appl
```

If you put too many arguments, it will raise this:
```
$ python source/piinappl.py example.appl extra_argument
Error code 001 - Unexpected amount of arguments: 3
```

If the file doesn't exist, it will raise this:
```
$ python source/piinappl.py nonexistent.appl
[Errno 2] No such file or directory: 'nonexistent.appl'
```

If you see an error with a code starting with 4, please report it to the issues tab.
```
[INTERNAL] Error code 401 - No visit method defnied: example
```
