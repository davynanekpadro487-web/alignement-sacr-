from django.contrib import admin
from django.utils.html import format_html
from .models import Inscription


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ('nom_complet', 'telephone', 'email', 'statut', 'date_validation', 'certificat_envoye', 'date_creation')
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
