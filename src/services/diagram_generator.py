"""
DiagramGenerator Service

Génère des diagrammes visuels (Mermaid, PlantUML) à partir des flux analysés.
"""

import os
from typing import List

from ..models.user_story_models import FlowStep
from ..models.user_story_models import FlowStepType
from ..models.user_story_models import UserStoryAnalysisResult
from ..models.user_story_models import UserStoryFlow


class DiagramGenerator:
    """
    Générateur de diagrammes pour les flux de user stories

    Supporte:
    - Diagrammes de séquence Mermaid
    - Flowcharts Mermaid
    - Diagrammes PlantUML
    """

    def __init__(self, output_dir: str = "docs/user-stories"):
        self.output_dir = output_dir

    def _sanitize_name(self, name: str) -> str:
        """Nettoie un nom pour l'utiliser dans un diagramme"""
        # Supprimer les caractères spéciaux
        sanitized = "".join(c if c.isalnum() or c in "_-" else "_" for c in name)
        # Limiter la longueur
        return sanitized[:30]

    def _get_participant_name(self, step: FlowStep) -> str:
        """Extrait un nom de participant depuis une étape"""
        step_type = step.step_type

        if step_type == FlowStepType.UI_EVENT.value:
            if step.file_path:
                return os.path.splitext(os.path.basename(step.file_path))[0]
            return "UI"
        elif step_type == FlowStepType.API_CALL.value:
            return "Frontend"
        elif step_type == FlowStepType.BACKEND_HANDLER.value:
            if step.file_path:
                return os.path.splitext(os.path.basename(step.file_path))[0]
            return "Backend"
        elif step_type == FlowStepType.DATABASE_QUERY.value:
            return "Database"
        elif step_type == FlowStepType.EXTERNAL_SERVICE.value:
            return "ExternalService"
        elif step_type == FlowStepType.RESPONSE.value:
            return "Backend"
        else:
            return "System"

    def generate_mermaid_sequence(self, flow: UserStoryFlow) -> str:
        """
        Génère un diagramme de séquence Mermaid pour un flux

        Args:
            flow: Le flux à visualiser

        Returns:
            Code Mermaid du diagramme de séquence
        """
        lines = ["sequenceDiagram"]

        # Collecter les participants uniques
        participants = ["User"]
        seen = {"User"}

        for step in flow.steps:
            participant = self._get_participant_name(step)
            if participant not in seen:
                participants.append(participant)
                seen.add(participant)

        # Ajouter les participants
        for p in participants:
            lines.append(f"    participant {self._sanitize_name(p)}")

        lines.append("")

        # Générer les interactions
        prev_participant = "User"

        for step in flow.steps:
            current = self._sanitize_name(self._get_participant_name(step))
            description = step.description[:50].replace('"', "'")

            step_type = step.step_type

            if step_type == FlowStepType.UI_EVENT.value:
                lines.append(f"    User->>+{current}: {description}")
                prev_participant = current

            elif step_type == FlowStepType.API_CALL.value:
                # Flèche vers le backend
                lines.append(f"    {prev_participant}->>+Backend: {description}")
                prev_participant = "Backend"

            elif step_type == FlowStepType.BACKEND_HANDLER.value:
                if current != "Backend":
                    lines.append(f"    Backend->>+{current}: {description}")
                    prev_participant = current
                else:
                    lines.append(f"    Note over Backend: {description}")

            elif step_type == FlowStepType.DATABASE_QUERY.value:
                lines.append(f"    {prev_participant}->>+Database: Query")
                lines.append(f"    Database-->>-{prev_participant}: Result")

            elif step_type == FlowStepType.EXTERNAL_SERVICE.value:
                lines.append(f"    {prev_participant}->>+ExternalService: {description}")
                lines.append(f"    ExternalService-->>-{prev_participant}: Response")

            elif step_type == FlowStepType.RESPONSE.value:
                lines.append(f"    {prev_participant}-->>-User: {description}")
                prev_participant = "User"

            elif step_type == FlowStepType.ERROR_HANDLER.value:
                lines.append(f"    Note over {prev_participant}: Error: {description}")

            elif step_type == FlowStepType.REDIRECT.value:
                lines.append(f"    {prev_participant}-->>User: Redirect: {description}")

            else:
                lines.append(f"    Note over {prev_participant}: {description}")

        return "\n".join(lines)

    def generate_mermaid_flowchart(self, flow: UserStoryFlow) -> str:
        """
        Génère un flowchart Mermaid pour un flux

        Args:
            flow: Le flux à visualiser

        Returns:
            Code Mermaid du flowchart
        """
        lines = ["flowchart TD"]

        # Générer les nœuds
        for i, step in enumerate(flow.steps):
            node_id = f"S{i}"
            description = step.description[:40].replace('"', "'")
            step_type = step.step_type

            # Forme selon le type
            if step_type == FlowStepType.UI_EVENT.value:
                lines.append(f"    {node_id}([{description}])")  # Oval
            elif step_type == FlowStepType.API_CALL.value:
                lines.append(f"    {node_id}[/{description}/]")  # Parallélogramme
            elif step_type == FlowStepType.BACKEND_HANDLER.value:
                lines.append(f"    {node_id}[{description}]")  # Rectangle
            elif step_type == FlowStepType.DATABASE_QUERY.value:
                lines.append(f"    {node_id}[({description})]")  # Cylindre
            elif step_type == FlowStepType.RESPONSE.value:
                lines.append(f"    {node_id}([{description}])")  # Oval
            elif step_type == FlowStepType.ERROR_HANDLER.value:
                lines.append(f"    {node_id}{{{description}}}")  # Losange
            else:
                lines.append(f"    {node_id}[{description}]")

        lines.append("")

        # Générer les connexions
        for i in range(len(flow.steps) - 1):
            lines.append(f"    S{i} --> S{i + 1}")

        # Ajouter les styles
        lines.append("")
        lines.append("    %% Styles")
        for i, step in enumerate(flow.steps):
            step_type = step.step_type
            if step_type == FlowStepType.UI_EVENT.value:
                lines.append(f"    style S{i} fill:#e1f5fe")
            elif step_type == FlowStepType.API_CALL.value:
                lines.append(f"    style S{i} fill:#fff3e0")
            elif step_type == FlowStepType.BACKEND_HANDLER.value:
                lines.append(f"    style S{i} fill:#e8f5e9")
            elif step_type == FlowStepType.DATABASE_QUERY.value:
                lines.append(f"    style S{i} fill:#f3e5f5")
            elif step_type == FlowStepType.ERROR_HANDLER.value:
                lines.append(f"    style S{i} fill:#ffebee")

        return "\n".join(lines)

    def generate_plantuml_sequence(self, flow: UserStoryFlow) -> str:
        """
        Génère un diagramme de séquence PlantUML pour un flux

        Args:
            flow: Le flux à visualiser

        Returns:
            Code PlantUML du diagramme
        """
        lines = ["@startuml", ""]

        # Configuration
        lines.append("skinparam sequenceMessageAlign center")
        lines.append("skinparam responseMessageBelowArrow true")
        lines.append("")

        # Participants
        participants = ["actor User"]
        seen = {"User"}

        for step in flow.steps:
            participant = self._get_participant_name(step)
            if participant not in seen:
                p_type = "participant"
                if "database" in participant.lower():
                    p_type = "database"
                elif "service" in participant.lower():
                    p_type = "entity"
                participants.append(
                    f'{p_type} "{participant}" as {self._sanitize_name(participant)}'
                )
                seen.add(participant)

        lines.extend(participants)
        lines.append("")

        # Interactions
        prev_participant = "User"

        for step in flow.steps:
            current = self._sanitize_name(self._get_participant_name(step))
            description = step.description[:60].replace('"', "'")
            step_type = step.step_type

            if step_type == FlowStepType.UI_EVENT.value:
                lines.append(f"User -> {current} : {description}")
                lines.append(f"activate {current}")
                prev_participant = current

            elif step_type == FlowStepType.API_CALL.value:
                lines.append(f"{prev_participant} -> Backend : {description}")
                lines.append("activate Backend")
                prev_participant = "Backend"

            elif step_type == FlowStepType.BACKEND_HANDLER.value:
                if current != "Backend":
                    lines.append(f"Backend -> {current} : {description}")
                    prev_participant = current
                else:
                    lines.append(f"note over Backend : {description}")

            elif step_type == FlowStepType.DATABASE_QUERY.value:
                lines.append(f"{prev_participant} -> Database : Query")
                lines.append("activate Database")
                lines.append(f"Database --> {prev_participant} : Result")
                lines.append("deactivate Database")

            elif step_type == FlowStepType.RESPONSE.value:
                lines.append(f"{prev_participant} --> User : {description}")
                if prev_participant != "User":
                    lines.append(f"deactivate {prev_participant}")
                prev_participant = "User"

            elif step_type == FlowStepType.ERROR_HANDLER.value:
                lines.append(f"note over {prev_participant} #ffcccc : Error: {description}")

        lines.append("")
        lines.append("@enduml")

        return "\n".join(lines)

    def generate_data_flow_diagram(self, flow: UserStoryFlow) -> str:
        """
        Génère un diagramme de flux de données Mermaid

        Args:
            flow: Le flux à visualiser

        Returns:
            Code Mermaid du diagramme
        """
        lines = ["graph LR"]
        lines.append("")

        # Définir les nœuds de données
        data_nodes = set()
        for step in flow.steps:
            for inp in step.inputs:
                data_nodes.add(inp)
            for out in step.outputs:
                data_nodes.add(out)

        # Créer les nœuds de données
        for i, data in enumerate(data_nodes):
            self._sanitize_name(data)
            lines.append(f"    D{i}[({data[:20]})]")

        lines.append("")

        # Créer les nœuds de processus
        for i, step in enumerate(flow.steps):
            description = step.description[:25]
            lines.append(f"    P{i}[{description}]")

        lines.append("")

        # Créer les connexions
        data_list = list(data_nodes)
        for i, step in enumerate(flow.steps):
            for inp in step.inputs:
                if inp in data_list:
                    d_idx = data_list.index(inp)
                    lines.append(f"    D{d_idx} --> P{i}")

            for out in step.outputs:
                if out in data_list:
                    d_idx = data_list.index(out)
                    lines.append(f"    P{i} --> D{d_idx}")

        # Styles
        lines.append("")
        lines.append("    %% Styles")
        for i in range(len(data_list)):
            lines.append(f"    style D{i} fill:#e3f2fd")
        for i in range(len(flow.steps)):
            lines.append(f"    style P{i} fill:#fff9c4")

        return "\n".join(lines)

    def generate_all_flows_diagram(
        self,
        result: UserStoryAnalysisResult,
    ) -> str:
        """
        Génère un diagramme récapitulatif de tous les flux

        Args:
            result: Le résultat complet de l'analyse

        Returns:
            Code Mermaid du diagramme
        """
        lines = ["flowchart TB"]
        lines.append("")

        # Créer un sous-graphe pour chaque flux
        for i, flow in enumerate(result.flows):
            title = flow.title[:30].replace('"', "'")
            lines.append(f"    subgraph F{i}[{title}]")

            for j, step in enumerate(flow.steps[:5]):  # Limiter à 5 étapes
                description = step.description[:20]
                lines.append(f"        F{i}S{j}[{description}]")

            # Connexions internes
            for j in range(min(len(flow.steps) - 1, 4)):
                lines.append(f"        F{i}S{j} --> F{i}S{j + 1}")

            lines.append("    end")
            lines.append("")

        # Connexions entre flux (via endpoints communs)
        endpoint_flows: dict = {}
        for i, flow in enumerate(result.flows):
            for ep in flow.api_endpoints:
                key = f"{ep.method}:{ep.path}"
                if key not in endpoint_flows:
                    endpoint_flows[key] = []
                endpoint_flows[key].append(i)

        # Connecter les flux qui partagent des endpoints
        for ep_key, flow_indices in endpoint_flows.items():
            if len(flow_indices) > 1:
                for j in range(len(flow_indices) - 1):
                    lines.append(f"    F{flow_indices[j]} -.-> F{flow_indices[j + 1]}")

        # Styles par problèmes
        lines.append("")
        lines.append("    %% Color by issues")
        for i, flow in enumerate(result.flows):
            has_critical = any(issue.severity == "critical" for issue in flow.issues)
            has_high = any(issue.severity == "high" for issue in flow.issues)

            if has_critical:
                lines.append(f"    style F{i} fill:#ffebee,stroke:#c62828")
            elif has_high:
                lines.append(f"    style F{i} fill:#fff3e0,stroke:#ef6c00")
            else:
                lines.append(f"    style F{i} fill:#e8f5e9,stroke:#2e7d32")

        return "\n".join(lines)

    def save_diagrams(
        self,
        result: UserStoryAnalysisResult,
        format: str = "mermaid",
    ) -> List[str]:
        """
        Sauvegarde tous les diagrammes dans des fichiers

        Args:
            result: Le résultat de l'analyse
            format: 'mermaid' ou 'plantuml'

        Returns:
            Liste des chemins de fichiers créés
        """
        os.makedirs(self.output_dir, exist_ok=True)
        files_created = []

        # Diagramme récapitulatif
        overview = self.generate_all_flows_diagram(result)
        overview_path = os.path.join(self.output_dir, "flows-overview.md")
        with open(overview_path, "w", encoding="utf-8") as f:
            f.write("# User Story Flows Overview\n\n")
            f.write(f"```{format}\n{overview}\n```\n")
        files_created.append(overview_path)

        # Diagrammes individuels
        for i, flow in enumerate(result.flows):
            if format == "mermaid":
                sequence = self.generate_mermaid_sequence(flow)
                flowchart = self.generate_mermaid_flowchart(flow)
            else:
                sequence = self.generate_plantuml_sequence(flow)
                flowchart = ""

            filename = f"flow-{i + 1}-{self._sanitize_name(flow.title)}.md"
            filepath = os.path.join(self.output_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {flow.title}\n\n")
                f.write("## Sequence Diagram\n\n")
                f.write(f"```{format}\n{sequence}\n```\n\n")
                if flowchart:
                    f.write("## Flowchart\n\n")
                    f.write(f"```{format}\n{flowchart}\n```\n")

            files_created.append(filepath)

        return files_created
