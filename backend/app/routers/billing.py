"""
Billing: Stripe Checkout for subscribing to a plan, a webhook that keeps
the database in sync with what Stripe actually charged, and a portal link
for managing/canceling a subscription.

IMPORTANT — this is real Stripe SDK usage, written correctly, but it has
never been run against a live Stripe account from this environment (no
network access here to test it). Treat it as a solid starting point that
needs an actual test against Stripe test mode before you trust it, not as
verified-working code. The other backend pieces in this project were at
least compile-checked against realistic data; this one additionally needs
a live Stripe test account, real price IDs, and `stripe listen` (or a
deployed webhook URL) to exercise the webhook path at all.

Without STRIPE_SECRET_KEY set, every endpoint here returns a clear 500
rather than crashing unhelpfully — same pattern as tutor.py's missing
ANTHROPIC_API_KEY handling.
"""
import os

import stripe
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.db_models import Subscription, User

load_dotenv()

router = APIRouter()

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")

PRICE_ENV_VARS = {
    "basic": "STRIPE_PRICE_BASIC",
    "professional": "STRIPE_PRICE_PROFESSIONAL",
    "premium": "STRIPE_PRICE_PREMIUM",
}


def _require_stripe_configured():
    api_key = os.environ.get("STRIPE_SECRET_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Billing isn't configured on this server. Set STRIPE_SECRET_KEY (and the "
                   "STRIPE_PRICE_* variables) in .env — see .env.example.",
        )
    stripe.api_key = api_key


def _get_price_id(plan: str) -> str:
    if plan not in PRICE_ENV_VARS:
        raise HTTPException(status_code=400, detail=f"Unknown or non-purchasable plan: {plan}")
    price_id = os.environ.get(PRICE_ENV_VARS[plan])
    if not price_id:
        raise HTTPException(status_code=500, detail=f"{PRICE_ENV_VARS[plan]} isn't set in .env for plan '{plan}'.")
    return price_id


def _get_or_create_stripe_customer(user: User, db: Session) -> str:
    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if sub and sub.payment_provider_customer_id:
        return sub.payment_provider_customer_id

    customer = stripe.Customer.create(email=user.email, name=user.full_name, metadata={"user_id": str(user.id)})

    if sub:
        sub.payment_provider_customer_id = customer.id
    else:
        sub = Subscription(user_id=user.id, plan="free", status="active", payment_provider_customer_id=customer.id)
        db.add(sub)
    db.commit()
    return customer.id


class CheckoutRequest(BaseModel):
    plan: str


class CheckoutResponse(BaseModel):
    checkout_url: str


class PortalResponse(BaseModel):
    portal_url: str


@router.post("/create-checkout-session", response_model=CheckoutResponse)
def create_checkout_session(
    request: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_stripe_configured()
    price_id = _get_price_id(request.plan)
    customer_id = _get_or_create_stripe_customer(current_user, db)

    session = stripe.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{FRONTEND_URL}/dashboard.html?checkout=success",
        cancel_url=f"{FRONTEND_URL}/landing.html?checkout=cancelled",
        metadata={"user_id": str(current_user.id), "plan": request.plan},
    )
    return CheckoutResponse(checkout_url=session.url)


@router.get("/portal", response_model=PortalResponse)
def create_portal_session(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_stripe_configured()
    sub = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    if not sub or not sub.payment_provider_customer_id:
        raise HTTPException(status_code=400, detail="No billing account yet — subscribe to a plan first.")

    session = stripe.billing_portal.Session.create(
        customer=sub.payment_provider_customer_id,
        return_url=f"{FRONTEND_URL}/dashboard.html",
    )
    return PortalResponse(portal_url=session.url)


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Point this at https://yourdomain.com/api/billing/webhook in the Stripe
    dashboard (or `stripe listen --forward-to localhost:8000/api/billing/webhook`
    for local testing). Verifies the signature before trusting anything in
    the payload — never skip that check.
    """
    _require_stripe_configured()
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    if not webhook_secret:
        raise HTTPException(status_code=500, detail="STRIPE_WEBHOOK_SECRET isn't set in .env.")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid webhook payload or signature: {exc}") from exc

    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        user_id = data.get("metadata", {}).get("user_id")
        plan = data.get("metadata", {}).get("plan")
        if user_id and plan:
            user = db.query(User).filter(User.id == int(user_id)).first()
            sub = db.query(Subscription).filter(Subscription.user_id == int(user_id)).first()
            if user:
                user.plan = plan
            if sub:
                sub.plan = plan
                sub.status = "active"
            db.commit()

    elif event_type in ("customer.subscription.updated", "customer.subscription.deleted"):
        customer_id = data.get("customer")
        sub = db.query(Subscription).filter(Subscription.payment_provider_customer_id == customer_id).first()
        if sub:
            if event_type == "customer.subscription.deleted":
                sub.status = "canceled"
                sub.plan = "free"
                user = db.query(User).filter(User.id == sub.user_id).first()
                if user:
                    user.plan = "free"
            else:
                sub.status = data.get("status", sub.status)
            db.commit()

    return {"received": True}
