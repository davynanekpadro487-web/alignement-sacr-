from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django_ratelimit.decorators import ratelimit

from .models import Inscription
from .forms import InscriptionForm, PaiementForm


def accueil(request):
    return render(request, 'programme/index.html')


@ratelimit(key='ip', rate='5/h', method='POST', block=True)
def inscription(request):
    """Étape 1 : formulaire d'informations personnelles."""
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            # Sauvegarder les données en session au lieu de la BDD pour le moment
            request.session['inscription_data'] = {
                'nom_complet': form.cleaned_data['nom_complet'],
                'telephone': form.cleaned_data['telephone'],
                'email': form.cleaned_data['email']
            }
            return redirect('paiement')
    else:
        form = InscriptionForm()
    return render(request, 'programme/inscription.html', {'form': form})

def paiement(request):
    """Étape 2 : instructions de paiement et upload de la preuve."""
    # Vérifier que l'étape 1 a bien été validée
    inscription_data = request.session.get('inscription_data')
    if not inscription_data:
        messages.error(request, "Veuillez remplir vos informations personnelles avant de procéder au paiement.")
        return redirect('inscription')

    if request.method == 'POST':
        form = PaiementForm(request.POST, request.FILES)
        if form.is_valid():
            # Créer l'inscription finale
            nouvelle_inscription = Inscription(
                nom_complet=inscription_data['nom_complet'],
                telephone=inscription_data['telephone'],
                email=inscription_data['email'],
                capture_paiement=form.cleaned_data['capture_paiement'],
                statut='en_attente'
            )
            nouvelle_inscription.save()
            
            # Nettoyer la session
            del request.session['inscription_data']
            return redirect('confirmation')
    else:
        form = PaiementForm()

    return render(request, 'programme/paiement.html', {
        'form': form,
        'nom': inscription_data['nom_complet'].split()[0] # prénom
    })


def confirmation(request):
    """Page de confirmation après inscription complète."""
    return render(request, 'programme/confirmation.html')


# ─── Vues Dashboard (Protégées) ───

@staff_member_required
def dashboard(request):
    """Tableau de bord personnalisé pour l'admin / staff."""
    inscriptions = Inscription.objects.all().order_by('-date_creation')
    return render(request, 'programme/dashboard.html', {'inscriptions': inscriptions})


@staff_member_required
def dashboard_action(request, inscription_id, action):
    """Action de validation/refus pour une inscription depuis le dashboard."""
    if request.method == 'POST':
        inscription_obj = get_object_or_404(Inscription, id=inscription_id)
        if action == 'valider':
            inscription_obj.statut = 'validee'
            inscription_obj.save()
            
            # Envoi d'email avec le lien WhatsApp
            try:
                from django.core.mail import EmailMessage
                EmailMessage(
                    subject="Bienvenue dans le Programme Alignement Sacré",
                    body=f"Bonjour {inscription_obj.nom_complet},\n\nFélicitations pour ton inscription !\n\nTon paiement a été validé avec succès. Tu peux dès à présent rejoindre notre groupe privé WhatsApp en cliquant sur ce lien : https://chat.whatsapp.com/DSdV75oTwlBBTLOePGpGpU\n\nÀ très vite pour le début du programme,\nL'équipe Jardin de Farah",
                    to=[inscription_obj.email]
                ).send(fail_silently=True)
            except Exception:
                pass
                
            messages.success(request, f"L'inscription de {inscription_obj.nom_complet} a été validée et l'email a été envoyé.")
        elif action == 'refuser':
            inscription_obj.statut = 'refusee'
            inscription_obj.save()
            messages.success(request, f"L'inscription de {inscription_obj.nom_complet} a été refusée.")
    
    return redirect('dashboard')
