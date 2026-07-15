"""Khalti ePayment v2 (sandbox) integration.

Docs: https://docs.khalti.com/khalti-epayment/ (test/sandbox environment).
Flow: server-side "initiate" call gets a payment_url + pidx -> we redirect
the browser there -> Khalti redirects back to our return_url with pidx in
the query string -> we call "lookup" server-to-server to confirm the
transaction's real status before unlocking the course.
"""

import requests
from django.conf import settings
from django.urls import reverse


def _headers():
    return {"Authorization": f"Key {settings.KHALTI_SECRET_KEY}"}


def initiate_payment(order, request) -> dict:
    return_url = request.build_absolute_uri(reverse("payments:khalti_callback"))
    payload = {
        "return_url": return_url,
        "website_url": request.build_absolute_uri("/"),
        "amount": int(order.amount * 100),  # paisa
        "purchase_order_id": str(order.transaction_uuid),
        "purchase_order_name": order.course.title,
        "customer_info": {
            "name": order.student.get_full_name() or order.student.email,
            "email": order.student.email,
        },
    }
    response = requests.post(
        settings.KHALTI_INITIATE_URL, json=payload, headers=_headers(), timeout=15
    )
    response.raise_for_status()
    return response.json()  # contains "payment_url" and "pidx"


def lookup_payment(pidx: str) -> dict:
    response = requests.post(
        settings.KHALTI_LOOKUP_URL, json={"pidx": pidx}, headers=_headers(), timeout=15
    )
    response.raise_for_status()
    return response.json()  # contains "status": "Completed"/"Pending"/"Expired"/...
