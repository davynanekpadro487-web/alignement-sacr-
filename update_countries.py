import re

countries = [
    ('Afrique du Sud', '+27'), ('Algérie', '+213'), ('Allemagne', '+49'), ('Andorre', '+376'), 
    ('Angola', '+244'), ('Antigua-et-Barbuda', '+1'), ('Argentine', '+54'), ('Autriche', '+43'), 
    ('Bahamas', '+1'), ('Barbade', '+1'), ('Belgique', '+32'), ('Belize', '+501'), 
    ('Bénin', '+229'), ('Bermudes', '+1'), ('Biélorussie', '+375'), ('Bolivie', '+591'), 
    ('Bosnie-Herzégovine', '+387'), ('Botswana', '+267'), ('Brésil', '+55'), ('Bulgarie', '+359'), 
    ('Burkina Faso', '+226'), ('Burundi', '+257'), ('Cameroun', '+237'), ('Canada', '+1'), 
    ('Cap-Vert', '+238'), ('Chili', '+56'), ('Colombie', '+57'), ('Comores', '+269'), 
    ('Congo', '+242'), ('Costa Rica', '+506'), ('Croatie', '+385'), ('Cuba', '+53'), 
    ('Danemark', '+45'), ('Djibouti', '+253'), ('Dominique', '+1'), ('Égypte', '+20'), 
    ('Équateur', '+593'), ('Érythrée', '+291'), ('Espagne', '+34'), ('Estonie', '+372'), 
    ('Eswatini', '+268'), ('États-Unis', '+1'), ('Éthiopie', '+251'), ('Finlande', '+358'), 
    ('France', '+33'), ('Gabon', '+241'), ('Gambie', '+220'), ('Ghana', '+233'), 
    ('Grèce', '+30'), ('Grenade', '+1'), ('Guatemala', '+502'), ('Guinée', '+224'), 
    ('Guinée-Bissau', '+245'), ('Guinée équatoriale', '+240'), ('Guyana', '+592'), 
    ('Haïti', '+509'), ('Honduras', '+504'), ('Hongrie', '+36'), ('Irlande', '+353'), 
    ('Islande', '+354'), ('Italie', '+39'), ('Jamaïque', '+1'), ('Kenya', '+254'), 
    ('Lesotho', '+266'), ('Lettonie', '+371'), ('Liberia', '+231'), ('Libye', '+218'), 
    ('Liechtenstein', '+423'), ('Lituanie', '+370'), ('Luxembourg', '+352'), 
    ('Macédoine du Nord', '+389'), ('Madagascar', '+261'), ('Malawi', '+265'), ('Mali', '+223'), 
    ('Malte', '+356'), ('Maroc', '+212'), ('Maurice', '+230'), ('Mauritanie', '+222'), 
    ('Mexique', '+52'), ('Moldavie', '+373'), ('Monaco', '+377'), ('Monténégro', '+382'), 
    ('Mozambique', '+258'), ('Namibie', '+264'), ('Nicaragua', '+505'), ('Niger', '+227'), 
    ('Nigeria', '+234'), ('Norvège', '+47'), ('Ouganda', '+256'), ('Panama', '+507'), 
    ('Paraguay', '+595'), ('Pays-Bas', '+31'), ('Pérou', '+51'), ('Pologne', '+48'), 
    ('Portugal', '+351'), ('République centrafricaine', '+236'), 
    ('République démocratique du Congo', '+243'), ('République dominicaine', '+1'), 
    ('République tchèque', '+420'), ('Roumanie', '+40'), ('Royaume-Uni', '+44'), 
    ('Rwanda', '+250'), ('Saint-Kitts-et-Nevis', '+1'), ('Saint-Marin', '+378'), 
    ('Saint-Vincent-et-les-Grenadines', '+1'), ('Sainte-Lucie', '+1'), ('Salvador', '+503'), 
    ('São Tomé-et-Príncipe', '+239'), ('Sénégal', '+221'), ('Serbie', '+381'), 
    ('Seychelles', '+248'), ('Sierra Leone', '+232'), ('Slovaquie', '+421'), 
    ('Slovénie', '+386'), ('Somalie', '+252'), ('Soudan', '+249'), ('Soudan du Sud', '+211'), 
    ('Suède', '+46'), ('Suisse', '+41'), ('Suriname', '+597'), ('Tanzanie', '+255'), 
    ('Tchad', '+235'), ('Togo', '+228'), ('Trinité-et-Tobago', '+1'), ('Tunisie', '+216'), 
    ('Ukraine', '+380'), ('Uruguay', '+598'), ('Vatican', '+379'), ('Venezuela', '+58'), 
    ('Zambie', '+260'), ('Zimbabwe', '+263')
]

countries.sort(key=lambda x: x[0])
options = ['<option value="+225" selected>Côte d\\'Ivoire +225</option>']
for c, code in countries:
    options.append(f'                        <option value="{code}">{c} {code}</option>')

options_str = '\\n'.join(options)

with open('programme/templates/programme/inscription.html', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = re.compile(r'(<select id="country_code"[^>]*>).*?(</select>)', re.DOTALL)
replacement = r'\1\n                        ' + options_str + r'\n                    \2'

new_content = pattern.sub(replacement, content)

with open('programme/templates/programme/inscription.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Replacement done.")
