import re
import magic
from django import forms
from .models import Inscription


class InscriptionForm(forms.Form):
    """Étape 1 : informations personnelles (pas encore enregistré en base)."""

    nom_complet = forms.CharField(
        max_length=255,
        label="Nom complet",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre nom et prénom',
            'id': 'nom_complet',
        }),
    )
    telephone = forms.CharField(
        max_length=20,
        label="Numéro de téléphone",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex : 0712345678',
            'id': 'telephone',
            'type': 'tel',
        }),
    )
    email = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'votre.email@exemple.com',
            'id': 'email',
        }),
    )

    def clean_nom_complet(self):
        nom = self.cleaned_data['nom_complet'].strip()
        if len(nom) < 2:
            raise forms.ValidationError("Le nom doit contenir au moins 2 caractères.")
        return nom

    def clean_telephone(self):
        telephone = self.cleaned_data['telephone'].strip()
        telephone = re.sub(r'\s+', '', telephone)
        if not re.match(r'^\d{10}$', telephone):
            raise forms.ValidationError(
                "Le numéro doit contenir exactement 10 chiffres (format ivoirien)."
            )
        return telephone


class PaiementForm(forms.Form):
    """Étape 2 : upload de la preuve de paiement."""

    EXTENSIONS_AUTORISEES = ['jpg', 'jpeg', 'png', 'pdf']
    TAILLE_MAX = 5 * 1024 * 1024  # 5 Mo

    capture_paiement = forms.FileField(
        label="Capture d'écran du paiement",
        widget=forms.ClearableFileInput(attrs={
            'id': 'capture_paiement',
            'accept': '.jpg,.jpeg,.png,.pdf',
        }),
    )

    def clean_capture_paiement(self):
        fichier = self.cleaned_data['capture_paiement']

        # Vérification de la taille
        if fichier.size > self.TAILLE_MAX:
            raise forms.ValidationError(
                f"Le fichier est trop volumineux ({fichier.size // (1024*1024)} Mo). "
                f"La taille maximale autorisée est de 5 Mo."
            )

        # Vérification de l'extension nominale
        nom = fichier.name.lower()
        extension = nom.rsplit('.', 1)[-1] if '.' in nom else ''
        if extension not in self.EXTENSIONS_AUTORISEES:
            raise forms.ValidationError(
                "Format d'extension non autorisé. Seuls les fichiers JPG, PNG et PDF sont acceptés."
            )

        # Vérification de sécurité du vrai type MIME (Magic bytes)
        content_types_autorises = [
            'image/jpeg', 'image/png', 'application/pdf',
        ]
        
        # Lire les premiers octets pour déterminer le vrai type
        fichier.seek(0)
        file_header = fichier.read(2048)
        fichier.seek(0)  # Remettre le curseur au début pour Django
        
        mime_type = magic.from_buffer(file_header, mime=True)
        
        if mime_type not in content_types_autorises:
            raise forms.ValidationError(
                f"Fichier invalide ou corrompu (Type détecté: {mime_type})."
            )

        return fichier
