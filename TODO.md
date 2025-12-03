# TODO: Fix Email Sending Issue for Activation Keys

- [x] Remove send_activation_email call from /api/create_payment endpoint
- [x] Add send_activation_email call to /api/payment_webhook after payment status update
- [x] In webhook, query database for user email, client_key, and plan_type
- [x] Add logging for email sending success/failure in webhook
- [x] Test the changes
