# Debugging the function

Since I used Cloud Shell, I did not use Functions Framework to spin up the local development server. Instead, I created a main_test.py and supplied arguments to the handler function.

```
r = type('',(object,),
    {
        "data": 
        { 
            "bucket": "BUCKET NAME", 
            "name": "202208.zip" 
        }
    })() 
handle_gcs_event(r)
```