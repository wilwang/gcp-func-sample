# Debugging the function

Since I used Cloud Shell, I did not use Functions Framework to spin up the local development server. Instead, I created a main_test.py and supplied arguments to the handler function. Make sure your file already exists in the bucket.

```
r = type('',(object,),
    {
        "data": 
        { 
            "bucket": BUCKET_NAME, 
            "name": FILE_NAME
        }
    })() 
handle_gcs_event(r)    
```