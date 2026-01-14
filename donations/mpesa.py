import requests
import base64
from datetime import datetime
from django.conf import settings
from adrf import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Donation
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

    def get_balance(self):
        """
        Initiate Account Balance Query.
        Note: This is async and result comes to callback.
        For dashboard display, we might need to store the latest balance in DB or use a different approach.
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {"error": "Failed to get access token"}

            url = f"{self.base_url}/mpesa/accountbalance/v1/query"
            
            # Use a dummy initiator password for sandbox if not provided
            initiator = "testapi" # Sandbox default
            security_credential = "..." # Needs to be generated properly with cert
            
            # For now, return a placeholder or error since we lack SecurityCredential generation logic here
            # which requires a certificate.
            return {"error": "M-Pesa Balance Query requires Security Credential generation (Certificate)"}
            
        except Exception as e:
            return {"error": str(e)}

    def get_transactions(self):
        return [] # Not directly supported via simple API

    def b2c_payment(self, amount, phone_number, remarks="Withdrawal"):
        """
        Initiate B2C Payment (Business to Customer) - e.g. Salary, Withdrawal
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {"error": "Failed to get access token"}

            # Format phone number
            if phone_number.startswith("0"):
                phone_number = "254" + phone_number[1:]
            elif phone_number.startswith("+"):
                phone_number = phone_number[1:]

            url = f"{self.base_url}/mpesa/b2c/v1/paymentrequest"
            
            # Note: B2C also requires SecurityCredential (encrypted password)
            # For this demo/task, we'll simulate the structure but it will fail without real certs
            
            payload = {
                "InitiatorName": "testapi",
                "SecurityCredential": "...", # Requires cert encryption
                "CommandID": "BusinessPayment",
                "Amount": int(amount),
                "PartyA": self.shortcode,
                "PartyB": phone_number,
                "Remarks": remarks,
                "QueueTimeOutURL": self.callback_url,
                "ResultURL": self.callback_url,
                "Occasion": "Withdrawal"
            }
            
            # In a real scenario, we would POST this.
            # For now, return a mock success or specific error about credentials
            return {"error": "M-Pesa B2C requires Security Credential generation (Certificate)"}

        except Exception as e:
            return {"error": str(e)}

    @action(detail=False, methods=["post"], url_path="stk-push")
    async def stk_push(self, request):
        try:
            # 1. Get data from request body
            print(request.data)
            phone_number = request.data.get("phone_number")
            amount = request.data.get("amount")
            project_id = request.data.get("project")
            account_ref = request.data.get("account_reference", "Donation")
            
            if not phone_number or not amount or not project_id:
                return Response({"error": "phone_number, amount, and project_id are required"}, status=400)
            
            # Format phone number
            phone_number = str(phone_number).strip().replace("+", "")
            if phone_number.startswith("0"):
                phone_number = "254" + phone_number[1:]
            
            # 2. Authorization
            access_token = self.get_access_token()
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            password_str = f"{self.shortcode}{self.passkey}{timestamp}"
            password = base64.b64encode(password_str.encode()).decode()

            # 3. Prepare Payload (CustomerPayBillOnline)
            payload = {
                "BusinessShortCode": self.shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(float(amount)), 
                "PartyA": phone_number,
                "PartyB": self.shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": self.callback_url,
                "AccountReference": account_ref,
                "TransactionDesc": f"Donation for Project {project_id}",
            }

            # 4. Make Request
            stk_url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            res = requests.post(
                stk_url,
                headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            res_data = res.json()
            
            # 5. Handle Response & Create Record
            if res.status_code == 200 and res_data.get("ResponseCode") == "0":
                """
                    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='donations')
                    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='donations')
                    amount = models.DecimalField(max_digits=12, decimal_places=2)
                    donation_date = models.DateTimeField(auto_now_add=True)
                    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
                    is_anonymous = models.BooleanField(default=False)
                    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
                    status = models.CharField(max_length=20, default='pending')
                """
                # Save the pending donation using Safaricom's CheckoutRequestID
                is_anonymous = False if request.user.is_authenticated else True
                await Donation.objects.acreate(
                    user=request.user if request.user.is_authenticated else None,
                    project_id=project_id,
                    amount=amount,
                    payment_method="mpesa",
                    transaction_id=res_data.get("CheckoutRequestID"),
                    is_anonymous=is_anonymous,
                    status='pending'
                )
                return Response(res_data)
            
            return Response({"error": res_data.get("CustomerMessage", "Request failed")}, status=400)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        

    @action(detail=False, methods=["post"], url_path="callback")
    def mpesa_callback(self, request):
        """
        Handle MPESA Callback (Daraja 3.0)
        """
        try:
            stk_callback = request.data.get("Body", {}).get("stkCallback", {})
            checkout_request_id = stk_callback.get("CheckoutRequestID")
            result_code = stk_callback.get("ResultCode")
            result_desc = stk_callback.get("ResultDesc")

            # 1. Find the donation record using the CheckoutRequestID
            try:
                donation = Donation.objects.get(transaction_id=checkout_request_id)
            except Donation.DoesNotExist:
                print(f"Error: Donation with ID {checkout_request_id} not found.")
                return Response({"ResultCode": 1, "ResultDesc": "Rejected"})

            # 2. Process Success (ResultCode 0)
            if result_code == 0:
                metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
                
                # Extract specific values from the metadata list
                mpesa_receipt = None
                for item in metadata:
                    if item.get("Name") == "MpesaReceiptNumber":
                        mpesa_receipt = item.get("Value")
                
                # Update the donation record
                donation.status = "completed"
                donation.transaction_id = mpesa_receipt # Switch from Checkout ID to actual Receipt
                donation.save()
                
                print(f"Payment Successful: {mpesa_receipt}")
                return Response({"ResultCode": 0, "ResultDesc": "Success"})

            # 3. Process Failure (Any other ResultCode)
            else:
                donation.status = "failed"
                # Optional: store the reason for failure
                # donation.failure_reason = result_desc 
                donation.save()
                
                print(f"Payment Failed for {checkout_request_id}: {result_desc}")
                return Response({"ResultCode": 0, "ResultDesc": "Failure Acknowledged"})
                
        except Exception as e:
            print(f"Callback Error: {str(e)}")
            # M-Pesa expects a 200 OK even on logic errors to stop retrying
            return Response({"ResultCode": 1, "ResultDesc": "Internal Error"}, status=200)