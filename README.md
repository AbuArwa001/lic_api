# Langata Islamic Center (LIC) - API

A robust and secure backend API for the Langata Islamic Center, built with Django and Django REST Framework.

## 🌟 Features

- **Donation Management**:
  - **M-Pesa Integration**: Handles STK Push requests, callbacks, and transaction verification via Safaricom Daraja API.
  - **Payment Gateway Support**: Integrated clients for Paystack, Stripe, and PayPal.
  - **Transaction Tracking**: Detailed logs of all donation attempts and successful payments.
- **Project & Campaign API**: Manage community projects, funding goals, and progress tracking.
- **Authentication**: Secure authentication and authorization using Firebase Admin SDK.
- **Contact Management**: API endpoints for handling contact form submissions and inquiries.
- **Analytics**: Data endpoints for donation summaries and project statistics.
- **Admin Interface**: Django Admin customized for managing the platform's data.

## 🚀 Tech Stack

- **Framework**: [Django](https://www.djangoproject.com/)
- **API Toolkit**: [Django REST Framework](https://www.django-rest-framework.org/)
- **Database**: PostgreSQL (Production) / SQLite (Development)
- **Authentication**: [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
- **Payment Integrations**:
  - Safaricom Daraja API (M-Pesa)
  - Paystack API
  - Stripe API
  - PayPal API
- **Task Queue**: Celery (Optional, for background tasks)

## 🛠️ Getting Started

### Prerequisites

- Python 3.10 or later
- pip and venv
- PostgreSQL (optional for local development)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/AbuArwa001/lic_api.git
   cd lic_api
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory and add the following:

   ```env
   DEBUG=True
   SECRET_KEY=your_django_secret_key
   DATABASE_URL=postgres://user:password@localhost:5432/lic_db

   # M-Pesa
   MPESA_CONSUMER_KEY=your_key
   MPESA_CONSUMER_SECRET=your_secret
   MPESA_SHORTCODE=your_shortcode
   MPESA_PASSKEY=your_passkey

   # Paystack
   PAYSTACK_SECRET_KEY=your_key

   # Firebase
   FIREBASE_SERVICE_ACCOUNT_JSON=your_json_string
   ```

5. Run migrations:

   ```bash
   python manage.py migrate
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

The API will be available at [http://www.liwomasjid.co.ke/api/v1](http://localhost:8000/api/v1).

## 📁 Project Structure

- `lic_api/`: Core settings and configuration.
- `donations/`: Donation processing, payment clients, and webhooks.
- `projects/`: Project and campaign management.
- `users/`: User profiles and authentication logic.
- `contact/`: Contact form handling.

## 📜 License

This project is licensed under the MIT License.
