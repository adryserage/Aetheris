#!/usr/bin/env python3
"""
Script pour générer le .bugs_cache.json depuis les fichiers d'analyse existants.
Utile si l'analyse a réussi mais l'étape impact_analysis a échoué.
"""

import os
import json
import re
import hashlib
from pathlib import Path


def generate_bug_id(file_path: str, description: str) -> str:
    """Génère un ID unique pour un bug"""
    content = f"{file_path}:{description[:50]}"
    hash_value = hashlib.sha256(content.encode()).hexdigest()[:8]
    return f"BUG-{hash_value.upper()}"


def parse_severity(text: str) -> str:
    """Parse la sévérité depuis le texte"""
    text_lower = text.lower()
    if any(w in text_lower for w in ["critical", "critique", "xss", "sql injection", "injection"]):
        return "critical"
    elif any(w in text_lower for w in ["high", "haute", "élevé", "security", "sécurité", "vulnérab"]):
        return "high"
    elif any(w in text_lower for w in ["low", "basse", "faible", "minor", "mineur"]):
        return "low"
    elif any(w in text_lower for w in ["info", "information", "note"]):
        return "info"
    return "medium"


def extract_bugs_from_markdown(md_path: str, base_dir: str) -> list:
    """Extrait les bugs depuis un fichier markdown d'analyse"""
    bugs = []

    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  ⚠️  Erreur lecture {md_path}: {e}")
        return bugs

    # Extraire le chemin du fichier analysé depuis le markdown
    file_path_match = re.search(r'`([^`]+\.(py|js|ts|tsx|jsx|dart|java|go|rs|cpp|c|h|swift|kt))`', content)
    if file_path_match:
        source_file = file_path_match.group(1)
    else:
        # Déduire depuis le chemin du markdown
        rel_path = os.path.relpath(md_path, base_dir)
        source_file = rel_path.replace('.md', '').replace('\\', '/')

    # Chercher la section Risques
    risks_match = re.search(r'##\s*Risques.*?\n(.*?)(?=##|$)', content, re.DOTALL | re.IGNORECASE)
    if risks_match:
        for line in risks_match.group(1).split('\n'):
            line = line.strip()
            if line.startswith(('-', '*', '•', '1.', '2.', '3.', '4.', '5.')) and len(line) > 10:
                bug_desc = re.sub(r'^[-*•\d.]+\s*', '', line).strip()
                if bug_desc and not bug_desc.startswith('#'):
                    bugs.append({
                        "id": generate_bug_id(source_file, bug_desc),
                        "file_path": source_file,
                        "line_number": None,
                        "bug_type": "risk",
                        "severity": parse_severity(bug_desc),
                        "description": bug_desc,
                        "recommendation": "Vérifier et corriger ce risque",
                        "impacted_files": []
                    })

    # Chercher les problèmes de sécurité
    security_match = re.search(r'##\s*(Sécurité|Security).*?\n(.*?)(?=##|$)', content, re.DOTALL | re.IGNORECASE)
    if security_match:
        for line in security_match.group(2).split('\n'):
            line = line.strip()
            if line.startswith(('-', '*', '•')) and len(line) > 10:
                bug_desc = re.sub(r'^[-*•]+\s*', '', line).strip()
                if bug_desc and not bug_desc.startswith('#'):
                    severity = parse_severity(bug_desc)
                    if severity in ["medium", "info"]:
                        severity = "high"  # Issues de sécurité sont au moins high
                    bugs.append({
                        "id": generate_bug_id(source_file, f"security:{bug_desc}"),
                        "file_path": source_file,
                        "line_number": None,
                        "bug_type": "security",
                        "severity": severity,
                        "description": bug_desc,
                        "recommendation": "Corriger cette vulnérabilité de sécurité",
                        "impacted_files": []
                    })

    return bugs


def main():
    print("=" * 60)
    print("🔧 Génération du cache des bugs depuis les analyses existantes")
    print("=" * 60)
    print()

    # Trouver le répertoire d'analyses
    analyses_dir = "docs/analyses"
    if not os.path.exists(analyses_dir):
        print(f"❌ Répertoire {analyses_dir} introuvable")
        print("   Assurez-vous d'être dans le bon répertoire de projet")
        return

    all_bugs = []
    files_processed = 0

    # Scanner les fichiers d'analyse
    for root, dirs, files in os.walk(analyses_dir):
        # Ignorer les dossiers cachés
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for f in files:
            if f.endswith('.md') and not f.startswith('.') and f != 'README.md':
                md_path = os.path.join(root, f)
                bugs = extract_bugs_from_markdown(md_path, analyses_dir)
                if bugs:
                    print(f"  📄 {md_path}: {len(bugs)} bug(s)")
                    all_bugs.extend(bugs)
                files_processed += 1

    print()
    print(f"📊 {files_processed} fichiers traités")
    print(f"🐛 {len(all_bugs)} bugs trouvés au total")

    # Dédupliquer par ID
    unique_bugs = {}
    for bug in all_bugs:
        if bug["id"] not in unique_bugs:
            unique_bugs[bug["id"]] = bug

    all_bugs = list(unique_bugs.values())
    print(f"🔍 {len(all_bugs)} bugs uniques après déduplication")

    # Statistiques par sévérité
    by_severity = {}
    for bug in all_bugs:
        sev = bug["severity"]
        by_severity[sev] = by_severity.get(sev, 0) + 1

    print()
    print("📈 Répartition par sévérité:")
    for sev in ["critical", "high", "medium", "low", "info"]:
        if sev in by_severity:
            print(f"   {sev}: {by_severity[sev]}")

    # Sauvegarder le cache
    cache_path = os.path.join(analyses_dir, ".bugs_cache.json")
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(all_bugs, f, indent=2, ensure_ascii=False)

    print()
    print(f"✅ Cache sauvegardé: {cache_path}")
    print()
    print("🚀 Vous pouvez maintenant lancer:")
    print("   aetheris fix --auto")


if __name__ == "__main__":
    main()
