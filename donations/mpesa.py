import requests
import base64
from datetime import datetime
from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import json

class MpesaClient(viewsets.ViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.callback_url = settings.MPESA_CALLBACK_URL
        self.passkey = settings.MPESA_PASSKEY
        self.shortcode = settings.MPESA_SHORTCODE
        self.base_url = settings.MPESA_BASE_URL

    def get_access_token(self):
        try:
            # FIXED: Correct URL - removed "/mpesa" from the path
            url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
            
            # Debug: Print the URL for verification
            print(f"Requesting access token from: {url}")
            
            # Make the request
            res = requests.get(
                url,
                auth=(self.consumer_key, self.consumer_secret),
                headers={'Content-Type': 'application/json'},
                timeout=30  # Add timeout
            )
            
            # Debug: Check response
            print(f"Status Code: {res.status_code}")
            print(f"Response Text: {res.text}")
            
            # Check if request was successful
            res.raise_for_status()
            
            # Try to parse JSON
            data = res.json()
            access_token = data.get("access_token")
            
            if not access_token:
                print(f"No access token in response: {data}")
                return None
                
            return access_token
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Raw response: {res.text if 'res' in locals() else 'No response'}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    @action(detail=False, methods=["post"], url_path="stk-push")
    def stk_push(self, request):
        try:
            # 1. Get data from request body
            phone_number = request.data.get("phone_number")
            amount = request.data.get("amount")
            account_ref = request.data.get("account_reference", "Donation")
            
            if not phone_number or not amount:
                return Response(
                    {"error": "phone_number and amount are required"},
                    status=400
                )
            
            # 2. Generate M-Pesa Credentials
            access_token = self.get_access_token()
            
            if not access_token:
                return Response(
                    {"error": "Failed to get access token from MPESA API"},
                    status=500
                )
            
            # Format phone number (remove leading 0 if exists, add 254)
            if phone_number.startswith("0"):
                phone_number = "254" + phone_number[1:]
            elif phone_number.startswith("+"):
                phone_number = phone_number[1:]
            
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            password_str = f"{self.shortcode}{self.passkey}{timestamp}"
            password = base64.b64encode(password_str.encode()).decode()

            # 3. Prepare Payload
            payload = {
                "BusinessShortCode": self.shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),  # Convert to int
                "PartyA": phone_number,
                "PartyB": self.shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": self.callback_url,
                "AccountReference": account_ref,
                "TransactionDesc": "Donation Payment",
            }
            
            print(f"STK Push Payload: {payload}")

            # 4. Make Request to Safaricom
            stk_url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            print(f"Making STK request to: {stk_url}")
            
            res = requests.post(
                stk_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30
            )
            
            print(f"STK Response Status: {res.status_code}")
            print(f"STK Response: {res.text}")
            
            res.raise_for_status()
            
            return Response(res.json())
            
        except requests.exceptions.RequestException as e:
            print(f"STK Request failed: {e}")
            return Response(
                {"error": f"MPESA API request failed: {str(e)}"},
                status=500
            )
        except Exception as e:
            print(f"Unexpected error in STK push: {e}")
            return Response(
                {"error": "Internal server error"},
                status=500
            )
    # Add this to your views.py or mpesa.py

    @action(detail=False, methods=["post"], url_path="callback")
    def mpesa_callback(self, request):
        """
        Handle MPESA Callback
        """
        try:
            callback_data = request.data
            
            # Log the callback
            print(f"MPESA Callback received: {callback_data}")
            
            # Process the callback
            result_code = callback_data.get("Body", {}).get("stkCallback", {}).get("ResultCode")
            
            if result_code == 0:
                # Payment was successful
                # Extract transaction details
                callback_metadata = callback_data.get("Body", {}).get("stkCallback", {}).get("CallbackMetadata", {}).get("Item", [])
                
                # Process successful payment
                print("Payment successful!")
                
                return Response({"result": "success", "message": "Payment processed successfully"})
            else:
                # Payment failed
                result_desc = callback_data.get("Body", {}).get("stkCallback", {}).get("ResultDesc", "Payment failed")
                print(f"Payment failed: {result_desc}")
                
                return Response({"result": "failed", "message": result_desc})
                
        except Exception as e:
            print(f"Error processing MPESA callback: {e}")
            return Response({"error": str(e)}, status=500)