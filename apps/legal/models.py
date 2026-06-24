from django.db import models


class WiderrufRequest(models.Model):
    """
    Records a customer's right-of-withdrawal (Widerruf) declaration under § 356a BGB.

    LEGAL: The withdrawal period can extend to 12 months + 14 days. If a dispute
    arises up to a year later, this timestamped record is our proof that the
    customer did / did not submit a withdrawal, and exactly when. created_at is
    the legally critical evidence field.
    """
    name = models.CharField(max_length=200)
    email = models.EmailField()
    bestellnummer = models.CharField(max_length=100)
    widerrufserklaerung = models.TextField(blank=True)

    # Legal evidence
    created_at = models.DateTimeField(auto_now_add=True)
    confirmation_sent = models.BooleanField(default=False)

    # Optional evidence hardening
    raw_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Widerruf — {self.name} — {self.bestellnummer} — {self.created_at:%Y-%m-%d %H:%M}"
