"""
UserStoryParser Service

Parse les user stories depuis différentes sources :
- Description textuelle
- Fichier markdown
- Point d'entrée code
- Auto-détection
"""

import os
import re
import uuid
from typing import List, Optional, Tuple

from ..models.user_story_models import UserStory


class UserStoryParser:
    """
    Service de parsing de User Stories

    Convertit différents formats d'entrée en objets UserStory
    pour l'analyse de flux.
    """

    def __init__(self, root_dir: str, all_files: Optional[List[str]] = None):
        self.root_dir = root_dir
        self.all_files = all_files or []

    def _generate_id(self) -> str:
        """Génère un ID unique pour une user story"""
        return f"US-{uuid.uuid4().hex[:8].upper()}"

    def parse_text(self, text: str) -> List[UserStory]:
        """
        Parse une description textuelle de user story

        Formats supportés:
        - "Quand l'utilisateur clique sur Login..."
        - "As a user, I want to..."
        - Description libre
        """
        stories: List[UserStory] = []

        # Nettoyer le texte
        text = text.strip()

        # Détecter les patterns de user story
        # Pattern "As a... I want... So that..."
        as_a_pattern = r"[Aa]s\s+(?:a|an)\s+(\w+)[,\s]+I\s+want\s+(?:to\s+)?(.+?)(?:\s+[Ss]o\s+that\s+(.+))?$"
        match = re.search(as_a_pattern, text, re.IGNORECASE | re.DOTALL)

        if match:
            actor = match.group(1).lower()
            action = match.group(2).strip()
            outcome = match.group(3).strip() if match.group(3) else ""

            story = UserStory(
                id=self._generate_id(),
                title=f"{actor.title()}: {action[:50]}...",
                description=text,
                actor=actor,
                action=action,
                expected_outcome=outcome,
            )
            stories.append(story)
            return stories

        # Pattern "Quand/When... alors/then..."
        when_pattern = r"[Qq]uand|[Ww]hen"
        if re.search(when_pattern, text):
            # Extraire l'acteur si présent
            actor = "user"
            actor_patterns = [
                r"(?:l')?utilisateur",
                r"(?:the\s+)?user",
                r"(?:the\s+)?admin",
                r"(?:le\s+)?visiteur",
                r"(?:the\s+)?visitor",
            ]
            for pattern in actor_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    actor = re.search(pattern, text, re.IGNORECASE).group().strip()
                    break

            # Extraire l'action principale
            action = text
            action_verbs = [
                "clique", "click", "soumet", "submit", "navigue", "navigate",
                "tape", "type", "sélectionne", "select", "ouvre", "open",
                "ferme", "close", "charge", "load", "envoie", "send"
            ]
            for verb in action_verbs:
                if verb in text.lower():
                    # Trouver la phrase contenant le verbe
                    sentences = re.split(r"[.!?\n]", text)
                    for sentence in sentences:
                        if verb in sentence.lower():
                            action = sentence.strip()
                            break
                    break

            story = UserStory(
                id=self._generate_id(),
                title=action[:60] + "..." if len(action) > 60 else action,
                description=text,
                actor=actor,
                action=action,
                expected_outcome="",
            )
            stories.append(story)
            return stories

        # Description libre - créer une user story générique
        story = UserStory(
            id=self._generate_id(),
            title=text[:60] + "..." if len(text) > 60 else text,
            description=text,
            actor="user",
            action=text,
            expected_outcome="",
        )
        stories.append(story)

        return stories

    def parse_markdown(self, file_path: str) -> List[UserStory]:
        """
        Parse un fichier markdown contenant des user stories

        Formats supportés:
        - Headers avec user stories
        - Listes à puces avec format "As a..."
        - Format Gherkin (Given/When/Then)
        - Acceptance criteria
        """
        stories: List[UserStory] = []

        full_path = os.path.join(self.root_dir, file_path)
        if not os.path.exists(full_path):
            return stories

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return stories

        # Découper par sections (headers)
        sections = re.split(r"^(#{1,3}\s+.+)$", content, flags=re.MULTILINE)

        current_title = ""
        for i, section in enumerate(sections):
            section = section.strip()
            if not section:
                continue

            # C'est un header
            if section.startswith("#"):
                current_title = re.sub(r"^#+\s*", "", section)
                continue

            # Parser le contenu de la section
            # Chercher des patterns de user story
            lines = section.split("\n")
            current_story_text = []

            for line in lines:
                line = line.strip()
                if not line:
                    if current_story_text:
                        # Fin d'une story potentielle
                        story_text = " ".join(current_story_text)
                        parsed = self.parse_text(story_text)
                        if parsed:
                            for story in parsed:
                                if current_title:
                                    story.title = current_title
                                stories.append(story)
                        current_story_text = []
                    continue

                # Ligne de liste
                if line.startswith("-") or line.startswith("*") or re.match(r"^\d+\.", line):
                    line = re.sub(r"^[-*\d.]+\s*", "", line)

                current_story_text.append(line)

            # Traiter le reste
            if current_story_text:
                story_text = " ".join(current_story_text)
                parsed = self.parse_text(story_text)
                for story in parsed:
                    if current_title:
                        story.title = current_title
                    stories.append(story)

        # Si on n'a rien trouvé, parser le contenu entier
        if not stories:
            stories = self.parse_text(content)

        return stories

    def parse_gherkin(self, content: str) -> List[UserStory]:
        """Parse un contenu au format Gherkin (Given/When/Then)"""
        stories: List[UserStory] = []

        # Pattern pour les scénarios Gherkin
        scenario_pattern = r"(?:Scenario|Scénario)\s*:?\s*(.+?)(?=Scenario|Scénario|$)"
        scenarios = re.findall(scenario_pattern, content, re.IGNORECASE | re.DOTALL)

        for scenario in scenarios:
            lines = scenario.strip().split("\n")
            if not lines:
                continue

            title = lines[0].strip()
            given_clauses: List[str] = []
            when_clauses: List[str] = []
            then_clauses: List[str] = []

            current_type = None
            for line in lines[1:]:
                line = line.strip()
                if line.lower().startswith("given") or line.lower().startswith("étant donné"):
                    current_type = "given"
                    line = re.sub(r"^(?:given|étant donné)\s*", "", line, flags=re.IGNORECASE)
                elif line.lower().startswith("when") or line.lower().startswith("quand"):
                    current_type = "when"
                    line = re.sub(r"^(?:when|quand)\s*", "", line, flags=re.IGNORECASE)
                elif line.lower().startswith("then") or line.lower().startswith("alors"):
                    current_type = "then"
                    line = re.sub(r"^(?:then|alors)\s*", "", line, flags=re.IGNORECASE)
                elif line.lower().startswith("and") or line.lower().startswith("et"):
                    line = re.sub(r"^(?:and|et)\s*", "", line, flags=re.IGNORECASE)

                if line and current_type:
                    if current_type == "given":
                        given_clauses.append(line)
                    elif current_type == "when":
                        when_clauses.append(line)
                    elif current_type == "then":
                        then_clauses.append(line)

            story = UserStory(
                id=self._generate_id(),
                title=title,
                description=scenario.strip(),
                actor="user",
                action=" AND ".join(when_clauses) if when_clauses else title,
                expected_outcome=" AND ".join(then_clauses) if then_clauses else "",
            )
            stories.append(story)

        return stories

    def detect_entry_point(
        self, user_story: UserStory
    ) -> Optional[str]:
        """
        Détecte le point d'entrée code pour une user story

        Recherche des composants UI correspondant à l'action décrite.
        """
        action = user_story.action.lower()
        description = user_story.description.lower()

        # Mots-clés à rechercher dans les noms de fichiers
        keywords = []

        # Extraire les mots-clés de l'action
        action_keywords = [
            "login", "logout", "signin", "signout", "signup", "register",
            "submit", "form", "button", "modal", "dialog", "menu",
            "nav", "header", "footer", "sidebar", "dashboard", "profile",
            "settings", "cart", "checkout", "payment", "order", "product",
            "search", "filter", "sort", "list", "table", "grid", "card"
        ]

        for keyword in action_keywords:
            if keyword in action or keyword in description:
                keywords.append(keyword)

        # Rechercher les fichiers correspondants
        candidates: List[Tuple[str, int]] = []

        for file_path in self.all_files:
            file_lower = file_path.lower()

            # Ignorer les fichiers non-UI
            if not any(ext in file_path for ext in [
                ".tsx", ".jsx", ".vue", ".svelte", ".dart"
            ]):
                continue

            # Ignorer les fichiers de test
            if any(test in file_lower for test in [
                ".test.", ".spec.", "__tests__", "_test."
            ]):
                continue

            # Compter les correspondances
            score = 0
            for keyword in keywords:
                if keyword in file_lower:
                    score += 1

            if score > 0:
                candidates.append((file_path, score))

        # Trier par score et retourner le meilleur
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]

        return None

    def auto_detect_flows(self) -> List[UserStory]:
        """
        Auto-détecte les flux utilisateur depuis le code

        Analyse les composants UI pour trouver les actions principales
        et génère des user stories correspondantes.
        """
        stories: List[UserStory] = []

        # Rechercher les fichiers UI avec des gestionnaires d'événements
        ui_extensions = [".tsx", ".jsx", ".vue", ".svelte", ".dart"]
        event_patterns = [
            # React/JS
            r"on(Click|Submit|Change|Press)\s*=\s*\{",
            r"@click\s*=",  # Vue
            r"on:click\s*=",  # Svelte
            # Flutter
            r"onPressed\s*:",
            r"onTap\s*:",
            r"onSubmitted\s*:",
        ]

        for file_path in self.all_files:
            # Vérifier l'extension
            if not any(file_path.endswith(ext) for ext in ui_extensions):
                continue

            # Ignorer les tests
            if any(test in file_path.lower() for test in [
                ".test.", ".spec.", "__tests__"
            ]):
                continue

            # Lire le fichier
            full_path = os.path.join(self.root_dir, file_path)
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception:
                continue

            # Chercher les événements
            for pattern in event_patterns:
                for match in re.finditer(pattern, content):
                    # Extraire le nom du composant depuis le fichier
                    component_name = os.path.splitext(os.path.basename(file_path))[0]

                    # Déterminer l'action depuis le pattern
                    action_type = "click"
                    if "Submit" in pattern or "submit" in pattern.lower():
                        action_type = "submit"
                    elif "Change" in pattern:
                        action_type = "change"
                    elif "Press" in pattern or "Pressed" in pattern:
                        action_type = "press"

                    # Créer une user story
                    story = UserStory(
                        id=self._generate_id(),
                        title=f"User {action_type}s on {component_name}",
                        description=f"User performs {action_type} action in {component_name} component",
                        actor="user",
                        action=f"{action_type} on {component_name}",
                        expected_outcome="Action is processed correctly",
                        entry_point_file=file_path,
                        entry_point_component=component_name,
                    )

                    # Éviter les doublons
                    if not any(
                        s.entry_point_file == file_path and s.action == story.action
                        for s in stories
                    ):
                        stories.append(story)
                    break  # Un seul événement par fichier

        return stories

    def parse_from_code_entry(self, file_path: str) -> List[UserStory]:
        """
        Crée une user story à partir d'un fichier de code comme point d'entrée

        Analyse le fichier pour comprendre son rôle et génère une user story.
        """
        stories: List[UserStory] = []

        full_path = os.path.join(self.root_dir, file_path)
        if not os.path.exists(full_path):
            return stories

        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            return stories

        # Extraire le nom du composant
        component_name = os.path.splitext(os.path.basename(file_path))[0]

        # Analyser le contenu pour deviner l'objectif
        purpose = self._guess_component_purpose(content, component_name)

        story = UserStory(
            id=self._generate_id(),
            title=f"User interacts with {component_name}",
            description=f"User flow starting from {component_name}: {purpose}",
            actor="user",
            action=purpose,
            expected_outcome="Flow completes successfully",
            entry_point_file=file_path,
            entry_point_component=component_name,
        )
        stories.append(story)

        return stories

    def _guess_component_purpose(self, content: str, name: str) -> str:
        """Devine l'objectif d'un composant à partir de son code"""
        name_lower = name.lower()
        content_lower = content.lower()

        # Patterns de détection
        purposes = {
            "login": ["login", "signin", "authentica"],
            "register": ["register", "signup", "create account"],
            "logout": ["logout", "signout", "disconnect"],
            "search": ["search", "find", "query"],
            "filter": ["filter", "sort", "order by"],
            "submit": ["submit", "send", "post", "create"],
            "delete": ["delete", "remove", "destroy"],
            "edit": ["edit", "update", "modify"],
            "view": ["view", "display", "show", "read"],
            "navigate": ["navigate", "route", "redirect"],
            "upload": ["upload", "file", "image"],
            "download": ["download", "export"],
            "payment": ["pay", "checkout", "cart", "purchase"],
        }

        for action, keywords in purposes.items():
            for keyword in keywords:
                if keyword in name_lower or keyword in content_lower:
                    return f"User performs {action} action"

        return f"User interacts with {name}"
