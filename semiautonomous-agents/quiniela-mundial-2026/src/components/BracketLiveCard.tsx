"use client";

// AVA's live bracket analysis card. Mounted at the top of /bracket.
//
// Three sections in one glass-strong card:
//   - Header: AVA avatar + label + counter (N grupos confirmados / M proyectados / K/8 terceros).
//   - Cambios recientes: per-slot diff between the last snapshot we persisted
//     in localStorage and the freshly-computed slot states. First visit shows
//     nothing here — we only display deltas once we have a previous snapshot
//     to compare against.
//   - Escenarios que mueven el bracket: collapsible list of the top 5 what-if
//     outcomes for still-pending group fixtures, narrated by AVA.
//
// All narration is template-based (no LLM call). Snapshots are written under
// the key q26:bracket-snapshot-v1.

import { useEffect, useMemo, useState } from "react";
import Image from "next/image";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, ChevronDown, ChevronUp, ArrowRight, CalendarClock } from "lucide-react";
import { PlayerAvatar } from "@/components/PlayerAvatar";
import { PLAYERS, AI_PLAYER_ID } from "@/data/players";
import { flagUrl, getTeam } from "@/data/teams";
import { GROUP_FIXTURES } from "@/data/groups";
import { useLocale, intlLocale } from "@/lib/i18n";
import { useGroupRealResults } from "@/lib/real-results";
import {
  bracketSlotStates,
  whatIfScenarios,
  diffSnapshots,
  avaNarrateDeltas,
  avaNarrateScenario,
  avaNarrateState,
  confirmedGroupLetters,
  type SlotState,
  type SlotDelta,
} from "@/lib/bracket-scenarios";

const AI_PLAYER = PLAYERS.find(p => p.id === AI_PLAYER_ID)!;
const SNAPSHOT_KEY = "q26:bracket-snapshot-v1";

// localStorage payload — minimal so it doesn't bloat.
type StoredSnapshot = {
  v: 1;
  at: number;
  slots: Array<{ token: string; team: string | null }>;
};

function readSnapshot(): StoredSnapshot | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(SNAPSHOT_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as StoredSnapshot;
    if (parsed?.v !== 1 || !Array.isArray(parsed.slots)) return null;
    return parsed;
  } catch {
    return null;
  }
}

function writeSnapshot(states: SlotState[]) {
  if (typeof window === "undefined") return;
  try {
    const payload: StoredSnapshot = {
      v: 1,
      at: Date.now(),
      slots: states.map(s => ({ token: s.token, team: s.team })),
    };
    window.localStorage.setItem(SNAPSHOT_KEY, JSON.stringify(payload));
  } catch {
    /* private mode — silent */
  }
}

function slotLabelShort(token: string): string {
  if (token.startsWith("3rd")) return `Mejor 3° #${token.slice(3)}`;
  const pos = token[0];
  const letter = token.slice(1);
  if (pos === "1") return `1° Grupo ${letter}`;
  if (pos === "2") return `2° Grupo ${letter}`;
  return token;
}

function fixtureLookup(id: string) {
  return GROUP_FIXTURES.find(f => f.id === id);
}

export function BracketLiveCard() {
  const { results: real } = useGroupRealResults();
  const { locale, t } = useLocale();
  const [expanded, setExpanded] = useState(false);
  const [deltas, setDeltas] = useState<SlotDelta[]>([]);

  // Current bracket projection.
  const states = useMemo(() => bracketSlotStates(real), [real]);
  const scenarios = useMemo(() => whatIfScenarios(real), [real]);
  const confirmedGroups = useMemo(() => confirmedGroupLetters(real), [real]);

  // Snapshot diff: read previous on mount + every time `real` updates, then
  // overwrite with the fresh snapshot. The diff only renders when we had a
  // prior snapshot to compare against (first-visit = no deltas, by design).
  useEffect(() => {
    const prev = readSnapshot();
    if (prev) {
      const d = diffSnapshots(prev.slots, states);
      setDeltas(d);
    } else {
      setDeltas([]);
    }
    writeSnapshot(states);
  }, [states]);

  const deltaNarrations = useMemo(() => avaNarrateDeltas(deltas), [deltas]);
  const stateNarration = useMemo(
    () => avaNarrateState(states, confirmedGroups),
    [states, confirmedGroups],
  );

  // Header counters.
  const groupSlotsProjected = states.filter(
    s => !s.token.startsWith("3rd") && s.status === "projected",
  ).length;
  const thirdsConfirmed = states.filter(
    s => s.token.startsWith("3rd") && s.status === "confirmed",
  ).length;

  const top5 = scenarios.slice(0, 5);

  return (
    <section className="container-app pt-4 pb-2">
      <div
        className="glass-strong rounded-2xl p-4 md:p-5 relative overflow-hidden"
        style={{
          background:
            "linear-gradient(135deg, color-mix(in srgb, var(--accent-violet) 14%, var(--bg)) 0%, var(--bg) 70%)",
          boxShadow: "0 0 26px -10px color-mix(in srgb, var(--accent-violet) 60%, transparent)",
        }}
      >
        {/* HEADER */}
        <header className="flex items-start gap-3">
          <PlayerAvatar
            player={AI_PLAYER}
            size={42}
            rounded="rounded-2xl"
            textClass="text-lg"
            tint={0.22}
          />
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 flex-wrap">
              <span
                className="text-[10px] font-display font-bold uppercase tracking-[0.18em]"
                style={{ color: "var(--accent-violet)" }}
              >
                {t("bracket.ava.label", "ANÁLISIS DE AVA")}
              </span>
              <span className="chip" style={{ background: "var(--bg-tint)", color: "var(--ink-soft)" }}>
                <Sparkles size={10} /> live
              </span>
            </div>
            <p className="mt-1 text-[12px] md:text-[13px] text-[var(--ink-soft)] leading-snug">
              {stateNarration}
            </p>
          </div>
        </header>

        {/* COUNTERS */}
        <div className="mt-3 grid grid-cols-3 gap-2">
          <CounterPill
            label="Grupos confirmados"
            value={`${confirmedGroups.length}/12`}
            tone="mint"
          />
          <CounterPill
            label="Slots en proyección"
            value={String(groupSlotsProjected)}
            tone="amber"
          />
          <CounterPill
            label="Mejores 3° sellados"
            value={`${thirdsConfirmed}/8`}
            tone={thirdsConfirmed === 8 ? "mint" : "tint"}
          />
        </div>

        {/* DELTAS */}
        {deltas.length > 0 && (
          <div className="mt-4">
            <div className="text-[10px] font-display font-bold uppercase tracking-wider text-[var(--ink-muted)] mb-2">
              {t("bracket.recentChanges", "Cambios recientes")}
            </div>
            <ul className="flex flex-col gap-2">
              {deltas.slice(0, 6).map((d, i) => (
                <DeltaRow key={`${d.token}-${i}`} delta={d} narration={deltaNarrations[i] ?? ""} />
              ))}
            </ul>
          </div>
        )}

        {/* SCENARIOS */}
        {top5.length > 0 && (
          <div className="mt-4">
            <button
              type="button"
              onClick={() => setExpanded(v => !v)}
              className="w-full flex items-center justify-between gap-2 px-3 py-2 rounded-xl bg-[var(--bg-tint)] hover:bg-[color-mix(in_srgb,var(--accent-violet)_12%,var(--bg-tint))] transition-colors"
              aria-expanded={expanded}
            >
              <span className="text-[11px] font-display font-bold uppercase tracking-wider text-[var(--ink-soft)]">
                {t("bracket.scenarios.title", "Escenarios que mueven el bracket")}
              </span>
              <span className="flex items-center gap-1.5 text-[10px] text-[var(--ink-muted)]">
                <span className="tabular-nums font-bold">{top5.length}</span>
                {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </span>
            </button>
            <AnimatePresence initial={false}>
              {expanded && (
                <motion.ul
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.25 }}
                  className="flex flex-col gap-2 mt-2 overflow-hidden"
                >
                  {top5.map((s, i) => (
                    <ScenarioRow
                      key={`${s.fixtureId}-${s.pick}-${i}`}
                      scenario={s}
                      locale={locale}
                    />
                  ))}
                </motion.ul>
              )}
            </AnimatePresence>
          </div>
        )}
      </div>
    </section>
  );
}

// ---------------------------------------------------------------------------
//                              SUB-COMPONENTS
// ---------------------------------------------------------------------------

function CounterPill({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: "mint" | "amber" | "tint";
}) {
  const bg =
    tone === "mint"
      ? "rgba(20,241,149,0.14)"
      : tone === "amber"
        ? "rgba(251,191,36,0.18)"
        : "var(--bg-tint)";
  const fg =
    tone === "mint"
      ? "rgb(5,122,85)"
      : tone === "amber"
        ? "rgb(146,90,7)"
        : "var(--ink-soft)";
  return (
    <div
      className="rounded-xl px-2.5 py-2 flex flex-col items-start gap-0.5"
      style={{ background: bg }}
    >
      <span className="font-display text-[15px] font-bold tabular-nums leading-none" style={{ color: fg }}>
        {value}
      </span>
      <span className="text-[9px] uppercase tracking-wider font-bold opacity-80" style={{ color: fg }}>
        {label}
      </span>
    </div>
  );
}

function TeamPip({ code }: { code: string | null }) {
  const team = code ? getTeam(code) : null;
  if (!team) {
    return (
      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-[var(--bg-tint)] text-[10px] text-[var(--ink-muted)] font-display font-bold">
        ?
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-[var(--bg-tint)] text-[10px] font-display font-bold text-[var(--ink)]">
      <Image
        src={flagUrl(team.iso2, 24)}
        alt={team.name}
        width={12}
        height={12}
        className="rounded-sm object-cover ring-1 ring-[var(--line)]"
        unoptimized
      />
      {team.code}
    </span>
  );
}

function DeltaRow({ delta, narration }: { delta: SlotDelta; narration: string }) {
  return (
    <li className="rounded-xl px-3 py-2 bg-[var(--bg-tint)]/70 flex flex-col gap-1.5">
      <div className="flex items-center gap-2 flex-wrap">
        <span
          className="text-[9px] font-display font-bold uppercase tracking-wider px-1.5 py-0.5 rounded"
          style={{ background: "var(--accent-violet)", color: "white" }}
        >
          {slotLabelShort(delta.token)}
        </span>
        <TeamPip code={delta.before} />
        <ArrowRight size={11} className="text-[var(--ink-muted)]" />
        <TeamPip code={delta.after} />
      </div>
      {narration && (
        <p className="text-[11px] leading-snug text-[var(--ink-soft)]">{narration}</p>
      )}
    </li>
  );
}

function ScenarioRow({
  scenario,
  locale,
}: {
  scenario: ReturnType<typeof whatIfScenarios>[number];
  locale: ReturnType<typeof useLocale>["locale"];
}) {
  const fx = fixtureLookup(scenario.fixtureId);
  const dateLabel = useMemo(() => {
    if (!fx) return scenario.fixtureId;
    // Build a CDMX wall-clock ISO string from the fixture's local fields, then
    // let Intl format it in the user's locale.
    const iso = `${fx.date}T${fx.kickoffLocal}:00-06:00`;
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return scenario.fixtureId;
    return new Intl.DateTimeFormat(intlLocale(locale), {
      weekday: "short",
      day: "numeric",
      month: "short",
      hour: "numeric",
      minute: "2-digit",
      timeZone: "America/Mexico_City",
    }).format(d);
  }, [fx, locale, scenario.fixtureId]);

  const narration = useMemo(() => avaNarrateScenario(scenario), [scenario]);

  return (
    <li className="rounded-xl px-3 py-2.5 bg-[var(--bg)] ring-1 ring-[var(--line)] flex flex-col gap-1.5">
      <div className="flex items-center gap-2 flex-wrap text-[10px] text-[var(--ink-muted)] font-semibold">
        <CalendarClock size={11} className="opacity-70" />
        <span className="tabular-nums">{dateLabel}</span>
        <span className="opacity-50">·</span>
        <span className="font-display font-bold text-[var(--ink-soft)]">
          {scenario.homeCode} vs {scenario.awayCode}
        </span>
        <span
          className="ml-auto text-[9px] font-display font-bold uppercase tracking-wider px-1.5 py-0.5 rounded"
          style={{
            background: "rgba(94,91,255,0.14)",
            color: "var(--accent-violet)",
          }}
        >
          {scenario.changedSlots.length} {scenario.changedSlots.length === 1 ? "slot" : "slots"}
        </span>
      </div>
      <p className="text-[12px] leading-snug text-[var(--ink)]">{narration}</p>
    </li>
  );
}
