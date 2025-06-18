from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.models.models import User


import os
import stripe

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


from pydantic import BaseModel

from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/stripe", tags=["payments"])


class ChceckoutSessionData(BaseModel):
    user_id: str
    amount: float


@router.post("/create-checkout-session")
async def create_checkout_session(
    data: ChceckoutSessionData, db: Session = Depends(get_db)
):
    user_id = data.user_id
    amount = data.amount

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")

    print("Amopunt:", amount)

    if int(amount) == 100:
        price_id = os.getenv("100_CREDITS_PRODUCT_ID")
    elif int(amount) == 500:
        price_id = os.getenv("500_CREDITS_PRODUCT_ID")
    elif int(amount) == 1000:
        price_id = os.getenv("1000_CREDITS_PRODUCT_ID")
    else:
        raise HTTPException(
            status_code=400, detail="Invalid amount. Choose from 100, 500, or 1000."
        )

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="http://localhost:3000/home",
        cancel_url="http://localhost:3000/profile",
        metadata={
            "user_id": user_id,
            "amount": str(amount),
        },
    )
    if not session:
        raise HTTPException(status_code=500, detail="Failed to create checkout session")

    return {"session_id": session.id, "status": "Checkout session created successfully"}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        sig_header = request.headers.get("Stripe-Signature", "")

        endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

        if not payload or not sig_header or not endpoint_secret:
            raise HTTPException(status_code=400, detail="Invalid webhook request")

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid payload: {str(e)}")
        except stripe.error.SignatureVerificationError as e:
            raise HTTPException(status_code=400, detail=f"Invalid signature: {str(e)}")

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]

            user_id = session["metadata"]["user_id"]
            credits_to_add = float(session["metadata"]["amount"])

            print("Processing payment for user:", user_id, "Amount:", credits_to_add)

            try:
                user = db.query(User).filter(User.clerk_id == user_id).first()
                if not user:
                    raise HTTPException(status_code=404, detail="User not found")

                user.credits += int(credits_to_add)

                print("Adding credits to user:", user_id, "Amount:", credits_to_add)
                db.add(user)
                db.commit()

            except Exception as e:
                print("Error processing payment: ", str(e))
                raise HTTPException(
                    status_code=500, detail=f"Error processing payment: {str(e)}"
                )

        return {"status": "success"}
    except HTTPException as http_exc:
        print("HTTPException in stripe_webhook: ", str(http_exc))
        raise http_exc
