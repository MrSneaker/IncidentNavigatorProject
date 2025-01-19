import json
import re

# Ouverture du fichier JSON d'entrée ('finetune_validation.json') en mode lecture
with open('../../data/finetune_validation.json', 'r') as file:
    data = json.load(file)

# Liste vide pour stocker les données reformattées
formatted_data = []

# Parcours de chaque entrée dans les données chargées
for entry in data:
    # Extraction du champ 'response' de l'entrée actuelle
    response_data = entry["response"]

    # Vérification si 'response' est une chaîne de caractères (cas où la réponse n'est pas déjà un dictionnaire)
    if isinstance(response_data, str):
        try:
            # Nettoyage de la chaîne de caractères en supprimant les caractères de contrôle (ASCII de 0x00 à 0x1F)
            cleaned_response = re.sub(r'[\x00-\x1F]+', '', response_data)
            # Tentative de conversion de la chaîne nettoyée en JSON
            response_data = json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            # Si une erreur de décodage se produit, on passe à l'entrée suivante
            continue 

    # Création d'un nouveau dictionnaire pour stocker l'entrée reformattée
    formatted_entry = {
        "industry": entry["industry"],
        "question": entry["question"],
        "response": {
            # Extraction de 'answer' et 'references' depuis 'response' et gestion des valeurs par défaut
            "answer": response_data.get("answer", ""),
            "references": response_data.get("references", [])
        }
    }
    
    # Ajout de l'entrée reformattée à la liste des données formatées
    formatted_data.append(formatted_entry)

# Définition du chemin du fichier de sortie où les données reformattées seront sauvegardées
output_path = '../../data/formatted/formatted_finetune_validation.json'

# Ouverture du fichier de sortie en mode écriture
with open(output_path, 'w') as output_file:
    # Écriture des données formatées dans le fichier de sortie sous forme d'objet JSON avec une indentation pour la lisibilité
    json.dump({"data": formatted_data}, output_file, indent=4)

# Affichage d'un message de confirmation avec le chemin du fichier où les données ont été enregistrées
print(f"Data reformatted and saved to {output_path}")
