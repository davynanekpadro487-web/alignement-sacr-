import os
import django
from django.contrib.auth import get_user_model

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alignement_sacre.settings')
django.setup()

User = get_user_model()

# Identifiants du superuser
USERNAME = 'admin'
EMAIL = 'contact@jardindefarah.com'
PASSWORD = 'admin' # Changez ce mot de passe une fois connecté sur le dashboard !

if not User.objects.filter(username=USERNAME).exists():
    print(f"Création du superuser '{USERNAME}'...")
    User.objects.create_superuser(username=USERNAME, email=EMAIL, password=PASSWORD)
    print("Superuser créé avec succès !")
else:
    print(f"Le superuser '{USERNAME}' existe déjà.")
