from main import *

while True:
    text = input("piinappl->>> ")
    result, error = run(text)
    
    if error: print(error.as_string())
    elif result: print(result)