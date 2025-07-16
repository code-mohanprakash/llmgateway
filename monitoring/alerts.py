"""
Alerting system for Model Bridge
"""
import os
import smtplib
import json
from datetime import datetime, timedelta
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

# Email configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
ALERT_FROM_EMAIL = os.getenv("ALERT_FROM_EMAIL", SMTP_USERNAME)


class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    USAGE_LIMIT_EXCEEDED = "usage_limit_exceeded"
    PROVIDER_DOWN = "provider_down"
    HIGH_ERROR_RATE = "high_error_rate"
    HIGH_COST = "high_cost"
    PAYMENT_FAILED = "payment_failed"
    SYSTEM_ERROR = "system_error"


@dataclass
class Alert:
    type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    organization_id: str
    metadata: Dict[str, Any]
    created_at: datetime


class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self):
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
    
    async def trigger_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        message: str,
        organization_id: str,
        metadata: Dict[str, Any] = None
    ):
        """Trigger a new alert"""
        
        alert = Alert(
            type=alert_type,
            severity=severity,
            title=title,
            message=message,
            organization_id=organization_id,
            metadata=metadata or {},
            created_at=datetime.utcnow()
        )
        
        # Generate alert ID
        alert_id = f"{alert_type.value}_{organization_id}_{int(alert.created_at.timestamp())}"
        
        # Store alert
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Send notifications
        await self._send_notifications(alert)
        
        return alert_id
    
    async def resolve_alert(self, alert_id: str):
        """Mark alert as resolved"""
        if alert_id in self.active_alerts:
            del self.active_alerts[alert_id]
    
    async def _send_notifications(self, alert: Alert):
        """Send alert notifications"""
        
        # Send email notification
        if alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
            await self._send_email_alert(alert)
        
        # Send webhook notification (if configured)
        await self._send_webhook_alert(alert)
        
        # Log alert
        print(f"ALERT [{alert.severity.value.upper()}] {alert.title}: {alert.message}")
    
    async def _send_email_alert(self, alert: Alert):
        """Send email alert"""
        try:
            # Get organization admin emails
            admin_emails = await self._get_admin_emails(alert.organization_id)
            
            if not admin_emails:
                return
            
            # Create email
            msg = MimeMultipart()
            msg['From'] = ALERT_FROM_EMAIL
            msg['To'] = ", ".join(admin_emails)
            msg['Subject'] = f"[Model Bridge Alert] {alert.title}"
            
            # Email body
            body = f"""
Alert Details:
- Type: {alert.type.value}
- Severity: {alert.severity.value.upper()}
- Organization: {alert.organization_id}
- Time: {alert.created_at.isoformat()}

Message:
{alert.message}

Metadata:
{json.dumps(alert.metadata, indent=2)}

---
Model Bridge Alert System
            """.strip()
            
            msg.attach(MimeText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            print(f"Failed to send email alert: {e}")
    
    async def _send_webhook_alert(self, alert: Alert):
        """Send webhook alert (placeholder)"""
        # Implement webhook notifications here
        pass
    
    async def _get_admin_emails(self, organization_id: str) -> List[str]:
        """Get admin email addresses for organization"""
        # This would query the database for admin users
        # Placeholder implementation
        return []
    
    def get_active_alerts(self, organization_id: str = None) -> List[Alert]:
        """Get active alerts"""
        alerts = list(self.active_alerts.values())
        
        if organization_id:
            alerts = [a for a in alerts if a.organization_id == organization_id]
        
        return sorted(alerts, key=lambda x: x.created_at, reverse=True)
    
    def get_alert_history(self, organization_id: str = None, hours: int = 24) -> List[Alert]:
        """Get alert history"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        alerts = [a for a in self.alert_history if a.created_at >= cutoff]
        
        if organization_id:
            alerts = [a for a in alerts if a.organization_id == organization_id]
        
        return sorted(alerts, key=lambda x: x.created_at, reverse=True)


# Global alert manager
alert_manager = AlertManager()


# Convenience functions
async def alert_rate_limit_exceeded(organization_id: str, limit_type: str, current_usage: int, limit: int):
    """Alert for rate limit exceeded"""
    await alert_manager.trigger_alert(
        AlertType.RATE_LIMIT_EXCEEDED,
        AlertSeverity.MEDIUM,
        "Rate Limit Exceeded",
        f"Rate limit exceeded for {limit_type}. Current usage: {current_usage}, Limit: {limit}",
        organization_id,
        {"limit_type": limit_type, "current_usage": current_usage, "limit": limit}
    )


async def alert_usage_limit_exceeded(organization_id: str, usage_type: str, current_usage: int, limit: int):
    """Alert for usage limit exceeded"""
    await alert_manager.trigger_alert(
        AlertType.USAGE_LIMIT_EXCEEDED,
        AlertSeverity.HIGH,
        "Usage Limit Exceeded",
        f"Monthly {usage_type} limit exceeded. Current usage: {current_usage}, Limit: {limit}",
        organization_id,
        {"usage_type": usage_type, "current_usage": current_usage, "limit": limit}
    )


async def alert_provider_down(provider: str, organization_id: str = "system"):
    """Alert for provider being down"""
    await alert_manager.trigger_alert(
        AlertType.PROVIDER_DOWN,
        AlertSeverity.HIGH,
        "Provider Down",
        f"Provider {provider} is currently unavailable",
        organization_id,
        {"provider": provider}
    )


async def alert_high_error_rate(organization_id: str, error_rate: float, threshold: float = 0.1):
    """Alert for high error rate"""
    await alert_manager.trigger_alert(
        AlertType.HIGH_ERROR_RATE,
        AlertSeverity.MEDIUM,
        "High Error Rate",
        f"Error rate is {error_rate:.2%}, above threshold of {threshold:.2%}",
        organization_id,
        {"error_rate": error_rate, "threshold": threshold}
    )


async def alert_payment_failed(organization_id: str, amount: float):
    """Alert for payment failure"""
    await alert_manager.trigger_alert(
        AlertType.PAYMENT_FAILED,
        AlertSeverity.CRITICAL,
        "Payment Failed",
        f"Payment of ${amount:.2f} failed for your organization",
        organization_id,
        {"amount": amount}
    )