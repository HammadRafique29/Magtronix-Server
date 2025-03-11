# API Documentation for Flask Automation Service

## Overview
This API provides functionalities to manage and automate tasks related to accounts, fingerprints, and browser automation.

## Base URL
```
http://localhost:8092
```

---

## Endpoints

### 1. Retrieve an Account
**Endpoint:**
```
GET /get-account
```

**Request:**
```json
{
    "account_id": "<string>"
}
```

**Response:**
```json
{
    "status": "success",
    "error": "",
    "data": { "response": <account_data> }
}
```

---

### 2. Retrieve All Accounts
**Endpoint:**
```
GET /get-all-accounts
```

**Response:**
```json
{
    "status": "success",
    "data": { "accounts": <all_accounts_data> }
}
```

---

### 3. Add an Automation Task & Account
**Endpoint:**
```
POST /add-automation-task
```

**Request:**
```json
{
    "acc_type": "<string>",
    "account_id": "<string>",
    "profile_tags": ["<string>", "<string>"] ,
    "proxy_url": "<string | null>",
    "platform": "<string>",
    "data": {<custom_data>}
}
```

**Response:**
```json
{
    "status": "success",
    "account": <account_data>
}
```

---

### 4. Run Automation Task & Account
**Endpoint:**
```
POST /run-automation-task
```

**Request:**
```json
{
    "account_id": "<string>",
    "headless": <boolean>
}
```

**Response:**
```json
{
    "status": "success",
    "address": "http://127.0.0.1:<port>",
    "port": <int>
}
```

---

### 5. Update an Account
**Endpoint:**
```
PUT /update-account
```

**Request:**
```json
{
    "account_id": "<string>",
    "key": "<string>",
    "value": "<string | boolean | object>"
}
```

**Response:**
```json
{
    "status": "success"
}
```

---

### 6. Delete an Account
**Endpoint:**
```
DELETE /delete-account
```

**Request:**
```json
{
    "account_id": "<string>"
}
```

**Response:**
```json
{
    "status": "success"
}
```

---

### 7. Save Cookies
**Endpoint:**
```
POST /save-cookies
```

**Request:**
```json
{
    "filepath": "<string>"
}
```

**Response:**
```json
{
    "status": "success"
}
```

---

### 8. Load Cookies
**Endpoint:**
```
POST /load-cookies
```

**Request:**
```json
{
    "filepath": "<string>"
}
```

**Response:**
```json
{
    "status": "success"
}
```

---

### 9. Get Random Fingerprint
**Endpoint:**
```
GET /random-fingerprint
```

**Request:**
```json
{
    "platform": "<string>"
}
```

**Response:**
```json
{
    "status": "success",
    "fingerprint": <fingerprint_data>
}
```

---

### 10. Launch Browser with Fingerprint
**Endpoint:**
```
POST /launch-browser
```

**Request:**
```json
{
    "profile_name": "<string>",
    "platform": "<string>",
    "proxy_url": "<string | null>",
    "headless": <boolean>
}
```

**Response:**
```json
{
    "status": "success",
    "address": "http://127.0.0.1:<port>",
    "port": <int>
}
```

---

### Notes
- Ensure `account_id` is provided for operations that require it.
- Responses contain `status` to indicate success or failure.
- For automation-related tasks, a browser fingerprint is applied to spoof detection mechanisms.
- Proxy configurations are optional but useful for anonymity.

This API is designed for seamless automation and management of accounts and browser sessions with a focus on fingerprinting and bot evasion.

