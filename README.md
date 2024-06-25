## Error Logger API Documentation

This documentation provides a comprehensive guide on how to use the Error Logger API. It is an API that I use personally to send error logs from all of my various servers and projects, store them in a MongoDB database, so that I can use webhooks and other means to get notified when any of my projects run into an error.

### Starting the server
Once you install the `requirements.txt` , you can use this command to start the server.
```
uvicorn src.main:app --reload
```

Local Base URL on Startup:
```
http://127.0.0.1:8000
```

### Authentication

The `POST /log` endpoint requires Basic Authentication. It has the following credentials out of the box:
- **Username**: `admin`
- **Password**: `password`

### Endpoints

#### 1. POST /log
Logs an error to the database.

- **URL**: `/log`
- **Method**: `POST`
- **Authentication**: Basic Authentication
- **Request Body**:
  ```json
  {
      "project_source": "string",
      "timestamp": "ISO 8601 format string",
      "error_message": "string",
      "additional_info": "string"
  }
  ```
- **Response**:
  - **Success** (200 OK):
    ```json
    {
        "status": "success",
        "id": "string"
    }
    ```
  - **Authentication Failure** (401 Unauthorized):
    ```json
    {
        "detail": "Invalid authentication credentials"
    }
    ```

#### 2. GET /logs
Retrieves a list of all error logs.

- **URL**: `/logs`
- **Method**: `GET`
- **Request Parameters**:
  - **skip** (optional, integer): Number of logs to skip.
  - **limit** (optional, integer): Maximum number of logs to return.
- **Response** (200 OK):
  ```json
  [
      {
          "project_source": "string",
          "timestamp": "ISO 8601 format string",
          "error_message": "string",
          "additional_info": "string"
      },
      ...
  ]
  ```

#### 3. GET /current
Retrieves all error logs from the current day (Indian Standard Time).

- **URL**: `/current`
- **Method**: `GET`
- **Response** (200 OK):
  ```json
  [
      {
          "project_source": "string",
          "timestamp": "ISO 8601 format string",
          "error_message": "string",
          "additional_info": "string"
      },
      ...
  ]
  ```

#### 4. GET /analytics
Retrieves a list of all analytics logs.

- **URL**: `/analytics`
- **Method**: `GET`
- **Request Parameters**:
  - **skip** (optional, integer): Number of logs to skip.
  - **limit** (optional, integer): Maximum number of logs to return.
- **Response** (200 OK):
  ```json
  [
      {
          "endpoint": "string",
          "method": "string",
          "ip_address": "string",
          "params": {},
          "response_status": "integer",
          "timestamp": "ISO 8601 format string"
      },
      ...
  ]
  ```

### Examples

#### Python

##### Posting an Error Log
```python
import requests
from requests.auth import HTTPBasicAuth
import datetime

url = "http://127.0.0.1:8000/log"
data = {
    "project_source": "TestProject",
    "timestamp": datetime.datetime.now().isoformat(),
    "error_message": "Sample error message",
    "additional_info": "Additional info"
}

response = requests.post(url, json=data, auth=HTTPBasicAuth('admin', 'password'))
print(response.json())
```

##### Retrieving All Logs
```python
import requests

url = "http://127.0.0.1:8000/logs"
response = requests.get(url)
print(response.json())
```

##### Retrieving Current Day Logs
```python
import requests

url = "http://127.0.0.1:8000/current"
response = requests.get(url)
print(response.json())
```

##### Retrieving Analytics Logs
```python
import requests

url = "http://127.0.0.1:8000/analytics"
response = requests.get(url)
print(response.json())
```

#### JavaScript

##### Posting an Error Log
```javascript
const axios = require('axios');
const moment = require('moment');

const url = 'http://127.0.0.1:8000/log';
const data = {
    project_source: "TestProject",
    timestamp: moment().toISOString(),
    error_message: "Sample error message",
    additional_info: "Additional info"
};

axios.post(url, data, {
    auth: {
        username: 'admin',
        password: 'password'
    }
})
.then(response => {
    console.log(response.data);
})
.catch(error => {
    console.error(error);
});
```

##### Retrieving All Logs
```javascript
const axios = require('axios');

const url = 'http://127.0.0.1:8000/logs';

axios.get(url)
.then(response => {
    console.log(response.data);
})
.catch(error => {
    console.error(error);
});
```

##### Retrieving Current Day Logs
```javascript
const axios = require('axios');

const url = 'http://127.0.0.1:8000/current';

axios.get(url)
.then(response => {
    console.log(response.data);
})
.catch(error => {
    console.error(error);
});
```

##### Retrieving Analytics Logs
```javascript
const axios = require('axios');

const url = 'http://127.0.0.1:8000/analytics';

axios.get(url)
.then(response => {
    console.log(response.data);
})
.catch(error => {
    console.error(error);
});
```

### Instructions for Using Dockerfile and Makefile

1. **Build the Docker image**:
   ```sh
   make build
   ```

2. **Run the Docker container**:
   ```sh
   make run
   ```

3. **Stop the Docker container**:
   ```sh
   make stop
   ```

4. **Remove the Docker container**:
   ```sh
   make remove
   ```

5. **Clean Docker images and containers**:
   ```sh
   make clean
   ```

6. **Run tests**:
   ```sh
   make test
   ```

7. **Initialize a Git repository**:
   ```sh
   make git-init
   ```

8. **Check Git status**:
   ```sh
   make git-status
   ```

9. **Push code to Git repository**:
   ```sh
   make git-push
   ```

Ensure that `git-push.sh` is executable by running (Linux/Mac):

```sh
chmod +x git-push.sh
```

On Windows, use `git-push.bat` directly by running:

```cmd
git-push.bat
```

### ChatGPT Prompt

You can use the following prompt to describe this API to ChatGPT in the future:

```
I have an Error Logger API that allows sending error logs from various servers and projects to a MongoDB database, with the ability to retrieve logs. The API has the following endpoints:
- POST /log: Logs an error with fields like project_source, timestamp, error_message, and additional_info. Requires Basic Authentication with username 'admin' and password 'password'.
- GET /logs: Retrieves all error logs, with optional skip and limit parameters.
- GET /current: Retrieves all error logs from the current day in Indian Standard Time.
- GET /analytics: Retrieves analytics logs of all API requests, with optional skip and limit parameters.
Please provide usage examples in Python and JavaScript for each endpoint.
```