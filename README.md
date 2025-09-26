Zenskar CSV Processing Flow - Local Testing Guide

This guide explains how to run and test the CSV parsing, transformation, and API upload scripts using Windmill locally with Docker.

1. Prerequisites

Docker installed and running:

Mac: Open /Applications/Docker.app

Windows: Start Docker Desktop

Linux: sudo systemctl start docker

curl command available (optional, used to download Windmill files)

Your scripts and config JSON in a folder (e.g., Zenskar)

2. Setup Windmill

Open a terminal and navigate to your project folder:

cd <path-to-Zenskar-folder>


Download the Windmill Docker setup files:

curl https://raw.githubusercontent.com/windmill-labs/windmill/main/docker-compose.yml -o docker-compose.yml
curl https://raw.githubusercontent.com/windmill-labs/windmill/main/Caddyfile -o Caddyfile
curl https://raw.githubusercontent.com/windmill-labs/windmill/main/.env -o .env


Alternatively, you can include these files in your repo to skip the curl steps.

Start Windmill:

docker compose up -d


Access Windmill in your browser:

http://localhost


Default credentials (if first login):

Username: admin@example.com

Password: windmill

3. Prepare Resources

Upload your CSV file:

Go to Resources → New → File Upload in Windmill UI

Upload the CSV you want to test

Upload your configuration JSON as a resource:

Include API endpoint, batch size, field mappings, validators, and business logic

Example resource name: customers_csv

4. Add Scripts to a Flow

Create a new Flow in Windmill:

Step 1 – Parse CSV

Script: script1.py

Input: the uploaded CSV resource

Output: list of rows

Step 2 – Transform Data

Script: script2.py

Input: output from Step 1

Output: transformed customer objects

Logs will show:

Rows skipped due to missing required fields

Invalid email or phone

Step 3 – Upload to Mock API

Script: script3.py

Input: output from Step 2

Logs will show:

Successful uploads

Failed uploads and retry attempts

API endpoint in config points to your mockapi.io resource

5. Running the Flow

Click Run Flow in Windmill.

Watch logs for each step:

Step 2: shows skipped rows and validation errors

Step 3: shows uploaded vs failed rows

Check your MockAPI.io dashboard to see the uploaded customer records.

6. Testing Different Scenarios

Include valid and invalid rows in your CSV:

Missing required fields

Invalid email or phone

Empty cells

Verify logs correctly capture errors

Confirm successful rows reach MockAPI.io

7. Notes

Authentication is skipped because mockapi.io does not require it.

Retry logic for failed API calls is handled in script3.py.

Your flow is modular:

You can replace CSV, change validation rules, or update field mappings via the config JSON without editing scripts.