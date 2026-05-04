# Kenny Enterprise E-commerce (Flask)

This is a simple Flask-based e-commerce site with:

- Product browsing
- Admin interface powered by **Flask-Admin**
- M-Pesa payment integration (STK Push) via Safaricom API

## Setup

1. Create a Python virtual environment and activate it:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set environment variables (or edit `config.py` directly):
   ```powershell
   $env:FLASK_APP = "app.py"
   $env:FLASK_ENV = "development"
   $env:SECRET_KEY = "your-secret"
   $env:MPESA_CONSUMER_KEY = "your-key"
   $env:MPESA_CONSUMER_SECRET = "your-secret"
   $env:MPESA_SHORTCODE = "174379"  # sandbox shortcode
   $env:MPESA_PASSKEY = "your-passkey"
   $env:MPESA_CALLBACK_URL = "https://yourdomain.com/mpesa/callback"
   ```
4. Initialize the database:
   ```sh
   flask init-db
   ```
5. Run the development server:
   ```sh
   flask run
   ```

## Admin panel

Visit `http://127.0.0.1:5000/admin` to access the admin interface. You can manage products, orders, and users from there.

## M-Pesa Integration

- The `mpesa.py` module handles obtaining an access token and sending an STK Push.
- When a customer submits a phone number on the product detail page, the server creates an `Order` record and then calls `stk_push`.
- Safaricom will POST the payment result to the `/mpesa/callback` endpoint. Implement logic there to update order status.


## Notes

This is a starting point. You'll likely want to add:

- User authentication and registration
- A shopping cart and checkout flow with multiple products
- Real payment processing and error handling
- Deployment configuration (HTTPS, domain, environment variables)

---

Happy coding! 🎯