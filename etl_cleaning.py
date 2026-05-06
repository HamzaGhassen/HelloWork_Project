import pandas as pd
import re

# --- CONFIGURATION ---
INPUT_FILE = "hellowork_all_offers.csv"
OUTPUT_FILE = "donnees_propres_bi.csv"


def clean_salary(text):
    """Extrait le salaire minimum et maximum s'ils existent"""
    # Cherche des motifs comme "30 000 - 40 000 €" ou "1 100 €"
    # On enlève les espaces insécables pour faciliter la regex
    text = text.replace('\u202f', '').replace(' ', '')

    # Regex pour trouver les montants en euros
    # Ex: cherche "30000-40000€" ou "1800€"
    match = re.search(r'(\d{3,6})(?:-(\d{3,6}))?€', text)

    if match:
        min_sal = int(match.group(1))
        # Si pas de max, on prend le min comme unique valeur
        max_sal = int(match.group(2)) if match.group(2) else min_sal

        # On normalise tout en "Salaire Annuel"
        # Si le montant est petit (< 8000), c'est probablement mensuel -> x12
        if min_sal < 8000:
            min_sal *= 12
            max_sal *= 12

        return min_sal, max_sal
    return None, None


def extract_contract(text):
    """Détecte le type de contrat"""
    text = text.upper()
    if "CDI" in text: return "CDI"
    if "CDD" in text: return "CDD"
    if "ALTERNANCE" in text or "CONTRAT PRO" in text: return "Alternance"
    if "STAGE" in text: return "Stage"
    if "FREELANCE" in text or "INDÉPENDANT" in text: return "Freelance"
    return "Autre"


def extract_location(text):
    """Extrait l'arrondissement ou la ville"""
    # Cherche un code postal (75001, 75, 92...)
    match = re.search(r'(Paris\s?\d*e?|Lille|Lyon|Marseille|\d{5}|\d{2}\s)', text, re.IGNORECASE)
    if match:
        return match.group(0).strip()
    return "Paris"  # Valeur par défaut si rien trouvé


def run_etl():
    print("🧹 Démarrage du nettoyage ETL...")

    # 1. Chargement
    try:
        df = pd.read_csv(INPUT_FILE)
        print(f"📥 {len(df)} lignes chargées.")
    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier {INPUT_FILE} n'existe pas. Lancez le scraper d'abord.")
        return

    # 2. Transformation
    # On applique nos fonctions sur la colonne brute

    # Extraction Salaire
    # On applique la fonction et on sépare le résultat en 2 colonnes
    salary_data = df['Description_Brute'].apply(clean_salary)
    df['Salaire_Min'] = [x[0] for x in salary_data]
    df['Salaire_Max'] = [x[1] for x in salary_data]

    # Calcul d'un salaire moyen pour les stats
    df['Salaire_Moyen'] = (df['Salaire_Min'] + df['Salaire_Max']) / 2

    # Extraction Contrat
    df['Type_Contrat'] = df['Description_Brute'].apply(extract_contract)

    # Extraction Localisation (Simple)
    df['Localisation_Clean'] = df['Description_Brute'].apply(extract_location)

    # Nettoyage final : On supprime les lignes sans salaire (optionnel, selon besoins BI)
    # Pour l'instant on garde tout, mais on ajoute un indicateur
    df['Salaire_Connu'] = df['Salaire_Moyen'].notna()

    # 3. Chargement (Save)
    print(f"📊 Aperçu des données propres :")
    print(df[['Titre', 'Type_Contrat', 'Salaire_Moyen']].head())

    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print(f"✅ Terminé ! Fichier propre généré : {OUTPUT_FILE}")


if __name__ == "__main__":
    run_etl()
