import hmac
import hashlib
import base64

def generate_hmac_signature(key, message):
    """
    Generates an HMAC-SHA256 signature.

    Args:
        key: The secret key (string).
        message: The message to sign (string).

    Returns:
        str: The generated HMAC hex digest
    """
    return hmac.new(
        key=key.encode('utf-8'),
        msg=message.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    import os
    rzp_key = os.getenv("RAZORPAY_KEY_SECRET")
    order_id = "order_QT8uZkDMbPmsJx"
    payment_id = "pay_QT8vUXR5PiDcNL"
    generated = generate_hmac_signature(rzp_key, f"{order_id}|{payment_id}")
    print(generated)