from main import *

while True:
    text = input("piinappl->>> ")
    if text.strip() == "":
        continue
    result, error = run(text)
    
    if error: print(error.as_string())
    elif result: 
        if len(result.value) == 1:
            print(repr(result.value[0]))
        else:
            print(result)