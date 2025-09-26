#In order to push everything to an API

import wmill
import httpx
import time


def main(customers):
    # Ensuring input is a list
    if isinstance(customers, dict):
        customers = [customers]
    elif not isinstance(customers, list):
        raise TypeError(f"Expected list of customers, got {type(customers)}")

    config = wmill.get_resource("u/anshshetty22/customers_csv")
    api_config = config["API_CONFIG"]

    endpoint = api_config["API_ENDPOINT"]
    batch_size = api_config["BATCH_SIZE"]
    max_retries = api_config["MAX_RETRIES"]
    retry_delay = api_config["RETRY_DELAY"]
    allowed_fields = api_config["ALLOWED_FIELDS"]
    headers = api_config.get("HEADERS", {})
    auth_config = api_config.get("AUTH", {"type": "none"})

    total_uploaded = 0
    total_failed = 0

    # Auth setup
    auth = None
    if auth_config["type"] == "bearer" and auth_config.get("token"):
        headers["Authorization"] = f"Bearer {auth_config['token']}"
    elif (
        auth_config["type"] == "basic"
        and auth_config.get("username")
        and auth_config.get("password")
    ):
        auth = (auth_config["username"], auth_config["password"])

    def short_info(cust):
        return {
            "id": cust.get("id"),
            "name": cust.get("name"),
            "email": cust.get("email"),
        }

    for batch_num, i in enumerate(range(0, len(customers), batch_size), start=1):
        batch = customers[i : i + batch_size]
        batch_uploaded = 0
        batch_failed = 0

        print(f"\n--- Processing Batch {batch_num} (size={len(batch)}) ---")

        for customer in batch:
            payload = {k: customer[k] for k in allowed_fields if k in customer}

            for attempt in range(1, max_retries + 1):
                try:
                    response = httpx.post(
                        endpoint, json=payload, headers=headers, auth=auth, timeout=10.0
                    )
                    if response.status_code in (200, 201):
                        total_uploaded += 1
                        batch_uploaded += 1
                        print(f"Uploaded: {short_info(customer)}")
                        break
                    else:
                        print(
                            f"Failed ({response.status_code}) attempt {attempt} for {short_info(customer)}: {response.text}"
                        )
                except Exception as e:
                    print(
                        f"Exception on attempt {attempt} for {short_info(customer)}: {e}"
                    )
                time.sleep(retry_delay)
            else:
                total_failed += 1
                batch_failed += 1
                print(f"Giving up on: {short_info(customer)}")

        print(
            f"Batch {batch_num} summary → Uploaded: {batch_uploaded}, Failed: {batch_failed}"
        )

    print(f"Total uploaded: {total_uploaded}")
    print(f"Total failed: {total_failed}")
    return {"uploaded": total_uploaded, "failed": total_failed}
