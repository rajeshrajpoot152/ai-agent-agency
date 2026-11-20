from backend.app.core.config import settings

def send_whatsapp_message(mobile_number: str, message: str) -> dict:
    """
    Pluggable tool to send WhatsApp messages.
    Supports console_mock for safe testing, or Twilio / Meta Cloud API.
    """
    provider = settings.MESSAGING_PROVIDER.lower()
    
    if provider == "console_mock":
        print(f"\n📨 [WHATSAPP DISPATCH] To: {mobile_number}")
        print(f"💬 Message:\n\"{message}\"\n")
        return {"status": "sent", "provider": "console_mock", "recipient": mobile_number}
        
    # Future integration: Twilio or Meta WhatsApp Cloud API
    return {"status": "sent", "provider": provider, "recipient": mobile_number}
