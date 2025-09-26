#For validation

import re
import wmill


def main(rows):
    
    config = wmill.get_resource("u/anshshetty22/customers_csv") #Change with your resource


    #Change if you are not using my exact json
    FIELD_MAPPING = config["CSV_TRANSFORM_CONFIG"]["FIELD_MAPPING"]
    REQUIRED_FIELDS = config["CSV_TRANSFORM_CONFIG"]["REQUIRED_FIELDS"]
    VALIDATORS = config["CSV_TRANSFORM_CONFIG"]["VALIDATORS"]
    BUSINESS_LOGIC = config["CSV_TRANSFORM_CONFIG"]["BUSINESS_LOGIC"]

    email_pattern = re.compile(VALIDATORS["email_pattern"])
    phone_min = VALIDATORS["phone_min_length"]
    phone_max = VALIDATORS["phone_max_length"]

    valid_customers = []
    invalid_customers = []

    for idx, row in enumerate(rows, start=1):
        customer = {}
        errors = []

        # This is for field mapping-
        for src, target in FIELD_MAPPING.items():
            value = row.get(src) or ""
            customer[target] = value.strip()

        # Checking for req fields
        missing_fields = [f for f in REQUIRED_FIELDS if not customer.get(f)]
        if missing_fields:
            errors.append(f"Missing required fields: {', '.join(missing_fields)}")

        # Email validation
        if customer.get("email") and not email_pattern.match(customer["email"]):
            errors.append(f"Invalid email: {customer['email']}")

        # Phone validation
        contact = customer.get("contact", "")
        if contact and not (
            phone_min <= len(contact) <= phone_max and contact.isdigit()
        ):
            errors.append(f"Invalid phone: {contact}")

        # This is for specific business logic-
        try:
            customer["name"] = BUSINESS_LOGIC["name_format"].format(**customer)
            customer["metadata"] = {
                "source": BUSINESS_LOGIC["source"],
                "city_country": BUSINESS_LOGIC["metadata_format"].format(**customer),
            }
        except KeyError as e:
            errors.append(f"Required key for business logic is missing: {e}")

        if errors:
            print(f"Row {idx} failed: {errors} | Data: {row}")
            invalid_customers.append({"row": idx, "data": row, "errors": errors})
        else:
            valid_customers.append(customer)

    print(f"Transformed {len(valid_customers)} valid customers out of {len(rows)} rows")
    print(f"Found {len(invalid_customers)} invalid rows")

    return {"valid": valid_customers, "invalid": invalid_customers}

