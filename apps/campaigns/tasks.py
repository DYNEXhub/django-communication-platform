"""
Celery tasks for campaigns app.
Handles campaign execution and metrics updates.
"""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def process_campaign(self, campaign_id):
    """
    Process and send a campaign to all recipients.

    Args:
        campaign_id: UUID of the Campaign to process

    Returns:
        dict: Campaign execution summary
    """
    from apps.campaigns.models import Campaign
    from apps.communications.models import EmailMessage, SMSMessage, WhatsAppMessage
    from apps.communications.tasks import send_email_task, send_sms_task, send_whatsapp_task
    from django.utils import timezone

    try:
        campaign = Campaign.objects.select_related('template', 'channel').get(id=campaign_id)

        if campaign.status != 'RUNNING':
            logger.warning(f"Campaign {campaign_id} is not in RUNNING status, skipping")
            return {'status': 'skipped', 'campaign_id': str(campaign_id)}

        # Collect all unique contacts from all segments
        contacts = set()
        for segment in campaign.segments.prefetch_related('contacts').all():
            contacts.update(segment.contacts.filter(status='ACTIVE'))

        campaign.total_recipients = len(contacts)
        campaign.save(update_fields=['total_recipients'])

        logger.info(f"Processing campaign {campaign.name} for {len(contacts)} recipients")

        # Send messages based on campaign type
        for contact in contacts:
            if campaign.campaign_type == 'EMAIL':
                msg = EmailMessage.objects.create(
                    channel=campaign.channel,
                    contact=contact,
                    subject=campaign.template.subject or campaign.template.name,
                    body_html=campaign.template.content,
                    status='QUEUED',
                )
                send_email_task.delay(str(msg.id))

            elif campaign.campaign_type == 'SMS':
                msg = SMSMessage.objects.create(
                    channel=campaign.channel,
                    contact=contact,
                    body=campaign.template.content,
                    status='QUEUED',
                )
                send_sms_task.delay(str(msg.id))

            elif campaign.campaign_type == 'WHATSAPP':
                msg = WhatsAppMessage.objects.create(
                    channel=campaign.channel,
                    contact=contact,
                    body=campaign.template.content,
                    template_name=campaign.template.name,
                    status='QUEUED',
                )
                send_whatsapp_task.delay(str(msg.id))

            campaign.sent_count += 1
            campaign.save(update_fields=['sent_count'])

        # Mark campaign as completed
        campaign.status = 'COMPLETED'
        campaign.completed_at = timezone.now()
        campaign.save(update_fields=['status', 'completed_at'])

        logger.info(f"Campaign {campaign.name} completed: {campaign.sent_count} messages sent")

        return {
            'status': 'completed',
            'campaign_id': str(campaign_id),
            'recipients': campaign.total_recipients,
            'sent': campaign.sent_count
        }

    except Campaign.DoesNotExist:
        logger.error(f"Campaign {campaign_id} not found")
        return {'status': 'error', 'message': 'Campaign not found'}
    except Exception as exc:
        logger.error(f"Campaign processing failed for {campaign_id}: {exc}")
        return {'status': 'error', 'message': str(exc)}


@shared_task
def update_campaign_metrics(campaign_id):
    """
    Recalculate campaign metrics from actual message data.

    Args:
        campaign_id: UUID of the Campaign to update

    Returns:
        dict: Updated metrics
    """
    from apps.campaigns.models import Campaign
    from apps.communications.models import EmailMessage
    from django.db.models import Count, Q

    try:
        campaign = Campaign.objects.get(id=campaign_id)

        if campaign.campaign_type == 'EMAIL':
            # Calculate metrics from EmailMessage records
            # This assumes messages are linked to campaign via created_at timestamp and channel
            metrics = EmailMessage.objects.filter(
                channel=campaign.channel,
                created_at__gte=campaign.started_at or campaign.created_at,
            ).aggregate(
                total=Count('id'),
                opened=Count('id', filter=Q(opened=True)),
                clicked=Count('id', filter=Q(clicked=True)),
                bounced=Count('id', filter=Q(status='BOUNCED')),
            )

            campaign.sent_count = metrics['total']
            campaign.open_count = metrics['opened']
            campaign.click_count = metrics['clicked']
            campaign.bounce_count = metrics['bounced']
            campaign.save(update_fields=[
                'sent_count', 'open_count', 'click_count',
                'bounce_count', 'updated_at'
            ])

            logger.info(f"Campaign metrics updated for {campaign.name}: "
                       f"sent={metrics['total']}, opened={metrics['opened']}, "
                       f"clicked={metrics['clicked']}, bounced={metrics['bounced']}")

            return {
                'campaign_id': str(campaign_id),
                'metrics': metrics
            }
        else:
            # For SMS and WhatsApp, metrics are simpler
            logger.info(f"Metrics update skipped for non-email campaign {campaign.name}")
            return {
                'campaign_id': str(campaign_id),
                'status': 'skipped',
                'reason': 'Non-email campaign'
            }

    except Campaign.DoesNotExist:
        logger.error(f"Campaign {campaign_id} not found for metrics update")
        return {'status': 'error', 'message': 'Campaign not found'}
    except Exception as exc:
        logger.error(f"Campaign metrics update failed for {campaign_id}: {exc}")
        return {'status': 'error', 'message': str(exc)}
