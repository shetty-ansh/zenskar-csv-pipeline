# Zenskar CSV Processing Flow - Local Testing Guide

This guide explains how to run and test the CSV parsing, transformation, and API upload scripts using **Windmill** locally with **Docker**.

---

## 1. Prerequisites

Ensure the following are set up on your system:

- **Docker** installed and running:
  - **Mac**: Open `/Applications/Docker.app`
  - **Windows**: Start **Docker Desktop**
  - **Linux**: Run `sudo systemctl start docker`
- **curl** command available (optional, used to download Windmill setup files)
- Your scripts and `config.json` in a folder (e.g., `Zenskar/`)

---

## 2. Setup Windmill

### Navigate to your project folder:

```bash
cd <path-to-Zenskar-folder>

```
## 3. Download and setup Docker Files

```bash
 curl https://raw.githubusercontent.com/windmill-labs/windmill/main/docker-compose.yml -o docker-compose.yml
 curl https://raw.githubusercontent.com/windmill-labs/windmill/main/Caddyfile -o Caddyfile
 curl https://raw.githubusercontent.com/windmill-labs/windmill/main/.env -o .env
```
-These files are also available in the Windmill GitHub repo

### Start Windmill:

```bash
docker compose up -d

```
- Access Windmill in your browser:

Open http://localhost

**Default credentials (on first login)**:

- Username: admin@windmill.dev

- Password: changeme

**After first login, create a new account and login again.**

3. Prepare Resources
Upload your CSV file:

**Go to Resources**

- 1.Click Add New Resource Type

- 2.Click Add New Resource

Use ID like: "c_<your-resource-type>"

(You can refer to the example resource file in the repo)

Upload your configuration JSON as a resource:

**Include the following in the config:**

- API endpoint
- Batch size
- Field mappings
- Validators
- Business logic

⚠️ When creating the Flow, add a resource in Input named csvFile of type RESOURCE

## 4. Add Scripts to a Flow

**🔹 Step 1** – Parse CSV

- Script: script1.py

- Input: Uploaded CSV resource

- Output: List of rows

🔁 Connect to next script

**🔹 Step 2**– Transform Data

- Script: script2.py

- Input: Output from Step 1

- Output: Transformed customer objects

🔁 Connect to next script

✅ Logs will show:
```bash
Rows skipped due to missing required fields

Invalid email or phone
```
**🔹 Step 3** – Upload to Mock API

- Script: script3.py

- Input: Output from Step 2

✅ Logs will show:
```
Successful uploads

Failed uploads and retry attempts
```

API endpoint in config should point to your mockapi.io resource

## 5. Running the Flow

- Click Run Flow in Windmill.

🧾 Watch logs in each step:

Step 2: Skipped rows and validation errors

Step 3: Uploaded vs failed rows

- Verify on **mockapi.io** dashboard that customer records are uploaded.

## 6. Testing Different Scenarios

- Include both valid and invalid rows in your CSV:

- Missing required fields

- Invalid email or phone

- Empty cells

**Verify that:**

- Logs correctly capture all errors

- Successful rows are uploaded to mockapi.io

## 7. Notes

- Authentication is skipped here (mockapi.io doesn't support it).

- Retry logic for failed API calls is implemented in script3.py.

- The flow is modular:

You can replace the CSV

Change validation rules

Update field mappings via config.json

**➜ All without majorly modifying any Python scripts.**

