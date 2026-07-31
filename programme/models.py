import os
import uuid
from django.db import models

def capture_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('captures_paiement/', filename)

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
        upload_to=capture_upload_path,
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
    date_envoi_certificat = models.DateTimeField(null=True, blank=True, verbose_name="Date d'envoi du certificat")
    fichier_certificat = models.FileField(upload_to='certificats/', null=True, blank=True, verbose_name="Fichier du certificat PDF")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")

    @property
    def jours_restants_certificat(self):
        if self.statut != 'validee' or not self.date_validation:
            return None
        if self.certificat_envoye:
            return 0
        from datetime import timedelta
        from django.utils import timezone
        
        date_cible = self.date_validation + timedelta(days=42)
        restant = (date_cible - timezone.now()).days
        return max(0, restant)

    @property
    def whatsapp_link_number(self):
        import re
        # Garder uniquement les chiffres
        num = re.sub(r'\D', '', str(self.telephone))
        
        # Corriger les doubles indicatifs (ex: utilisateur tape +225 00225 ou 225225)
        if num.startswith('22500225'):
            num = '225' + num[8:]
        elif num.startswith('225225'):
            num = '225' + num[6:]
            
        # Pour la Côte d'Ivoire (225), si le numéro total fait 12 chiffres (225 + 9 chiffres),
        # c'est que le 0 initial a été supprimé par erreur par le JS ou l'utilisateur.
        # En CI, les numéros ont 10 chiffres et commencent par 01, 05, 07.
        if num.startswith('225') and len(num) == 12:
            local_part = num[3:]
            if local_part.startswith(('1', '5', '7')):
                num = '2250' + local_part
                
        return num

    class Meta:
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.nom_complet} — {self.get_statut_display()}"

    def save(self, *args, **kwargs):
        send_email = False
        if self.pk:
            try:
                old_instance = Inscription.objects.get(pk=self.pk)
                if old_instance.statut == 'en_attente' and self.statut == 'validee':
                    send_email = True
            except Inscription.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)

        if send_email:
            self._envoyer_email_validation()

    def _envoyer_email_validation(self):
        from django.core.mail import EmailMessage
        from django.conf import settings
        
        lien_groupe = "https://chat.whatsapp.com/DSdV75oTwlBBTLOePGpGpU?s=cl&p=i&mlu=0&ilr=0"
        try:
            EmailMessage(
                subject="Bienvenue dans le Programme Alignement Sacré",
                body=f"Bonjour {self.nom_complet},\n\nFélicitations pour ton inscription !\n\nTon paiement a été validé avec succès. Tu peux dès à présent rejoindre notre groupe privé WhatsApp en cliquant sur ce lien : {lien_groupe}\n\nÀ très vite pour le début du programme,\nL'équipe Jardin de Farah",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[self.email]
            ).send(fail_silently=False)
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email : {e}")
