import urllib.parse
from django.contrib import admin
from django.utils.html import format_html
from .models import Inscription


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ('nom_complet', 'telephone', 'email', 'statut', 'action_whatsapp', 'date_validation', 'certificat_envoye', 'date_creation')
    list_filter = ('statut', 'certificat_envoye', 'date_creation')
    search_fields = ('nom_complet', 'telephone', 'email')
    list_editable = ('statut', 'certificat_envoye')
    date_hierarchy = 'date_creation'
    ordering = ('-date_creation',)
    readonly_fields = ('date_creation', 'capture_paiement_preview')

    fieldsets = (
        ('Informations personnelles', {
            'fields': ('nom_complet', 'telephone', 'email'),
        }),
        ('Paiement', {
            'fields': ('capture_paiement', 'capture_paiement_preview', 'statut'),
        }),
        ('Certification et Dates', {
            'fields': ('date_validation', 'certificat_envoye', 'date_creation'),
        }),
    )

    def action_whatsapp(self, obj):
        if obj.statut == 'validee' and obj.telephone:
            numero = obj.whatsapp_link_number
            lien_groupe = "https://chat.whatsapp.com/DSdV75oTwlBBTLOePGpGpU?s=cl&p=i&mlu=0&ilr=0"
            message = f"Bonjour {obj.nom_complet}, ton inscription au programme Alignement Sacré est validée ! Rejoins le groupe WhatsApp ici : {lien_groupe}"
            message_encoded = urllib.parse.quote(message)
            url = f"https://wa.me/{numero}?text={message_encoded}"
            
            return format_html(
                '<a class="button" href="{}" target="_blank" style="background-color: #25D366; color: white; border: none; padding: 5px 10px; border-radius: 4px; font-weight: bold; text-decoration: none;">WhatsApp</a>',
                url
            )
        return "-"
    action_whatsapp.short_description = "WhatsApp"

    def capture_paiement_preview(self, obj):
        if obj.capture_paiement:
            url = obj.capture_paiement.url
            if url.lower().endswith(('.jpg', '.jpeg', '.png')):
                return format_html(
                    '<a href="{}" target="_blank">'
                    '<img src="{}" style="max-height:200px; border-radius:8px;" />'
                    '</a>',
                    url, url,
                )
            return format_html(
                '<a href="{}" target="_blank">📄 Voir le fichier PDF</a>',
                url,
            )
        return "Aucun fichier"
    capture_paiement_preview.short_description = "Aperçu de la capture"
