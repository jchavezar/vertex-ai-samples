"""ADK agent — Quiniela Charales 2026. Gemini 2.5 Flash + google_search."""
import os
from typing import Any, Optional

import requests
from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools import FunctionTool

# ── System prompt ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
Eres el asistente de la Quiniela Charales 2026. Eres rápido, preciso y amigable.

## TONO (NO NEGOCIABLE)
- Profesional y directo. Sin slang, sin groserías, sin "wey", "cabrón", "no mames". Jamás.
- Responde lo que te preguntan. Sin preámbulos. Sin "¡Excelente pregunta!".
- Breve por defecto: 1-3 oraciones. Si piden detalle, usa listas markdown.
- Tuteo natural, español mexicano culto.

## CONOCIMIENTO
- Responde de tu conocimiento. Si algo es muy reciente y no estás seguro, dilo claramente.

## TORNEO
- 48 selecciones, 12 grupos de 4, 104 partidos. Sede: México / EUA / Canadá.
- Inauguración: 11 jun 2026, Azteca, MEX vs RSA. Final: 19 jul 2026, MetLife NJ.
- Avanza: Top 2 de cada grupo + 8 mejores terceros → 32avos.

## QUINIELA CHARALES
- Jugadores: Jesús, Xavi, Akyno, Charal, Aldo, Darin, Tilapia, Jochabe, MVictor.
- Puntos grupos: 3 pts por 1X2 correcto; +2 pts marcador exacto.
- Bracket: R32=3 · Octavos=5 · Cuartos=10 · Semis=15 · 3er lugar=8 · Final=20.
- Bonus campeón: 30 pts | Subcampeón: 15 pts.

## FORMATO (mobile ~340 px)
- Negritas solo para datos clave. Listas para 3+ items. Tablas máx 4 columnas.
- Sin encabezados # salvo respuestas largas con secciones claras.
- No repitas la pregunta antes de responder.
"""

AI_FILL_BLOCK = """\

## MODO AI-FILL
Se activa cuando el usuario pide "lléname la quiniela", "ayúdame a llenar" o manda "AI_FILL_START".

Flujo:
1. Pide sus equipos favoritos en orden de importancia (máx 5, códigos FIFA 3 letras).
2. Pregunta si quiere fijar algún marcador específico (ej: MEX 2-0 RSA).
3. Llama propose_ai_picks(player_id, favorites, fill_only_empty=True, manual_scores=[...]).
4. Muestra los proposals agrupados por Grupo en markdown compacto:
   **Grupo A** — `A-M1` MEX vs RSA → **MEX** (2-0)
5. Pregunta si quiere cambiar algo. Si sí, llama propose_ai_picks de nuevo con los cambios.
6. Al confirmar ("va", "guarda"), llama commit_ai_picks con los picks finales.
7. Confirma cuántos picks se guardaron y cuántos se respetaron (si ya existían).

Reglas: NUNCA inventes picks, NUNCA hagas commit sin confirmación explícita.
"""

IDENTITY_TEMPLATE = """\

## USUARIO ACTUAL
Hablas con **{name}** (id: {player_id}). Usa siempre ese nombre; no lo confundas con otros.
"""


def _build_instruction(ctx: ReadonlyContext) -> str:
    state = ctx.state if hasattr(ctx, "state") else {}
    name = (state.get("player_name") if state else None) or "uno de los Charales"
    player_id = (state.get("player_id") if state else None) or "?"
    return SYSTEM_PROMPT + AI_FILL_BLOCK + IDENTITY_TEMPLATE.format(name=name, player_id=player_id)


# ── Tools (AI-fill callbacks to Next.js) ────────────────────────────────────

NEXTJS_URL = os.environ.get("NEXTJS_URL", "https://quiniela-charales-2026-254356041555.us-central1.run.app").rstrip("/")
AGENT_SECRET = os.environ.get("Q26_AGENT_SECRET", "")


def _post(path: str, payload: dict) -> dict:
    if not AGENT_SECRET:
        return {"ok": False, "error": "Q26_AGENT_SECRET not set"}
    try:
        r = requests.post(
            f"{NEXTJS_URL}{path}",
            json=payload,
            headers={"x-q26-agent-secret": AGENT_SECRET, "Content-Type": "application/json"},
            timeout=15,
        )
        try:
            return r.json()
        except Exception:
            return {"ok": False, "error": f"non-JSON {r.status_code}: {r.text[:200]}"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _get(path: str) -> dict:
    try:
        r = requests.get(f"{NEXTJS_URL}{path}", timeout=15)
        try:
            return r.json()
        except Exception:
            return {"ok": False, "error": f"non-JSON {r.status_code}: {r.text[:200]}"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def get_current_picks(player_id: str) -> dict:
    """Lee los picks actuales del jugador desde Firestore.

    Args:
        player_id: id del jugador (ej: "jesus").
    Returns:
        dict con ok y picks.
    """
    return _get(f"/api/predictions?playerId={player_id}")


def propose_ai_picks(
    player_id: str,
    favorites: list[str],
    fill_only_empty: bool = True,
    manual_scores: Optional[list[dict]] = None,
) -> dict:
    """Genera propuesta de picks sin escribir en Firestore.

    Args:
        player_id: id del jugador.
        favorites: códigos FIFA en orden de preferencia (máx 5).
        fill_only_empty: si True, no propone para fixtures ya llenados manualmente.
        manual_scores: lista de {fixtureId, homeGoals, awayGoals} fijados por el usuario.
    Returns:
        dict con proposals[], counts.
    """
    payload: dict[str, Any] = {
        "playerId": player_id,
        "favorites": favorites or [],
        "fillOnlyEmpty": bool(fill_only_empty),
    }
    if manual_scores:
        payload["manualScores"] = manual_scores
    return _post("/api/ai-predictions/propose", payload)


def commit_ai_picks(player_id: str, picks: list[dict], fill_only_empty: bool = True) -> dict:
    """Persiste los picks en Firestore (source='ai'). Solo llamar con confirmación explícita.

    Args:
        player_id: id del jugador.
        picks: lista de {fixtureId, pick (H/D/A), homeGoals, awayGoals}.
        fill_only_empty: si True, salta fixtures con pick manual existente.
    Returns:
        dict con ok, written, skipped.
    """
    return _post("/api/ai-predictions/commit", {
        "playerId": player_id,
        "picks": picks or [],
        "fillOnlyEmpty": bool(fill_only_empty),
    })


# ── Agent ────────────────────────────────────────────────────────────────────

root_agent = LlmAgent(
    name="quiniela_assistant",
    model="gemini-2.5-flash",
    description="Asistente de la Quiniela Charales 2026.",
    instruction=_build_instruction,
    tools=[FunctionTool(get_current_picks), FunctionTool(propose_ai_picks), FunctionTool(commit_ai_picks)],
)
