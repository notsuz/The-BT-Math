"""eSewa ePay v2 (sandbox) integration.

Docs: https://developer.esewa.com.np/pages/Epay#/ (sandbox/UAT).
Flow: build a signed form -> browser auto-submits POST to eSewa ->
eSewa redirects back to our success_url with a base64-encoded `data` query
param -> we recompute the signature to verify it wasn't tampered with, then
double-check with eSewa's status-check endpoint before unlocking the course.
"""

import base64
import hashlib
import hmac
import json

import requests
from django.conf import settings
from django.urls import reverse


SIGNED_FIELD_NAMES = "total_amount,transaction_uuid,product_code"


def _sign(message: str) -> str:
    digest = hmac.new(
        settings.ESEWA_SECRET_KEY.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
    ).digest()
    return base64.b64encode(digest).decode("utf-8")


def build_payment_form_fields(order, request) -> dict:
    amount = f"{order.amount:.2f}"
    message = f"total_amount={amount},transaction_uuid={order.transaction_uuid},product_code={settings.ESEWA_MERCHANT_CODE}"
    signature = _sign(message)

    return {
        "amount": amount,
        "tax_amount": "0",
        "total_amount": amount,
        "transaction_uuid": str(order.transaction_uuid),
        "product_code": settings.ESEWA_MERCHANT_CODE,
        "product_service_charge": "0",
        "product_delivery_charge": "0",
        "success_url": request.build_absolute_uri(reverse("payments:esewa_callback")),
        "failure_url": request.build_absolute_uri(reverse("payments:esewa_callback")),
        "signed_field_names": SIGNED_FIELD_NAMES,
        "signature": signature,
    }


def decode_callback_payload(data_param: str) -> dict:
    return json.loads(base64.b64decode(data_param))


def verify_callback_signature(payload: dict) -> bool:
    signed_field_names = payload.get("signed_field_names", "")
    fields = signed_field_names.split(",")
    message = ",".join(f"{field}={payload.get(field, '')}" for field in fields)
    expected = _sign(message)
    return hmac.compare_digest(expected, payload.get("signature", ""))


def check_transaction_status(order) -> bool:
    """Authoritative server-to-server check, used in addition to the
    signature check above before ever marking an order successful."""
    params = {
        "product_code": settings.ESEWA_MERCHANT_CODE,
        "total_amount": f"{order.amount:.2f}",
        "transaction_uuid": str(order.transaction_uuid),
    }
    response = requests.get(settings.ESEWA_STATUS_CHECK_URL, params=params, timeout=15)
    response.raise_for_status()
    return response.json().get("status") == "COMPLETE"
