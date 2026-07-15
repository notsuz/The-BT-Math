import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from apps.orders.models import Order

from .services import esewa, khalti

logger = logging.getLogger(__name__)


def _success_redirect(order):
    return redirect(f"{reverse('orders:payment_success')}?order={order.transaction_uuid}")


def _failure_redirect(order):
    return redirect(f"{reverse('orders:payment_failure')}?order={order.transaction_uuid}")


class InitiatePaymentView(LoginRequiredMixin, View):
    """Kicks off payment at the chosen gateway for a pending Order."""

    def get(self, request, transaction_uuid):
        order = get_object_or_404(
            Order, transaction_uuid=transaction_uuid, student=request.user, status=Order.Status.PENDING
        )

        if order.gateway == Order.Gateway.ESEWA:
            fields = esewa.build_payment_form_fields(order, request)
            return render(
                request,
                "payments/esewa_redirect.html",
                {"fields": fields, "action_url": settings.ESEWA_PAYMENT_URL},
            )

        if order.gateway == Order.Gateway.KHALTI:
            try:
                data = khalti.initiate_payment(order, request)
            except Exception:
                logger.exception("Khalti initiate failed for order %s", order.transaction_uuid)
                order.mark_failed()
                return _failure_redirect(order)
            order.gateway_reference = data.get("pidx", "")
            order.save(update_fields=["gateway_reference", "updated_at"])
            return redirect(data["payment_url"])

        return _failure_redirect(order)


class EsewaCallbackView(LoginRequiredMixin, View):
    def get(self, request):
        data_param = request.GET.get("data")
        if not data_param:
            return render(request, "orders/payment_failure.html", {"order": None})

        try:
            payload = esewa.decode_callback_payload(data_param)
        except Exception:
            logger.exception("Failed to decode eSewa callback payload")
            return render(request, "orders/payment_failure.html", {"order": None})

        order = get_object_or_404(
            Order, transaction_uuid=payload.get("transaction_uuid"), student=request.user
        )

        status_ok = payload.get("status") == "COMPLETE"
        signature_ok = esewa.verify_callback_signature(payload) if status_ok else None
        try:
            gateway_ok = esewa.check_transaction_status(order) if (status_ok and signature_ok) else None
        except Exception:
            logger.exception("eSewa status-check request failed for order %s", order.transaction_uuid)
            gateway_ok = False
        logger.warning(
            "eSewa callback debug: status_ok=%s signature_ok=%s gateway_ok=%s payload=%s",
            status_ok, signature_ok, gateway_ok, payload,
        )

        if status_ok and signature_ok and gateway_ok:
            order.mark_success(gateway_reference=payload.get("transaction_code", ""))
            return _success_redirect(order)

        order.mark_failed()
        return _failure_redirect(order)


class KhaltiCallbackView(LoginRequiredMixin, View):
    def get(self, request):
        pidx = request.GET.get("pidx")
        purchase_order_id = request.GET.get("purchase_order_id")
        order = get_object_or_404(
            Order, transaction_uuid=purchase_order_id, student=request.user
        )

        try:
            result = khalti.lookup_payment(pidx)
        except Exception:
            logger.exception("Khalti lookup failed for order %s", order.transaction_uuid)
            order.mark_failed()
            return _failure_redirect(order)

        if result.get("status") == "Completed":
            order.mark_success(gateway_reference=result.get("transaction_id", ""))
            return _success_redirect(order)

        order.mark_failed()
        return _failure_redirect(order)
