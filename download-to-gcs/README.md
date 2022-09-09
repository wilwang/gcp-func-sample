# Test the function

```
$ curl  -H "Authorization: bearer $(gcloud auth print-identity-token)" FUNCTION_URL
```

# Debugging on Cloud Shell

Since I used Cloud Shell, I did not use Functions Framework to spin up the local development server. Instead, I created a main_test.py and supplied arguments to the handler function.

```
r = type('',(object,),{"args": { "date": "202205" }})() 
#r = type('',(object,),{"args": {}})() 
http_handler(r)
```