from main import *
import sys

if len(sys.argv) == 1:
    while True:
        text = input("piinappl->>> ")
        if text.strip() == "":
            continue
        result, error = run(text, 'fn')
        
        if error: print(error.as_string())
        # elif result: 
        #     if len(result.value) == 1:
        #         print(repr(result.value[0]))
        #     else:
        #         print(result)
elif len(sys.argv) == 2:
    try:
        with open(sys.argv[1], "r") as f:
            script = f.read()
    except Exception as e:
        raise Exception("Error code 002 - Failed to load script: \"{fn}\"\n" + str(e))
    if not script.strip() == "":
        result, error = run(script, sys.argv[1])
        
        if error: print(error.as_string())
        # elif result: 
        #     if len(result.value) == 1:
        #         print(repr(result.value[0]))
        #     else:
        #         print(result)
else:
    print(f"Error code 001 - Unexpected amount of arguments: {len(sys.argv)}")