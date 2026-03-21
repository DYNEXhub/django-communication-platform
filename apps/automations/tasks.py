"""
Celery tasks for automations app.
Handles automation execution and webhook delivery.
"""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def execute_automation(automation_id, trigger_data):
    """
    Execute automation actions based on trigger.

    Args:
        automation_id: UUID of the Automation to execute
        trigger_data: Dict containing trigger event data

    Returns:
        dict: Execution summary
    """
    from apps.automations.models import Automation, AutomationLog
    from django.utils import timezone
    import time

    try:
        automation = Automation.objects.get(id=automation_id, is_active=True)
        start_time = time.time()
        actions_executed = []
        status = 'SUCCESS'
        error_message = ''

        logger.info(f"Executing automation: {automation.name}")

        # Execute each action in the automation
        for action in automation.actions:
            try:
                action_type = action.get('type', '')
                action_params = action.get('params', {})

                # TODO: Implement actual action execution logic
                # Example actions:
                # - send_email: Send email to contact
                # - add_tag: Add tag to contact
                # - update_field: Update custom field
                # - create_deal: Create a deal
                # - send_webhook: Trigger webhook

                actions_executed.append({
                    'type': action_type,
                    'params': action_params,
                    'status': 'executed',
                    'timestamp': timezone.now().isoformat()
                })

                logger.debug(f"Action executed: {action_type}")

            except Exception as e:
                actions_executed.append({
                    'type': action.get('type', ''),
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': timezone.now().isoformat()
                })
                status = 'PARTIAL'
                error_message = str(e)
                logger.warning(f"Action failed: {action.get('type', '')} - {e}")

        execution_time = int((time.time() - start_time) * 1000)

        # Create execution log
        AutomationLog.objects.create(
            automation=automation,
            trigger_data=trigger_data,
            actions_executed=actions_executed,
            status=status,
            error_message=error_message,
            execution_time_ms=execution_time,
        )

        # Update automation metrics
        automation.execution_count += 1
        automation.last_executed_at = timezone.now()
        automation.save(update_fields=['execution_count', 'last_executed_at'])

        logger.info(f"Automation {automation.name} executed: {status} in {execution_time}ms")

        return {
            'automation_id': str(automation_id),
            'status': status,
            'actions_count': len(actions_executed),
            'execution_time_ms': execution_time
        }

    except Automation.DoesNotExist:
        logger.warning(f"Automation {automation_id} not found or inactive")
        return {'status': 'error', 'message': 'Automation not found or inactive'}
    except Exception as exc:
        logger.error(f"Automation execution failed for {automation_id}: {exc}")
        return {'status': 'error', 'message': str(exc)}


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def deliver_webhook(self, webhook_id, event, payload):
    """
    Deliver webhook to external URL.

    Args:
        webhook_id: UUID of the Webhook to deliver
        event: Event name that triggered the webhook
        payload: Dict containing event payload

    Returns:
        dict: Delivery summary
    """
    from apps.automations.models import Webhook, WebhookDelivery
    from django.utils import timezone
    import hashlib
    import hmac
    import json
    import urllib.request
    import urllib.error

    try:
        webhook = Webhook.objects.get(id=webhook_id, is_active=True)

        logger.info(f"Delivering webhook: {webhook.name} for event {event}")

        # Prepare request body
        body = json.dumps({'event': event, 'data': payload}).encode('utf-8')
        headers = {'Content-Type': 'application/json'}

        # Add signature if secret is configured
        if webhook.secret:
            signature = hmac.new(
                webhook.secret.encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            headers['X-Webhook-Signature'] = signature
            logger.debug(f"Webhook signature generated for {webhook.name}")

        # Make HTTP request
        req = urllib.request.Request(
            webhook.url,
            data=body,
            headers=headers,
            method='POST'
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                response_status = response.status
                response_body = response.read().decode('utf-8')[:1000]
                success = 200 <= response_status < 300

        except urllib.error.HTTPError as e:
            response_status = e.code
            response_body = str(e.reason)
            success = False

        except urllib.error.URLError as e:
            response_status = 0
            response_body = str(e.reason)
            success = False

        # Create delivery record
        WebhookDelivery.objects.create(
            webhook=webhook,
            event=event,
            payload=payload,
            response_status=response_status,
            response_body=response_body,
            success=success,
        )

        # Update webhook metrics
        if success:
            webhook.failure_count = 0
            logger.info(f"Webhook delivered successfully: {webhook.name} ({response_status})")
        else:
            webhook.failure_count += 1
            logger.warning(f"Webhook delivery failed: {webhook.name} ({response_status})")

        webhook.last_triggered_at = timezone.now()
        webhook.save(update_fields=['failure_count', 'last_triggered_at'])

        # Raise exception if delivery failed (will trigger retry)
        if not success:
            raise Exception(f"Webhook delivery failed: {response_status}")

        return {
            'webhook_id': str(webhook_id),
            'event': event,
            'status': response_status,
            'success': success
        }

    except Webhook.DoesNotExist:
        logger.warning(f"Webhook {webhook_id} not found or inactive")
        return {'status': 'error', 'message': 'Webhook not found or inactive'}
    except Exception as exc:
        logger.error(f"Webhook delivery error for {webhook_id}: {exc}")
        raise self.retry(exc=exc)
