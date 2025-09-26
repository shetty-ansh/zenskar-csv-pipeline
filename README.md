# Zenskar CSV Processing Flow Task— Local Docker, Developer and User Guide

This guide explains how to run and test the CSV parsing, transformation, and API upload scripts using **Windmill** locally with **Docker**.

---

## 1. Local Setup using Docker Guide

### Prerequisites

- **Docker** installed and running:
  - **Mac**: Open `/Applications/Docker.app`
  - **Windows**: Start **Docker Desktop**
  - **Linux**: Run `sudo systemctl start docker`
- **curl** (optional, to download Windmill setup files)
- Your scripts and `config.json` in a folder (e.g., `Zenskar/`)

### Setup Windmill

Navigate to your project folder:
```bash
cd <path-to-Zenskar-folder>
```

#### Download and setup Docker files
```bash
curl https://raw.githubusercontent.com/windmill-labs/windmill/main/docker-compose.yml -o docker-compose.yml
curl https://raw.githubusercontent.com/windmill-labs/windmill/main/Caddyfile -o Caddyfile
curl https://raw.githubusercontent.com/windmill-labs/windmill/main/.env -o .env
```
*(These files are also available in the [Windmill GitHub repo](https://github.com/windmill-labs/windmill))*  

#### Start Windmill:
```bash
docker compose up -d
```
- Open [http://localhost](http://localhost) in your browser.

**Default credentials (first login):**
- Username: `admin@windmill.dev`
- Password: `changeme`
- After first login, create a new account and login again.

### Prepare Resources

**Upload your CSV file:**
- Go to **Resources**
- Click **Add New Resource Type**
- Click **Add New Resource**
- Use an ID like: `c_<your-resource-type>`

**Upload your configuration JSON as a resource:**  
Include in config:
- API endpoint
- Batch size
- Field mappings
- Validators
- Business logic

⚠️ When creating the Flow, add a resource in Input named `csvFile` of type `RESOURCE`.

---

## 2. Developer Guide

This section explains how to configure and modify the CSV-to-MockAPI flow using Windmill.

### Where Configuration Lives

All runtime-configurable behavior is driven from a single Windmill resource JSON (e.g.):
```
u/anshshetty22/customers_csv
```
It contains two sections: `CSV_TRANSFORM_CONFIG` and `API_CONFIG`.

#### Example Combined Config

```json
{
  "CSV_TRANSFORM_CONFIG": {
    "FIELD_MAPPING": {
      "CustomerID": "id",
      "FirstName": "first_name",
      "LastName": "last_name",
      "Email": "email",
      "Phone": "contact",
      "City": "city",
      "Country": "country"
    },
    "REQUIRED_FIELDS": ["first_name","last_name","email","contact"],
    "VALIDATORS": {
      "email_pattern": "^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$",
      "phone_min_length": 7,
      "phone_max_length": 15
    },
    "BUSINESS_LOGIC": {
      "source": "csv_upload",
      "name_format": "{first_name} {last_name}",
      "metadata_format": "{city}, {country}"
    }
  },
  "API_CONFIG": {
    "API_ENDPOINT": "https://<your-endpoint>.mockapi.io/customers",
    "BATCH_SIZE": 3,
    "MAX_RETRIES": 3,
    "RETRY_DELAY": 2,
    "ALLOWED_FIELDS": ["id","first_name","last_name","email","contact","city","country","metadata","name"],
    "HEADERS": { "Content-Type": "application/json" },
    "AUTH": { "type": "none" }
  }
}
```
> **Important:** Update the actual `API_ENDPOINT` to your project's MockAPI URL.

---

### How to Add / Change a Field Mapping

- Edit `CSV_TRANSFORM_CONFIG.FIELD_MAPPING` in the resource.
- The left side is the CSV header name, the right side is the target customer object key.

**Example (adding PostalCode → postal_code):**
```json
"FIELD_MAPPING": {
  "PostalCode": "postal_code",
  ...
}
```
No code change required — Script 2 will pick it up automatically.

---

### How to Add / Change Validation Rules

- Validation is encoded in `CSV_TRANSFORM_CONFIG.VALIDATORS`.

**Email regex:**  
Change `email_pattern` (raw string, used by `re.compile()`).

**Phone rules:**  
Change `phone_min_length` & `phone_max_length`.

**Example (accept 6–20 digits):**
```json
"VALIDATORS": {
  "email_pattern": "^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$",
  "phone_min_length": 6,
  "phone_max_length": 20
}
```
Script 2 reads these and applies them; no code change needed.

---

### How to Change Business Logic

- `BUSINESS_LOGIC` contains templates used by `.format(**customer)`:

  - `name_format`: e.g. `"{first_name} {last_name}"`
  - `metadata_format`: e.g. `"{city}, {country}"`

**To include postal code:**
```json
"name_format": "{first_name} {last_name}",
"metadata_format": "{city}, {country}, {postal_code}"
```
If the template references keys that don’t exist, Script 2 will mark the row invalid and log the missing key.

---

### How to Change API Behavior (Batch/Retry/Headers/Auth)

Edit `API_CONFIG`:

- `BATCH_SIZE` — number of customers per batch (Script 3 batches for progress logs; posting is per-customer inside batch).
- `MAX_RETRIES` & `RETRY_DELAY` — retry policy for transient failures.
- `ALLOWED_FIELDS` — whitelist of keys to send in API payloads.
- `HEADERS` — any HTTP headers (e.g., `{"Content-Type":"application/json"}`).
- `AUTH` — object with:
    - `{"type":"none"}`
    - `{"type":"bearer","token":"TOKEN"}`
    - `{"type":"basic","username":"u","password":"p"}`

Script 3 reads `AUTH` and applies headers/auth automatically — just change config.

---

### How to Add a Custom Validator or Business Check

If you need a new type of validation (e.g., checksum, external lookup):

1. Add a config flag to `CSV_TRANSFORM_CONFIG` (e.g., `"check_tax_id": true`).
2. Implement the validation function in Script 2:
```python
if config["CSV_TRANSFORM_CONFIG"].get("check_tax_id"):
    if not is_valid_tax(customer.get("tax_id")):
        errors.append("Invalid tax_id")
```
Script 2 already collects errors and logs them; the row will be returned as invalid.

---

### Developer Tips & Best Practices

- Keep `FIELD_MAPPING` consistent with CSV headers (case-sensitive).
- Use defensive templates in `BUSINESS_LOGIC` (only reference keys you know exist, or handle missing ones gracefully).
- For major changes, update `ALLOWED_FIELDS` to avoid sending unexpected keys to the API.
- When adding complex validators, unit-test them locally (use a small Python script) before pushing to Windmill.

---

## 3. User Guide

### Quick Start

1. **Open Windmill UI** (local or cloud).
2. Ensure the config resource `u/anshshetty22/customers_csv` exists and is up-to-date (especially `API_ENDPOINT`).
3. **Upload your CSV:**
   - Go to Resources → New → File Upload → select your CSV.
   - Name the resource (e.g., `input_customers.csv`) for clarity.

4. **Open your Flow** (with three steps):
    - **Step 1:** CSV Parser → input: uploaded CSV resource.
    - **Step 2:** Transformer → inputs: Step1 output + config resource.
    - **Step 3:** Uploader → input: Step2 output + config resource.
    - Click **Run** on the flow.

### What to Watch in UI

- **Step 1 logs:** Total valid rows parsed, malformed/skipped rows.
- **Step 2 logs:**  
  - Per-row rejection:  
    `❌ Row N failed: [errors] | Data: {raw row}`
  - Summary:  
    `✅ Transformed X valid customers out of Y rows`
  - Results tab includes:
    ```json
    {
      "valid": [ {...}, {...} ],
      "invalid": [ {"row":2,"data":...,"errors":[...]}, ... ]
    }
    ```
- **Step 3 logs:**  
  - Per-batch header: `--- Processing Batch N (size=M) ---`
  - Per-customer lines:  
    - Success: `Uploaded: {id,name,email}`  
    - Failure: `Failed ... status code or Exception`
  - Final summary: `{"uploaded": X, "failed": Y}`

### Troubleshooting

- **No customers uploaded, only network exceptions:** Check API_ENDPOINT and network connectivity.
- **404 Not Found:** Check API_ENDPOINT for typos/trailing slash; make sure resource path matches MockAPI.
- **400 Bad Request:** Make sure payload shape matches MockAPI fields; check ALLOWED_FIELDS.
- **Rows skipped for missing fields:** CSV headers must match FIELD_MAPPING and required fields.
- **Missing keys in business logic:** Update BUSINESS_LOGIC template or FIELD_MAPPING.

### Quick Checklist Before Demo/Run

- Confirm `customers_csv` resource contains intended config.
- Upload sample CSV (mixed good/bad rows).
- Run flow and watch logs (Script 2: data problems, Script 3: API issues).
- Check MockAPI dashboard for created records.

---

## 4. mockapi.io Config

### Resource Schema

Create a `customers` resource in MockAPI with these fields:

| Field name   | Type      | Notes                                            |
|--------------|-----------|--------------------------------------------------|
| id           | Object ID | MockAPI generated or set by you (string)         |
| name         | String    | Full name (first + last)                         |
| first_name   | String    |                                                  |
| last_name    | String    |                                                  |
| email        | String    |                                                  |
| contact      | String    | Phone number                                     |
| city         | String    |                                                  |
| country      | String    |                                                  |
| metadata     | Object    | JSON object (e.g. `{"source":"csv_upload"}`)     |

*The `metadata` field type should be set as Object in MockAPI resource settings so nested objects work.*

### Endpoint URL

- Example:  
  `https://68d54743e29051d1c0adfb54.mockapi.io/zenskar/customers`
- **No trailing slash** — MockAPI treats `/customers/` differently and may return 404.

To confirm the correct URL:
- Open MockAPI project → click the customers resource → copy the base resource URL for POST/GET.

### Example Payload (what Script 3 sends)

```json
{
  "id": "C001",
  "first_name": "Ananya",
  "last_name": "Sharma",
  "name": "Ananya Sharma",
  "email": "ananya.sharma@example.com",
  "contact": "9876543210",
  "city": "Mumbai",
  "country": "India",
  "metadata": {
    "source": "csv_upload",
    "city_country": "Mumbai, India"
  }
}
```
- Only keys in `ALLOWED_FIELDS` are sent.
- Make sure `metadata` is allowed as an object. If not, stringify it.

---

**Notes:**
- Authentication is skipped here (mockapi.io doesn't support it).
- Retry logic for failed API calls is in `script3.py`.
- The flow is modular:  
  You can replace the CSV, change validation rules, update field mappings via `config.json`, all without major changes to Python scripts.

