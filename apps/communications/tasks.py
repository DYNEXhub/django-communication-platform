"""
Celery tasks for communications app.
Handles async message sending and tracking.
"""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, email_message_id):
    """
    Send a single email via configured channel.

    Args:
        email_message_id: UUID of the EmailMessage to send

    Returns:
        bool: True if sent successfully
    """
    from apps.communications.models import EmailMessage

    try:
        message = EmailMessage.objects.select_related('channel', 'contact').get(id=email_message_id)

        # TODO: Integrate with actual email provider using channel.credentials
        # For now, mark as sent
        message.status = 'SENT'
        message.save(update_fields=['status', 'updated_at'])

        logger.info(f"Email sent: {message.subject} to {message.contact.email}")
        return True

    except EmailMessage.DoesNotExist:
        logger.error(f"EmailMessage {email_message_id} not found")
        return False

    except Exception as exc:
        logger.error(f"Email send failed for {email_message_id}: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_sms_task(self, sms_message_id):
    """
    Send SMS via configured provider.

    Args:
        sms_message_id: UUID of the SMSMessage to send

    Returns:
        bool: True if sent successfully
    """
    from apps.communications.models import SMSMessage

    try:
        message = SMSMessage.objects.select_related('channel', 'contact').get(id=sms_message_id)

        # Calculate segments before sending
        message.segments = message.calculate_segments()

        # TODO: Integrate with SMS provider (Twilio, Vonage, etc.)
        # For now, mark as sent
        message.status = 'SENT'
        message.save(update_fields=['status', 'segments', 'updated_at'])

        logger.info(f"SMS sent to {message.contact.phone} ({message.segments} segments)")
        return True

    except SMSMessage.DoesNotExist:
        logger.error(f"SMSMessage {sms_message_id} not found")
        return False

    except Exception as exc:
        logger.error(f"SMS send failed for {sms_message_id}: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_whatsapp_task(self, whatsapp_message_id):
    """
    Send WhatsApp message via API.

    Args:
        whatsapp_message_id: UUID of the WhatsAppMessage to send

    Returns:
        bool: True if sent successfully
    """
    from apps.communications.models import WhatsAppMessage

    try:
        message = WhatsAppMessage.objects.select_related('channel', 'contact').get(id=whatsapp_message_id)

        # TODO: Integrate with WhatsApp Business API or provider (Twilio, 360dialog, etc.)
        # For now, mark as sent
        message.status = 'SENT'
        message.save(update_fields=['status', 'updated_at'])

        logger.info(f"WhatsApp sent to {message.contact.phone}")
        return True

    except WhatsAppMessage.DoesNotExist:
        logger.error(f"WhatsAppMessage {whatsapp_message_id} not found")
        return False

    except Exception as exc:
        logger.error(f"WhatsApp send failed for {whatsapp_message_id}: {exc}")
        raise self.retry(exc=exc)


@shared_task
def process_email_tracking(tracking_id, event, metadata=None):
    """
    Process email open/click tracking events.

    Args:
        tracking_id: UUID tracking ID of the email
        event: Event type ('opened' or 'clicked')
        metadata: Optional dict with additional tracking data

    Returns:
        bool: True if processed successfully
    """
    from apps.communications.models import EmailMessage
    from django.utils import timezone

    try:
        message = EmailMessage.objects.get(tracking_id=tracking_id)

        if event == 'opened':
            message.open_count += 1
            if not message.opened:
                message.opened = True
                message.first_opened_at = timezone.now()
            message.save(update_fields=['opened', 'open_count', 'first_opened_at', 'updated_at'])
            logger.info(f"Email opened: tracking_id={tracking_id}, count={message.open_count}")

        elif event == 'clicked':
            message.click_count += 1
            message.clicked = True
            message.save(update_fields=['clicked', 'click_count', 'updated_at'])
            logger.info(f"Email clicked: tracking_id={tracking_id}, count={message.click_count}")

        return True

    except EmailMessage.DoesNotExist:
        logger.warning(f"Tracking: EmailMessage not found for tracking_id {tracking_id}")
        return False
    except Exception as exc:
        logger.error(f"Email tracking failed for {tracking_id}: {exc}")
        return False
