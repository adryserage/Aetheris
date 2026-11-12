"""Draw the README diagrams (docs/assets/diagrams/*.svg), in English and French.

Usage: python scripts/gen_diagrams.py [output_dir]

The agent names and the rule and playbook counts come from the registry, so the diagrams
follow the rules. README.md and README.fr.md load them from the main branch on GitHub,
which also works on PyPI.
"""

import sys
from pathlib import Path
from xml.sax.saxutils import escape

from aetheris.registry import AGENTS, PLAYBOOKS

DEFAULT_OUT = Path(__file__).resolve().parent.parent / "docs" / "assets" / "diagrams"

CANVAS = "#F5F7FA"
INK = "#1F2933"
MUTED = "#52606D"
LINE = "#9AA5B1"
ACCENT = "#0F6E8C"
ACCENT_FILL = "#E6F3F7"
NET = "#B45309"
NET_TEXT = "#92400E"
NET_FILL = "#FDF3E7"
SANS = "'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

AGENT_NAMES_FR = {
    "security": "Sécurité",
    "architecture": "Architecture",
    "code_quality": "Qualité du code",
    "metrics": "Métriques",
    "dependency": "Dépendances",
    "qa_synthesis": "Synthèse QA",
    "type_safety": "Sûreté des types",
    "performance": "Performance",
    "api_contract": "Contrat d'API",
    "data_privacy": "Données perso.",
}


def _rule_count() -> int:
    return sum(len(agent.rules) for agent in AGENTS.values())


TEXT = {
    "en": {
        "how_title": "How Aetheris works",
        "how_label": "Your assistant calls Aetheris over MCP. Aetheris reads your project and "
        "never calls an AI model; its only network call sends package names and versions to OSV.",
        "provider": ["Your assistant's AI provider", "unchanged by Aetheris"],
        "prompts": "prompts",
        "machine": "Your machine",
        "assistant": ["AI coding assistant", "Claude Code, Cursor,", "any MCP client"],
        "assistant_job": "Reasons, writes the review",
        "server": [
            "Aetheris MCP server",
            f"{len(AGENTS)} agents, {_rule_count()} rules",
            "Checks without AI",
            f"{len(PLAYBOOKS)} review playbooks",
        ],
        "calls": "tool calls",
        "returns": "rules, findings",
        "project": ["Your project", "source files, git diff, lockfiles"],
        "reads": "reads",
        "reads_root": "reads (root only)",
        "osv": ["OSV.dev", "Known vulnerability", "database"],
        "osv_send": ["packages,", "versions"],
        "osv_note": "the only network call",
        "flow_title": "Review flow",
        "flow_sub": "Your assistant calls the tools in this order.",
        "flow_label": "Review flow: plan_review picks files and agents; for each agent the "
        "assistant calls get_rules, get_playbook and run_checks and reviews the code; "
        "synthesize_report merges, sorts and scores the findings.",
        "plan": ["files by priority,", "agents to run"],
        "loop": "for each agent in the plan",
        "rules": ["rules for the", "languages found"],
        "playbook": ["review method", "to follow"],
        "checks": ["findings", "without AI"],
        "then": "then the assistant reads the code and adds its findings",
        "report": ["merged, sorted,", "scored 0 to 100"],
        "agents_title": f"The {len(AGENTS)} agents and their rules",
        "agents_note_post": " returns this list and presets, such as a security audit.",
    },
    "fr": {
        "how_title": "Fonctionnement d'Aetheris",
        "how_label": "L'assistant appelle Aetheris par MCP. Aetheris lit le projet et n'appelle "
        "jamais de modèle d'IA ; son seul appel réseau envoie des noms et versions de paquets "
        "à OSV.",
        "provider": ["Fournisseur IA de l'assistant", "inchangé par Aetheris"],
        "prompts": "requêtes",
        "machine": "Votre machine",
        "assistant": ["Assistant de code IA", "Claude Code, Cursor,", "tout client MCP"],
        "assistant_job": "Raisonne, écrit la revue",
        "server": [
            "Serveur MCP Aetheris",
            f"{len(AGENTS)} agents, {_rule_count()} règles",
            "Vérifications sans IA",
            f"{len(PLAYBOOKS)} méthodes de revue",
        ],
        "calls": "appels d'outils",
        "returns": "règles, résultats",
        "project": ["Votre projet", "fichiers source, diff git, fichiers de verrouillage"],
        "reads": "lit",
        "reads_root": "lit (racine seulement)",
        "osv": ["OSV.dev", "Base des failles", "connues"],
        "osv_send": ["paquets,", "versions"],
        "osv_note": "le seul appel réseau",
        "flow_title": "Déroulé d'une revue",
        "flow_sub": "L'assistant appelle les outils dans cet ordre.",
        "flow_label": "Déroulé d'une revue : plan_review choisit les fichiers et les agents ; "
        "pour chaque agent, l'assistant appelle get_rules, get_playbook et run_checks et relit "
        "le code ; synthesize_report fusionne, trie et note les résultats.",
        "plan": ["fichiers par priorité,", "agents à lancer"],
        "loop": "pour chaque agent du plan",
        "rules": ["règles des", "langages trouvés"],
        "playbook": ["méthode de revue", "à suivre"],
        "checks": ["résultats", "sans IA"],
        "then": "puis l'assistant lit le code et ajoute ses résultats",
        "report": ["dédoublonné, trié,", "noté de 0 à 100"],
        "agents_title": f"Les {len(AGENTS)} agents et leurs règles",
        "agents_note_post": " renvoie cette liste et des préréglages, comme un audit de sécurité.",
    },
}


def _text(x, y, content, size=12, fill=INK, weight="normal", anchor="start", font=SANS):
    return (
        f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(content)}</text>'
    )


def _box(x, y, w, h, fill="#FFFFFF", stroke=LINE, width=1.5, dash=None, radius=10):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="{width}"{dash_attr}/>'
    )


def _arrow(x1, y1, x2, y2, color=MUTED, both=False):
    marker = {MUTED: "ink", NET: "net", ACCENT: "accent"}[color]
    start = f' marker-start="url(#{marker}-start)"' if both else ""
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.6"'
        f'{start} marker-end="url(#{marker})"/>'
    )


def _defs():
    parts = []
    for name, color in (("ink", MUTED), ("net", NET), ("accent", ACCENT)):
        parts.append(
            f'<marker id="{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            f'markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{color}"/>'
            "</marker>"
        )
        parts.append(
            f'<marker id="{name}-start" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="7" '
            f'markerHeight="7" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="{color}"/>'
            "</marker>"
        )
    return "<defs>" + "".join(parts) + "</defs>"


def _svg(width, height, label, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" aria-label="{escape(label)}">'
        f"<title>{escape(label)}</title>{_defs()}"
        f'<rect width="{width}" height="{height}" rx="14" fill="{CANVAS}"/>'
        + "".join(body)
        + "</svg>\n"
    )


def how_it_works(t: dict) -> str:
    b = [_text(32, 40, t["how_title"], size=20, weight="bold")]

    b.append(_box(40, 62, 240, 56, fill="#EEF1F4"))
    b.append(_text(160, 86, t["provider"][0], size=13, fill=MUTED, weight="bold", anchor="middle"))
    b.append(_text(160, 105, t["provider"][1], fill=MUTED, anchor="middle"))

    b.append(_box(20, 150, 620, 300, fill="none", stroke=LINE, dash="6 5", radius=12))
    b.append(_text(36, 172, t["machine"], fill=MUTED, weight="bold"))

    b.append(_arrow(160, 188, 160, 120, both=True))
    b.append(_text(170, 140, t["prompts"], fill=MUTED))

    b.append(_box(50, 190, 220, 110, stroke=MUTED))
    a = t["assistant"]
    b.append(_text(160, 216, a[0], size=14, weight="bold", anchor="middle"))
    b.append(_text(160, 238, a[1], fill=MUTED, anchor="middle"))
    b.append(_text(160, 254, a[2], fill=MUTED, anchor="middle"))
    b.append(_text(160, 282, t["assistant_job"], anchor="middle"))

    b.append(_box(390, 190, 220, 110, fill=ACCENT_FILL, stroke=ACCENT, width=2))
    s = t["server"]
    b.append(_text(500, 216, s[0], size=14, fill=ACCENT, weight="bold", anchor="middle"))
    for i, line in enumerate(s[1:]):
        b.append(_text(500, 242 + i * 18, line, anchor="middle"))

    b.append(_arrow(270, 228, 388, 228))
    b.append(_text(330, 220, t["calls"], fill=MUTED, anchor="middle"))
    b.append(_arrow(390, 262, 272, 262))
    b.append(_text(330, 280, t["returns"], fill=MUTED, anchor="middle"))

    b.append(_box(50, 350, 560, 70))
    b.append(_text(330, 378, t["project"][0], size=14, weight="bold", anchor="middle"))
    b.append(_text(330, 400, t["project"][1], fill=MUTED, anchor="middle"))
    b.append(_arrow(160, 300, 160, 348))
    b.append(_text(170, 329, t["reads"], fill=MUTED))
    b.append(_arrow(500, 300, 500, 348))
    b.append(_text(490, 329, t["reads_root"], fill=MUTED, anchor="end"))

    b.append(_box(720, 190, 160, 110, fill=NET_FILL, stroke=NET, width=2))
    o = t["osv"]
    b.append(_text(800, 222, o[0], size=14, fill=NET_TEXT, weight="bold", anchor="middle"))
    b.append(_text(800, 248, o[1], fill=NET_TEXT, anchor="middle"))
    b.append(_text(800, 264, o[2], fill=NET_TEXT, anchor="middle"))
    b.append(_arrow(610, 245, 718, 245, color=NET))
    b.append(_text(665, 265, t["osv_send"][0], fill=NET_TEXT, anchor="middle"))
    b.append(_text(665, 280, t["osv_send"][1], fill=NET_TEXT, anchor="middle"))
    b.append(_text(800, 322, t["osv_note"], fill=NET_TEXT, weight="bold", anchor="middle"))

    return _svg(900, 470, t["how_label"], b)


def _tool_box(b, x, y, w, h, tool, lines, accent=False):
    b.append(_box(x, y, w, h, fill=ACCENT_FILL if accent else "#FFFFFF", stroke=ACCENT, width=1.5))
    cx = x + w / 2
    b.append(
        _text(cx, y + 28, tool, size=13, fill=ACCENT, weight="bold", anchor="middle", font=MONO)
    )
    for i, line in enumerate(lines):
        b.append(_text(cx, y + 52 + i * 17, line, fill=MUTED, anchor="middle"))


def review_flow(t: dict, lang: str) -> str:
    b = [_text(32, 40, t["flow_title"], size=20, weight="bold")]
    b.append(_text(32, 62, t["flow_sub"], size=13, fill=MUTED))

    _tool_box(b, 24, 100, 176, 110, "plan_review", t["plan"], accent=True)

    b.append(_box(234, 84, 446, 166, fill="none", stroke=ACCENT, dash="6 5", radius=12))
    b.append(_text(250, 104, t["loop"], fill=ACCENT, weight="bold"))
    for i, (tool, key) in enumerate(
        (("get_rules", "rules"), ("get_playbook", "playbook"), ("run_checks", "checks"))
    ):
        _tool_box(b, 250 + i * 140, 116, 132, 96, tool, t[key])
    b.append(_text(457, 236, t["then"], fill=INK, anchor="middle"))

    b.append(_arrow(200, 155, 232, 155, color=ACCENT))
    b.append(_arrow(680, 155, 712, 155, color=ACCENT))

    _tool_box(b, 714, 100, 162, 110, "synthesize_report", t["report"], accent=True)

    b.append(_text(24, 290, t["agents_title"], size=14, weight="bold"))
    for i, agent in enumerate(AGENTS.values()):
        x = 24 + (i % 5) * 172
        y = 304 + (i // 5) * 44
        name = AGENT_NAMES_FR[agent.id] if lang == "fr" else agent.name
        b.append(_box(x, y, 164, 34, radius=8))
        b.append(_text(x + 12, y + 22, name, size=13))
        b.append(_text(x + 152, y + 22, str(len(agent.rules)), size=12, fill=MUTED, anchor="end"))

    note_y = 418
    b.append(
        f'<text x="24" y="{note_y}" font-family="{SANS}" font-size="12" fill="{MUTED}">'
        f'<tspan font-family="{MONO}" fill="{ACCENT}">list_agents</tspan>'
        f"{escape(t['agents_note_post'])}</text>"
    )

    return _svg(900, 440, t["flow_label"], b)


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    out.mkdir(parents=True, exist_ok=True)
    for lang, t in TEXT.items():
        (out / f"how-it-works.{lang}.svg").write_text(how_it_works(t), encoding="utf-8")
        (out / f"review-flow.{lang}.svg").write_text(review_flow(t, lang), encoding="utf-8")
    print(f"Wrote 4 diagrams to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
