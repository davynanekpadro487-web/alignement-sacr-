import os
import io
from datetime import timedelta
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import EmailMessage
from django.core.files.base import ContentFile
from programme.models import Inscription

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.colors import HexColor
from reportlab.lib.units import cm

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Génère et envoie les certificats pour les inscriptions validées depuis 6 semaines (42 jours)"

    def handle(self, *args, **options):
        # 6 semaines = 42 jours
        target_date = timezone.now() - timedelta(days=42)
        inscriptions = Inscription.objects.filter(
            statut='validee',
            certificat_envoye=False,
            date_validation__lte=target_date
        )

        if not inscriptions.exists():
            self.stdout.write("Aucune inscription éligible pour un certificat aujourd'hui.")
            return

        for inscription in inscriptions:
            try:
                pdf_bytes = self.generate_certificate(inscription)
                
                # Sauvegarde du fichier PDF dans le modèle
                file_name = f"Certificat_{inscription.nom_complet.replace(' ', '_')}.pdf"
                inscription.fichier_certificat.save(file_name, ContentFile(pdf_bytes), save=False)
                
                self.send_email(inscription, pdf_bytes, file_name)
                
                # Marquer comme envoyé
                inscription.certificat_envoye = True
                inscription.date_envoi_certificat = timezone.now()
                inscription.save(update_fields=['certificat_envoye', 'date_envoi_certificat', 'fichier_certificat'])
                
                self.stdout.write(self.style.SUCCESS(f"Certificat envoyé et enregistré pour {inscription.nom_complet}"))
            except Exception as e:
                logger.error(f"Échec de l'envoi du certificat à {inscription.nom_complet}: {e}")
                self.stdout.write(self.style.ERROR(f"Échec pour {inscription.nom_complet}: {e}"))

    def generate_certificate(self, inscription):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=landscape(A4))
        width, height = landscape(A4)

        # Couleurs
        bg_color = HexColor('#fdfbf6')
        teal = HexColor('#164b4f')
        gold = HexColor('#c9a227')
        gray = HexColor('#4b5563')

        # Fond crème
        c.setFillColor(bg_color)
        c.rect(0, 0, width, height, fill=1, stroke=0)

        # Cadre Extérieur Teal (épaisseur 2.2)
        c.setStrokeColor(teal)
        c.setLineWidth(2.2)
        c.rect(15, 15, width - 30, height - 30, fill=0, stroke=1)

        # Cadre Intérieur Doré (épaisseur 1)
        c.setStrokeColor(gold)
        c.setLineWidth(1)
        inner_margin = 25
        c.rect(inner_margin, inner_margin, width - 50, height - 50, fill=0, stroke=1)

        # 4 losanges dorés
        def draw_diamond(cx, cy, size=4):
            c.setFillColor(gold)
            path = c.beginPath()
            path.moveTo(cx, cy + size)
            path.lineTo(cx + size, cy)
            path.lineTo(cx, cy - size)
            path.lineTo(cx - size, cy)
            path.close()
            c.drawPath(path, fill=1, stroke=0)
            
        draw_diamond(inner_margin, inner_margin)
        draw_diamond(width - inner_margin, inner_margin)
        draw_diamond(inner_margin, height - inner_margin)
        draw_diamond(width - inner_margin, height - inner_margin)

        # Kicker "J A R D I N D E F A R A H"
        c.setFillColor(gold)
        c.setFont("Helvetica-Bold", 13)
        kicker_text = "J A R D I N   D E   F A R A H"
        c.drawCentredString(width / 2.0, height - 80, kicker_text)
        # petite ligne dorée horizontale
        c.setStrokeColor(gold)
        c.setLineWidth(1)
        c.line(width / 2.0 - 55, height - 95, width / 2.0 + 55, height - 95)

        # Titre centré : "Certificat de Réussite"
        c.setFillColor(teal)
        c.setFont("Times-Bold", 40)
        c.drawCentredString(width / 2.0, height - 150, "Certificat de Réussite")

        # Sous-titre centré, italique doré
        c.setFillColor(gold)
        c.setFont("Times-Italic", 16)
        c.drawCentredString(width / 2.0, height - 195, "Programme Alignement Sacré · Corps • Âme • Destinée")

        # Texte centré : "Ceci certifie que"
        c.setFillColor(teal)
        c.setFont("Times-Roman", 15)
        c.drawCentredString(width / 2.0, height - 250, "Ceci certifie que")

        # Nom complet
        name = inscription.nom_complet.title()
        c.setFont("Times-Bold", 34)
        c.setFillColor(teal)
        c.drawCentredString(width / 2.0, height - 310, name)
        
        # Trait doré souligné sous le nom (largeur + 24mm, min 80mm)
        text_width = c.stringWidth(name, "Times-Bold", 34)
        mm = 2.83465
        line_width = max(text_width + (24 * mm), 80 * mm)
        c.setStrokeColor(gold)
        c.setLineWidth(1.5)
        c.line(width / 2.0 - line_width / 2.0, height - 325, width / 2.0 + line_width / 2.0, height - 325)

        # Corps de texte centré
        c.setFillColor(gray)
        c.setFont("Times-Roman", 15)
        # 9mm spacing = ~25.5 points
        c.drawCentredString(width / 2.0, height - 375, "a suivi avec engagement les 6 semaines du programme Alignement Sacré,")
        c.drawCentredString(width / 2.0, height - 400.5, "dédié à l'élévation du corps, de l'âme et de la destinée,")
        c.drawCentredString(width / 2.0, height - 426, "et a mené ce parcours de transformation intérieure jusqu'à son terme.")

        # Signatures
        date_envoi_str = timezone.now().strftime('%d/%m/%Y')
        
        c.setFont("Times-Roman", 12)
        c.setFillColor(teal)
        c.drawString(100, 100, "Date de délivrance")
        c.drawString(100, 80, date_envoi_str)

        c.setFont("Times-Bold", 14)
        c.drawString(width - 320, 100, "Coach Farah Barbour Nekpadro")
        c.setFont("Times-Roman", 11)
        c.setFillColor(gold)
        c.drawString(width - 320, 80, "Fondatrice, Jardin de Farah")

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer.getvalue()

    def send_email(self, inscription, pdf_bytes, file_name):
        subject = "Félicitations ! Votre certificat Alignement Sacré"
        body = f"Bonjour {inscription.nom_complet},\n\nFélicitations pour avoir complété le Programme Alignement Sacré !\nTu trouveras en pièce jointe ton certificat d'accomplissement.\n\nAvec toute notre bienveillance,\nL'équipe Jardin de Farah"
        
        email = EmailMessage(
            subject=subject,
            body=body,
            to=[inscription.email],
        )
        email.attach(file_name, pdf_bytes, 'application/pdf')
        email.send(fail_silently=False)
