from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.models.models import User
import os
import json
from svix.webhooks import Webhook, WebhookVerificationError

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

webhook = Webhook(os.getenv("CLERK_WEBHOOK_SECRET"))


@router.post("/clerk")
async def clerk_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        headers = dict(request.headers)

        signature = headers.get("svix-signature")
        if not signature:
            raise HTTPException(status_code=400, detail="No signature provided")

        try:
            webhook.verify(payload, headers)
        except WebhookVerificationError as e:
            print(f"Webhook verification failed: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid signature")

        payload_data = json.loads(payload)
        event_type = payload_data.get("type")

        if event_type in ["user.created", "user.updated", "user.deleted"]:
            return await clerk_user_handler(payload_data, event_type, db)
        else:
            print(f"Unknown event type: {event_type}")
            return {"status": "success"}

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Done testing
async def clerk_user_handler(payload_data: dict, event_type: str, db: Session):
    try:
        print(f"\n=== Processing {event_type} event ===")

        if event_type == "user.created":
            print("Processing user creation...")
            user_data = payload_data.get("data", {})

            email_addresses = user_data.get("email_addresses", [])

            primary_email = next(
                (
                    email.get("email_address")
                    for email in email_addresses
                    if email.get("id") == user_data.get("primary_email_address_id")
                ),
                email_addresses[0].get("email_address") if email_addresses else None,
            )
            print(f"Primary email identified as: {primary_email}")

            print("Checking if user already exists...")
            user = (
                db.query(User)
                .filter(
                    (User.clerk_id == user_data.get("id"))
                    | (User.email == primary_email)
                )
                .first()
            )

            if user:
                print(f"User already exists in database: {user.email}")

                user.clerk_id = user_data.get("id")
                user.email = primary_email
                user.img_url = user_data.get("image_url", "")

                # Explicitly handle None values
                first_name = user_data.get("first_name")
                last_name = user_data.get("last_name")
                first_name = "" if first_name is None else first_name
                last_name = "" if last_name is None else last_name

                user.username = user_data.get("username") or (
                    first_name + "_" + last_name
                )

                db.commit()
                print("User ID: ", user.clerk_id)
                return {"status": "success"}

            print("Creating new user record...")
            # Explicitly handle None values
            first_name = user_data.get("first_name")
            last_name = user_data.get("last_name")
            first_name = "" if first_name is None else first_name
            last_name = "" if last_name is None else last_name

            new_user = User(
                clerk_id=user_data.get("id"),
                email=primary_email,
                img_url=user_data.get("profile_image_url", ""),
                username=user_data.get("username") or (first_name + "_" + last_name),
            )

            db.add(new_user)
            db.commit()

            print(f"Successfully created new user in database: {new_user.email}")
            print(
                f"User details: clerk_id={new_user.clerk_id}, name={new_user.username}"
            )

            return {"status": "success"}

        elif event_type == "user.deleted":
            print("Processing user deletion...")
            user_data = payload_data.get("data", {})
            user_id = user_data.get("id")

            email_addresses = user_data.get("email_addresses", [])
            primary_email = next(
                (
                    email.get("email_address")
                    for email in email_addresses
                    if email.get("id") == user_data.get("primary_email_address_id")
                ),
                email_addresses[0].get("email_address") if email_addresses else None,
            )

            print(
                f"Attempting to delete user with clerk_id: {user_id} or email: {primary_email}"
            )

            user = (
                db.query(User)
                .filter((User.clerk_id == user_id) | (User.email == primary_email))
                .first()
            )

            if user:
                print(f"Found user to delete: {user.email} (clerk_id: {user.clerk_id})")
                db.delete(user)
                db.commit()

                print(f"Successfully deleted user from database: {user.email}")
                return {"status": "success"}
            else:
                print(f"User not found in database with clerk_id: {user_id}")
                return {"status": "success"}

        elif event_type == "user.updated":
            print("Processing user update...")
            user_data = payload_data.get("data", {})
            user_id = user_data.get("id")

            email_addresses = user_data.get("email_addresses", [])
            primary_email = next(
                (
                    email.get("email_address")
                    for email in email_addresses
                    if email.get("id") == user_data.get("primary_email_address_id")
                ),
                email_addresses[0].get("email_address") if email_addresses else None,
            )

            print(f"Attempting to update user with clerk_id: {user_id}")

            user = (
                db.query(User)
                .filter((User.clerk_id == user_id) | (User.email == primary_email))
                .first()
            )

            if user:
                print(f"Found user to update: {user.email} (clerk_id: {user.clerk_id})")

                email_addresses = user_data.get("email_addresses", [])
                primary_email = next(
                    (
                        email.get("email_address")
                        for email in email_addresses
                        if email.get("id") == user_data.get("primary_email_address_id")
                    ),
                    email_addresses[0].get("email_address")
                    if email_addresses
                    else None,
                )
                print(f"New primary email: {primary_email}")

                print("Updating user fields...")
                user.email = primary_email

                # Explicitly handle None values
                first_name = user_data.get("first_name")
                last_name = user_data.get("last_name")
                first_name = "" if first_name is None else first_name
                last_name = "" if last_name is None else last_name

                user.username = user_data.get("username") or (
                    first_name + "_" + last_name
                )

                user.img_url = user_data.get("profile_image_url", "")

                db.commit()

                print(f"Successfully updated user in database: {user.email}")
                print(f"Updated details: name={user.username}")
                return {"status": "success"}
            else:
                print(f"User not found in database with clerk_id: {user_id}")
                return {"status": "success"}

    except Exception as e:
        print(f"ERROR: Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing webhook")
