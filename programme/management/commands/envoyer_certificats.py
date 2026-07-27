import os
import io
from datetime import timedelta
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import EmailMessage
from programme.models import Inscription

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.colors import HexColor
from reportlab.lib.units import cm

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Génère et envoie les certificats pour les inscriptions validées depuis 6 semaines (42 jours)"

    def handle(self, *args, **options):
        target_date = timezone.now().date() - timedelta(days=42)
        inscriptions = Inscription.objects.filter(
            statut='validee',
            certificat_envoye=False,
            date_validation__date=target_date
        )

        if not inscriptions.exists():
            self.stdout.write("Aucune inscription éligible pour un certificat aujourd'hui.")
            return

        for inscription in inscriptions:
            try:
                pdf_buffer = self.generate_certificate(inscription)
                self.send_email(inscription, pdf_buffer)
                
                # Marquer comme envoyé
                inscription.certificat_envoye = True
                inscription.save(update_fields=['certificat_envoye'])
                
                self.stdout.write(self.style.SUCCESS(f"Certificat envoyé à {inscription.nom_complet}"))
            except Exception as e:
                logger.error(f"Échec de l'envoi du certificat à {inscription.nom_complet}: {e}")
                self.stdout.write(self.style.ERROR(f"Échec pour {inscription.nom_complet}: {e}"))

    def generate_certificate(self, inscription):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=landscape(A4))
        width, height = landscape(A4)

        # Couleurs: #0f2a4a (marine), #3f7de0 (azur), #eaf2fd (blanc/bleu très clair)
        c.setFillColor(HexColor('#0f2a4a'))
        c.rect(0, 0, width, height, fill=1)

        c.setFillColor(HexColor('#eaf2fd'))
        c.rect(20, 20, width - 40, height - 40, fill=1)

        c.setFillColor(HexColor('#3f7de0'))
        c.rect(25, 25, width - 50, height - 50, fill=0, stroke=1)

        # Textes
        c.setFillColor(HexColor('#0f2a4a'))
        c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(width / 2.0, height - 100, "CERTIFICAT D'ACCOMPLISSEMENT")

        c.setFont("Helvetica", 18)
        c.drawCentredString(width / 2.0, height - 160, "Ce certificat est décerné à")

        c.setFont("Helvetica-Bold", 28)
        c.setFillColor(HexColor('#3f7de0'))
        c.drawCentredString(width / 2.0, height - 210, inscription.nom_complet.upper())

        c.setFont("Helvetica", 16)
        c.setFillColor(HexColor('#0f2a4a'))
        c.drawCentredString(width / 2.0, height - 260, "pour avoir complété avec succès le")
        
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width / 2.0, height - 300, "Programme Alignement Sacré")

        c.setFont("Helvetica-Oblique", 14)
        c.drawCentredString(width / 2.0, height - 330, "Corps • Âme • Destinée")

        date_fin_str = (inscription.date_validation + timedelta(days=42)).strftime('%d/%m/%Y')
        c.setFont("Helvetica", 14)
        c.drawCentredString(width / 2.0, height - 380, f"Abidjan, le {date_fin_str}")

        # Signature
        c.setFont("Helvetica-Bold", 16)
        c.drawString(width - 250, 80, "Coach Farah Barbour")
        c.setFont("Helvetica", 12)
        c.drawString(width - 250, 60, "Fondatrice, Jardin de Farah")

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer.getvalue()

    def send_email(self, inscription, pdf_bytes):
        subject = "Félicitations ! Votre certificat Alignement Sacré"
        body = f"Bonjour {inscription.nom_complet},\n\nFélicitations pour avoir complété le Programme Alignement Sacré !\nTu trouveras en pièce jointe ton certificat d'accomplissement.\n\nAvec toute notre bienveillance,\nL'équipe Jardin de Farah"
        
        email = EmailMessage(
            subject=subject,
            body=body,
            to=[inscription.email],
        )
        email.attach(f"Certificat_{inscription.nom_complet.replace(' ', '_')}.pdf", pdf_bytes, 'application/pdf')
        email.send(fail_silently=False)
