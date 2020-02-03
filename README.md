# CloudDNNC
Interface layer and examples for the Cloud Deep Neural Network Controller

# Python class for setup and running 

Example should be self explaining. Jupyther Notebook with tutorial is in progress.

# CURL interface doc

Get a random session id first

```
curl --location --request GET 'http://dnncontroller.ddnss.de/newsessionid'
{"sessionid": "da8cafdc-d4ee-48e5-8cde-2199e6b735ca"}
```

Use your session id to send the CloudDNNC your current process value and desired setpoint.

```
curl --location --request GET 'http://dnncontroller.ddnss.de/control?sessionid=da8cafdc-d4ee-48e5-8cde-2199e6b735ca&processvalue=20.5&setpoint=40.0'
{"step": 0, "timediff": 0.02038264274597168, "processingtime": 0.5271427631378174, "setpoint": 40.0, "processvalue": 20.5, "controlvalue": 0.0773794949054718}
```

Apply the given control value to your process or
use your session id to send the CloudDNNC your next process value and desired setpoint, but tell the DNNC that you havn't applied the suggested control value to your process (pause the DNNC)

```
curl --location --request GET 'http://dnncontroller.ddnss.de/control?sessionid=da8cafdc-d4ee-48e5-8cde-2199e6b735ca&processvalue=20.5&setpoint=40.0&controlvalue=0.0'
{"step": 1, "timediff": 173.93308115005493, "processingtime": 0.025597095489501953, "setpoint": 40.0, "processvalue": 20.5, "controlvalue": 0.0773794949054718}
```

You get the same control value because nothing has changed, but the step should be count up.

Delete your session if you are done

```
curl --location --request GET 'http://dnncontroller.ddnss.de/deletesessionid?sessionid=da8cafdc-d4ee-48e5-8cde-2199e6b735ca'
{"ack": "Thx!"}
```
