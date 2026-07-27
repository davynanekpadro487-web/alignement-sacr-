from django.db import models


class Inscription(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('validee', 'Validée'),
        ('refusee', 'Refusée'),
    ]

    nom_complet = models.CharField(max_length=255, verbose_name="Nom complet")
    telephone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(verbose_name="Email")
    capture_paiement = models.FileField(
        upload_to='captures_paiement/',
        verbose_name="Capture de paiement",
        null=True,
        blank=True,
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente',
        verbose_name="Statut",
    )
    date_validation = models.DateTimeField(null=True, blank=True, verbose_name="Date de validation")
    certificat_envoye = models.BooleanField(default=False, verbose_name="Certificat envoyé")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")

    class Meta:
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.nom_complet} — {self.get_statut_display()}"
