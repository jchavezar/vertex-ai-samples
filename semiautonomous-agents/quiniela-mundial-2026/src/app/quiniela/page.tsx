"use client";

import Link from "next/link";
import Image from "next/image";
import { motion, AnimatePresence } from "framer-motion";
import { Suspense, useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Crown, CheckCircle2, AlertCircle, UserCircle2, Minus, Plus, Trophy, Sparkles, ChevronDown, Calendar, MapPin, Lock, Swords, Bot, Undo2, Eye, Radio } from "lucide-react";
import { GROUP_LETTERS, groupFixtures, allGroupFixtures, type GroupLetter, type GroupFixture } from "@/data/groups";
import { TEAMS, flagUrl } from "@/data/teams";
import { usePlayer } from "@/lib/player-context";
import { PlayerAvatar } from "@/components/PlayerAvatar";
import {
  loadPredictions, savePredictions, firePickToServer, fillStats, bracketRoundComplete,
  championBonusPoints, runnerUpBonusPoints, currentChampionBonusIfChangedNow,
  loadOnePredictionFromServer, hydratePredictionsFromServer,
  type PlayerPredictions, type GroupPrediction, type Pick1X2, type BracketPick,
  type SyncStatus, type SyncEvent,
} from "@/lib/predictions";
import { CHAMPION_PHASE_LABEL, SCORING, type ChampionLockRound } from "@/data/tournament";
import { isFixtureLocked, isBracketRoundLocked, isKOSlotLocked, fixtureKickoffMs } from "@/lib/fixture-time";
import { computePlayerOdds, probLabel, type PlayerOdds } from "@/lib/probability";
import { matchProbability } from "@/data/team-strength";
import { aiPickCount, undoAiPicks } from "@/lib/ai-pick-helpers";
import { computeAllStandings, computeR32Pairings, pairWinners, type Standing } from "@/lib/standings";
import { useGroupRealResults } from "@/lib/real-results";
import { useLiveScoreboard, type LiveFixture } from "@/lib/live-scoreboard";
import { useAllPicksByFixture, type PlayerLite } from "@/lib/all-picks";
import { KickoffCountdown } from "@/components/KickoffCountdown";
import { PushActivationInline } from "@/components/PushActivationFlow";
import { track } from "@/lib/track";

export default function QuinielaPage() {
  return (
    <Suspense fallback={null}>
      <MundialQuinielaView />
    </Suspense>
  );
}

function MundialQuinielaView() {
  const { currentPlayer, players, ready } = usePlayer();
  const searchParams = useSearchParams();
  const viewId = searchParams.get("view");
  const focusFixtureId = searchParams.get("fixture");
  const viewedPlayer = viewId ? players.find(p => p.id === viewId) ?? null : null;
  const isViewingOther = !!(viewedPlayer && currentPlayer && viewedPlayer.id !== currentPlayer.id);
  const displayPlayer = isViewingOther ? viewedPlayer : currentPlayer;
  const readOnly = isViewingOther;
  const [active, setActive] = useState<GroupLetter>("A");
  const [data, setData] = useState<PlayerPredictions | null>(null);
  const [savedFlash, setSavedFlash] = useState(false);
  const [highlightFx, setHighlightFx] = useState<string | null>(null);
  const scrolledFxRef = useRef<string | null>(null);
  const allGroupFx = useMemo(() => allGroupFixtures(), []);
  const { byId: liveById } = useLiveScoreboard();
  const { byFixture: pickersByFx } = useAllPicksByFixture();

  useEffect(() => {
    if (!focusFixtureId) return;
    const fx = allGroupFx.find(f => f.id === focusFixtureId);
    if (fx) setActive(fx.group as GroupLetter);
  }, [focusFixtureId, allGroupFx]);

  useEffect(() => {
    if (!focusFixtureId || !data) return;
    const fx = allGroupFx.find(f => f.id === focusFixtureId);
    if (!fx || active !== fx.group) return;
    if (scrolledFxRef.current === focusFixtureId) return;
    scrolledFxRef.current = focusFixtureId;
    requestAnimationFrame(() => {
      const el = document.getElementById(`fx-${focusFixtureId}`);
      if (!el) return;
      el.scrollIntoView({ behavior: "smooth", block: "start" });
      setHighlightFx(focusFixtureId);
      setTimeout(() => setHighlightFx(null), 2400);
    });
  }, [focusFixtureId, data, active, allGroupFx]);

  useEffect(() => {
    if (!displayPlayer) return;
    // Optimistic local render first (instant), then sync with Firestore.
    // Own player: use hydratePredictionsFromServer which merges per-fixture and
    // re-pushes any local-only picks (unsynced due to 401/network blip). This
    // fixes the race where saveLocalMirror(serverData) would wipe unsynced picks
    // that hydratePredictionsFromServer had already preserved in localStorage.
    // Other player: plain read (no local storage involvement).
    setData(loadPredictions(displayPlayer.id));
    let cancelled = false;
    if (isViewingOther) {
      loadOnePredictionFromServer(displayPlayer.id).then(p => {
        if (cancelled) return;
        setData(p);
      });
    } else {
      hydratePredictionsFromServer(displayPlayer.id).then(() => {
        if (cancelled) return;
        setData(loadPredictions(displayPlayer.id));
      }).catch(() => {});
    }
    return () => { cancelled = true; };
  }, [displayPlayer, isViewingOther]);

  const stats = useMemo(() => data ? fillStats(data) : null, [data]);

  function setPick(fixtureId: string, pick: Pick1X2) {
    if (readOnly || !data || !displayPlayer) return;
    const fx = allGroupFx.find(f => f.id === fixtureId);
    if (fx && isFixtureLocked(fx)) return;
    const prev = data.group[fixtureId];
    // Toggle off if clicking the same pick again — use legacy bulk sync for removal
    if (prev?.pick === pick) {
      const { [fixtureId]: _, ...rest } = data.group;
      const updated: PlayerPredictions = { ...data, group: rest };
      setData(updated); savePredictions(updated); flash();
      track("pick_made", { fixtureId, pick: null, hasScore: false });
      return;
    }
    const next: GroupPrediction = { ...prev, pick, source: "manual", aiAt: undefined };
    if (prev?.pick && prev.pick !== pick) {
      next.homeGoals = undefined;
      next.awayGoals = undefined;
    }
    const updated: PlayerPredictions = { ...data, group: { ...data.group, [fixtureId]: next } };
    // Write to localStorage immediately (optimistic) + legacy fallback sync
    setData(updated); savePredictions(updated); flash();
    // Also fire directly to server without debounce — primary write path
    firePickToServer(displayPlayer.id, fixtureId, pick).then(result => {
      if (result.error === "locked") {
        // Server says locked — revert optimistic state
        setData(data);
      }
    });
    track("pick_made", { fixtureId, pick, hasScore: next.homeGoals !== undefined && next.awayGoals !== undefined });
  }

  function setExact(fixtureId: string, side: "home" | "away", value: number) {
    if (readOnly || !data) return;
    const fx = allGroupFx.find(f => f.id === fixtureId);
    if (fx && isFixtureLocked(fx)) return;
    const prev = data.group[fixtureId];
    const v = Math.max(0, Math.min(20, value));
    const homeGoals = side === "home" ? v : (prev?.homeGoals ?? 0);
    const awayGoals = side === "away" ? v : (prev?.awayGoals ?? 0);
    if (prev?.homeGoals === homeGoals && prev?.awayGoals === awayGoals) return;
    const derivedPick: Pick1X2 = homeGoals > awayGoals ? "H" : homeGoals < awayGoals ? "A" : "D";
    const next: GroupPrediction = { ...prev, homeGoals, awayGoals, pick: derivedPick, source: "manual", aiAt: undefined };
    const updated: PlayerPredictions = { ...data, group: { ...data.group, [fixtureId]: next } };
    setData(updated); savePredictions(updated); flash();
    track("pick_made", { fixtureId, pick: derivedPick, hasScore: true });
  }

  function setChampion(code: string | undefined) {
    if (readOnly || !data) return;
    const { round } = currentChampionBonusIfChangedNow();
    // Si quita el pick, también limpia el sello de fase.
    // Si lo cambia (o lo pone por primera vez), se sella la fase actual.
    const sameAsBefore = code !== undefined && code === data.champion;
    const updated: PlayerPredictions = {
      ...data,
      champion: code,
      championLockedAt: code === undefined ? undefined : sameAsBefore ? data.championLockedAt : round,
    };
    setData(updated); savePredictions(updated); flash();
  }
  function setRunnerUp(code: string | undefined) {
    if (readOnly || !data) return;
    const { round } = currentChampionBonusIfChangedNow();
    const sameAsBefore = code !== undefined && code === data.runnerUp;
    const updated: PlayerPredictions = {
      ...data,
      runnerUp: code,
      runnerUpLockedAt: code === undefined ? undefined : sameAsBefore ? data.runnerUpLockedAt : round,
    };
    setData(updated); savePredictions(updated); flash();
  }

  function setBracketWinner(round: "R32" | "R16" | "QF" | "SF", idx: number, total: number, code: string) {
    if (readOnly || !data) return;
    if (round === "R32" ? isKOSlotLocked(`R32-${idx + 1}`) : isBracketRoundLocked(round)) return;
    const current = (data.bracket[round] ?? []).slice();
    while (current.length < total) current.push("");
    if (current[idx] === code) current[idx] = "";
    else current[idx] = code;
    // Trim trailing empties for cleanliness but keep length === total for completion checks
    const nextBracket: BracketPick = { ...data.bracket, [round]: current };
    // Wipe downstream rounds if upstream change breaks them
    if (round === "R32") { nextBracket.R16 = []; nextBracket.QF = []; nextBracket.SF = []; nextBracket.THIRD = undefined; nextBracket.FINAL = undefined; }
    if (round === "R16") { nextBracket.QF = []; nextBracket.SF = []; nextBracket.THIRD = undefined; nextBracket.FINAL = undefined; }
    if (round === "QF")  { nextBracket.SF = []; nextBracket.THIRD = undefined; nextBracket.FINAL = undefined; }
    if (round === "SF")  { nextBracket.THIRD = undefined; nextBracket.FINAL = undefined; }
    const updated: PlayerPredictions = { ...data, bracket: nextBracket };
    setData(updated); savePredictions(updated); flash();
    track("bracket_pick", { round, code });
  }

  function setBracketSingle(field: "THIRD" | "FINAL", code: string) {
    if (readOnly || !data) return;
    if (isBracketRoundLocked(field)) return;
    const current = data.bracket[field];
    const nextBracket: BracketPick = { ...data.bracket, [field]: current === code ? undefined : code };
    const updated: PlayerPredictions = { ...data, bracket: nextBracket };
    setData(updated); savePredictions(updated); flash();
    track("bracket_pick", { round: field, code });
  }

  function flash() {
    setSavedFlash(true);
    setTimeout(() => setSavedFlash(false), 1200);
  }

  if (!ready) return null;

  if (!displayPlayer) {
    return (
      <div className="container-app py-20">
        <div className="max-w-md mx-auto glass-strong rounded-3xl p-10 text-center">
          <div className="w-16 h-16 rounded-2xl bg-[var(--bg-tint)] grid place-items-center mx-auto mb-4">
            <UserCircle2 size={28} />
          </div>
          <h1 className="font-display text-2xl font-bold">Identifícate primero</h1>
          <p className="mt-2 text-[var(--ink-soft)]">
            Para llenar tu quiniela necesitamos saber quién eres. Elige tu nombre en la lista.
          </p>
          <Link href="/jugadores" className="btn btn-primary mt-6">Elegir jugador →</Link>
        </div>
      </div>
    );
  }

  const fixtures = groupFixtures(active);

  return (
    <div className="bg-canvas">
      {isViewingOther && (
        <section className="container-app pt-4">
          <div className="glass-strong rounded-2xl px-4 py-3 flex items-center justify-between gap-3 border border-[var(--ink)]/15">
            <div className="flex items-center gap-2 text-sm">
              <Eye size={16} />
              <span>Estás viendo la quiniela de <strong>{displayPlayer?.name}</strong> en modo lectura.</span>
            </div>
            <Link href="/quiniela" prefetch={false} className="btn btn-ghost text-xs whitespace-nowrap">
              Volver a la mía →
            </Link>
          </div>
        </section>
      )}
      {/* Header */}
      <section className="container-app pt-8 md:pt-12 pb-4">
        <div className="flex flex-col md:flex-row md:items-end gap-6 md:justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <PlayerAvatar player={displayPlayer} size={40} className="rounded-2xl" enableLightbox />
              <div>
                <div className="text-xs uppercase tracking-[0.18em] text-[var(--ink-muted)]">Quiniela de</div>
                <div className="font-display font-semibold leading-none">{displayPlayer.name}</div>
              </div>
            </div>
            <h1 className="font-display text-3xl md:text-5xl font-bold leading-tight">
              {readOnly ? (
                <><span className="grad-text">Sus predicciones.</span> <br className="md:hidden" />Su lana.</>
              ) : (
                <><span className="grad-text">Tus predicciones.</span> <br className="md:hidden" />Tu lana.</>
              )}
            </h1>
          </div>

          {/* Progress card */}
          <div className="glass-strong rounded-3xl p-4 md:p-5 min-w-[280px] md:min-w-[300px]">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs uppercase tracking-[0.18em] text-[var(--ink-muted)]">Avance</span>
              <span className="font-display font-bold text-lg tabular-nums">{stats?.percent ?? 0}%</span>
            </div>
            <div className="h-2 rounded-full bg-[var(--bg-tint)] overflow-hidden">
              <motion.div
                className="h-full rounded-full"
                animate={{ width: `${stats?.percent ?? 0}%` }}
                transition={{ duration: .4 }}
                style={{ background: `linear-gradient(90deg, ${displayPlayer.accent}, var(--accent-violet))` }}
              />
            </div>
            <div className="mt-2 flex items-center justify-between text-xs text-[var(--ink-soft)]">
              <span className="tabular-nums">{stats?.groupFilled ?? 0} / {stats?.groupTotal ?? 72} partidos</span>
              <span>{stats?.champion ? <>Campeón: <strong>{stats.champion}</strong></> : "Sin campeón"}</span>
            </div>
          </div>
        </div>
      </section>

      {/* Save flash + cloud sync status */}
      <AnimatePresence>
        {savedFlash && (
          <motion.div
            initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}
            className="fixed top-20 left-1/2 -translate-x-1/2 z-50 glass-strong rounded-full px-4 py-2 flex items-center gap-2 text-sm font-semibold shadow-lg"
          >
            <CheckCircle2 size={14} className="text-[var(--accent-mint)]" /> Guardado
          </motion.div>
        )}
      </AnimatePresence>
      {displayPlayer && !readOnly && <CloudSyncBadge playerId={displayPlayer.id} />}

      {/* AI picks banner */}
      {data && aiPickCount(data) > 0 && !readOnly && (
        <section className="container-app pt-2">
          <div className="glass-strong rounded-2xl px-4 py-3 flex items-center justify-between gap-3 border border-[var(--accent-violet)]/30">
            <div className="flex items-center gap-2 text-sm">
              <Bot size={16} className="text-[var(--accent-violet)]" />
              <span>La AI te ayudó con <strong>{aiPickCount(data)}</strong> picks · puedes deshacerlos sin perder los tuyos manuales.</span>
            </div>
            <button
              onClick={() => {
                if (!data) return;
                if (!confirm(`¿Deshacer ${aiPickCount(data)} picks de la AI? Tus picks manuales se quedan tal cual.`)) return;
                const cleaned = undoAiPicks(data);
                setData(cleaned);
                savePredictions(cleaned);
                flash();
              }}
              className="btn btn-ghost text-xs flex items-center gap-1.5"
            >
              <Undo2 size={12} /> Deshacer AI
            </button>
          </div>
        </section>
      )}

      {/* Inline push activation nudge — only when user still has unfilled picks
          and isn't in read-only mode. One-shot per session (see PushActivationFlow). */}
      {!readOnly && stats && stats.percent < 100 && (
        <section className="container-app pt-2">
          <PushActivationInline placement="quiniela" />
        </section>
      )}

      {/* Group tabs */}
      <section className="container-app sticky top-20 z-30 pt-4 pb-3">
        <div className="glass-strong rounded-full p-1.5 flex gap-1 max-w-full overflow-x-auto no-scrollbar">
          {GROUP_LETTERS.map(letter => {
            const fxs = groupFixtures(letter);
            const filled = fxs.filter(f => data?.group[f.id]?.pick).length;
            const isActive = active === letter;
            const done = filled === fxs.length;
            return (
              <button
                key={letter}
                onClick={() => setActive(letter)}
                className={`shrink-0 px-3.5 py-1.5 rounded-full text-sm font-display font-bold transition-colors flex items-center gap-1.5 ${isActive ? "bg-[var(--ink)] text-white" : "text-[var(--ink-soft)] hover:text-[var(--ink)]"}`}
              >
                {letter}
                {done && <CheckCircle2 size={11} className="text-[var(--accent-mint)]" />}
              </button>
            );
          })}
        </div>
      </section>

      {/* Group fixtures */}
      <section className="container-app pt-2 pb-10">
        <div className="grid lg:grid-cols-2 gap-3">
          {fixtures.map((fx, idx) => (
            <MatchRow
              key={fx.id}
              fixture={fx}
              prediction={data?.group[fx.id]}
              accent={displayPlayer.accent}
              locked={isFixtureLocked(fx) || readOnly}
              live={liveById[fx.id]}
              pickers={pickersByFx[fx.id]}
              onPick={(pk) => setPick(fx.id, pk)}
              onExact={(side, v) => setExact(fx.id, side, v)}
              delay={idx * 0.03}
              highlight={highlightFx === fx.id}
            />
          ))}
        </div>

        {/* Bracket / standings derived from the player's picks */}
        {data && (
          <BracketSection
            data={data}
            accent={displayPlayer.accent}
            readOnly={readOnly}
            onPickWinner={setBracketWinner}
            onPickSingle={setBracketSingle}
            onApplyBracket={(nextBracket) => {
              const updated: PlayerPredictions = { ...data, bracket: nextBracket };
              setData(updated); savePredictions(updated);
            }}
          />
        )}

        {/* Champion / Runner-up section */}
        <div className="mt-10 grid md:grid-cols-2 gap-4">
          <ChampionPicker
            label="Campeón del mundo"
            basePoints={SCORING.bonusChampion}
            icon={<Crown size={20} />}
            color="#D4AF37"
            value={data?.champion}
            lockedAt={data?.championLockedAt}
            kind="champion"
            readOnly={readOnly}
            onChange={setChampion}
          />
          <ChampionPicker
            label="Subcampeón"
            basePoints={SCORING.bonusRunnerUp}
            icon={<Trophy size={20} />}
            color="#94A3B8"
            value={data?.runnerUp}
            lockedAt={data?.runnerUpLockedAt}
            kind="runnerUp"
            readOnly={readOnly}
            onChange={setRunnerUp}
          />
        </div>

        {/* Tu ticket: probabilidades + expected points */}
        {data && <TicketOdds data={data} accent={displayPlayer.accent} />}

        {/* Helper text */}
        <div className="mt-8 glass rounded-2xl p-5 flex items-start gap-3 text-sm">
          <AlertCircle size={18} className="text-[var(--accent-violet)] shrink-0 mt-0.5" />
          <div>
            <p className="text-[var(--ink)] font-semibold mb-1">Cómo se juega</p>
            <p className="text-[var(--ink-soft)]">
              <strong>{SCORING.pickWinner} pts</strong> por acertar 1X2 (gana / empata / pierde) en fase de grupos. El marcador exacto <strong>no suma puntos</strong> — se guarda como desempate para tu tabla. El <strong>bracket no suma</strong> — lo único que paga ahí es atinarle al <strong>campeón</strong> (hasta +{SCORING.bonusChampion} pts, baja conforme avanza el torneo). Se guarda automático.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

// ----- Match row with 1X2 + optional exact score -----

function MatchRow({
  fixture, prediction, accent, locked, live, pickers, onPick, onExact, delay, highlight,
}: {
  fixture: GroupFixture;
  prediction?: GroupPrediction;
  accent: string;
  locked: boolean;
  live?: LiveFixture;
  pickers?: { H: PlayerLite[]; D: PlayerLite[]; A: PlayerLite[] };
  onPick: (pick: Pick1X2) => void;
  onExact: (side: "home" | "away", value: number) => void;
  delay: number;
  highlight?: boolean;
}) {
  const [showScore, setShowScore] = useState(false);
  const home = TEAMS.find(t => t.code === fixture.home)!;
  const away = TEAMS.find(t => t.code === fixture.away)!;
  const picked = prediction?.pick;
  const hasExact = Number.isFinite(prediction?.homeGoals) && Number.isFinite(prediction?.awayGoals);
  const probs = matchProbability(fixture.home, fixture.away);

  const kickoff = new Date(fixtureKickoffMs(fixture));
  const [tzLabels, setTzLabels] = useState<{ date: string; time: string } | null>(null);
  useEffect(() => {
    setTzLabels({
      date: kickoff.toLocaleDateString("es-MX", { weekday: "short", day: "numeric", month: "short" }),
      time: kickoff.toLocaleTimeString("es-MX", { hour: "2-digit", minute: "2-digit" }),
    });
  }, [kickoff.getTime()]);
  const dateLabel = tzLabels?.date ?? `${fixture.date.slice(5, 7)}/${fixture.date.slice(8, 10)}`;
  const timeLabel = tzLabels?.time ?? fixture.kickoffLocal;

  const isLiveNow = live?.phase === "live";
  const isFinal = live?.phase === "final";
  const hg = live?.homeGoals;
  const ag = live?.awayGoals;
  const hasScore = (isLiveNow || isFinal) && hg !== undefined && ag !== undefined;
  const leadingPick: Pick1X2 | null = hasScore
    ? (hg! > ag! ? "H" : hg! < ag! ? "A" : "D")
    : null;

  // Verdict for finished matches
  type Verdict = "exact" | "hit" | "miss" | "empty";
  const verdict: Verdict | null = isFinal && leadingPick
    ? (!picked ? "empty"
      : picked === leadingPick && hasExact && prediction?.homeGoals === hg && prediction?.awayGoals === ag ? "exact"
      : picked === leadingPick ? "hit"
      : "miss")
    : null;
  const verdictStyle = verdict === "exact"
    ? { label: "★ EXACTO", bg: "linear-gradient(135deg, #D4AF37, #F59E0B)", text: "white" }
    : verdict === "hit"
    ? { label: "✓ ACERTASTE", bg: "linear-gradient(135deg, #10B981, #14F195)", text: "white" }
    : verdict === "miss"
    ? { label: "✗ MAMASTE", bg: "linear-gradient(135deg, #F43F5E, #FB7185)", text: "white" }
    : null;

  return (
    <motion.div
      id={`fx-${fixture.id}`}
      initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .25, delay }}
      className={`glass rounded-3xl p-4 scroll-mt-40 transition-shadow ${locked && !isLiveNow && !isFinal ? "opacity-70" : ""}`}
      style={
        highlight
          ? { boxShadow: `0 0 0 3px ${accent}, 0 14px 30px -16px rgba(15,23,42,0.4)` }
          : isLiveNow
            ? { boxShadow: "0 0 0 2px rgba(244,63,94,0.35)" }
            : undefined
      }
    >
      {/* Meta row */}
      <div className="flex items-center justify-between gap-2 mb-3 text-[11px] text-[var(--ink-muted)]">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="chip">J{fixture.matchday}</span>
          <span className="flex items-center gap-1"><Calendar size={11} />{dateLabel} · {timeLabel}</span>
          {!locked && !isLiveNow && !isFinal && <KickoffCountdown kickoff={kickoff} />}
        </div>
        <div className="flex items-center gap-1.5 flex-wrap justify-end">
          {prediction?.source === "ai" && (
            <span className="text-[10px] flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-[var(--accent-violet)]/15 text-[var(--accent-violet)] font-bold uppercase tracking-wide whitespace-nowrap">
              <Bot size={10} /> AI
            </span>
          )}
          {isFinal ? (
            <Link
              href={`/partido/${fixture.id}`}
              onClick={e => e.stopPropagation()}
              className="text-[11px] flex items-center gap-1 px-2 py-0.5 rounded-full font-display font-bold uppercase tracking-wide hover:opacity-90 transition-opacity whitespace-nowrap"
              style={{ background: "var(--accent-mint, #14F195)", color: "white" }}
            >
              <CheckCircle2 size={11} /> Final {hasScore ? `${hg}–${ag}` : ""}
            </Link>
          ) : isLiveNow ? (
            <Link
              href={`/partido/${fixture.id}/live`}
              onClick={e => e.stopPropagation()}
              className="text-[11px] flex items-center gap-1 px-2 py-0.5 rounded-full font-display font-bold uppercase tracking-wide hover:opacity-90 transition-opacity whitespace-nowrap"
              style={{ background: "rgba(244,63,94,0.95)", color: "white" }}
            >
              <Radio size={11} className="animate-pulse" /> En vivo {live?.minute ? `· ${live.minute}'` : ""}
            </Link>
          ) : locked ? (
            <span className="text-[11px] flex items-center gap-1 text-[var(--ink-muted)] font-semibold whitespace-nowrap">
              <Lock size={11} /> Cerrado
            </span>
          ) : picked && (
            <span className="text-[11px] flex items-center gap-1 text-[var(--accent-mint)] font-semibold whitespace-nowrap">
              <CheckCircle2 size={11} /> Listo
            </span>
          )}
          {verdictStyle && (
            <motion.span
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="text-[11px] font-display font-black px-2.5 py-1 rounded-full tracking-wide shrink-0"
              style={{ background: verdictStyle.bg, color: verdictStyle.text }}
            >
              {verdictStyle.label}
            </motion.span>
          )}
        </div>
      </div>

      {/* Live / final score banner — clickable → match detail */}
      {(isLiveNow || isFinal) && hasScore && (
        <Link
          href={`/partido/${fixture.id}${isLiveNow ? "/live" : ""}`}
          onClick={e => e.stopPropagation()}
          className="mb-3 rounded-2xl px-3 py-2.5 flex items-center justify-between gap-2 hover:opacity-90 transition-opacity"
          style={{
            background: isFinal ? "rgba(20,241,149,0.12)" : "rgba(244,63,94,0.08)",
            border: `1px solid ${isFinal ? "rgba(20,241,149,0.35)" : "rgba(244,63,94,0.35)"}`,
            display: "flex",
          }}
        >
          <div className="flex items-center gap-3 font-display font-bold">
            <span className={`text-sm ${leadingPick === "H" ? "text-[var(--ink)]" : "text-[var(--ink-muted)]"}`}>{home.code}</span>
            <span className="font-black text-2xl tabular-nums tracking-tighter">{hg}</span>
            <span className="text-[var(--ink-muted)] text-lg">–</span>
            <span className="font-black text-2xl tabular-nums tracking-tighter">{ag}</span>
            <span className={`text-sm ${leadingPick === "A" ? "text-[var(--ink)]" : "text-[var(--ink-muted)]"}`}>{away.code}</span>
          </div>
          <div className="flex items-center gap-1.5">
            {live?.statusText && (
              <span className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)]">{live.statusText}</span>
            )}
            <span className="text-[10px] text-[var(--ink-muted)]">→</span>
          </div>
        </Link>
      )}

      {/* 1X2 buttons with team logos on the sides */}
      <div className={`grid grid-cols-[auto_1fr_auto] items-center gap-2 ${locked ? "pointer-events-none" : ""}`}>
        <TeamMini team={home} />
        <div className="grid grid-cols-3 gap-1">
          <PickBtn label="Local"   sub={home.code} active={picked === "H"} accent={accent} onClick={() => onPick("H")} prob={probs.H} highlight={leadingPick === "H"} />
          <PickBtn label="Empate"  sub="X"         active={picked === "D"} accent={accent} onClick={() => onPick("D")} prob={probs.D} highlight={leadingPick === "D"} />
          <PickBtn label="Visit."  sub={away.code} active={picked === "A"} accent={accent} onClick={() => onPick("A")} prob={probs.A} highlight={leadingPick === "A"} />
        </div>
        <TeamMini team={away} />
      </div>

      {/* All-picks breakdown — 3 columns always, avatars clickable */}
      {pickers && (pickers.H.length + pickers.D.length + pickers.A.length > 0) && (
        <div className="mt-3 rounded-2xl bg-[var(--bg-tint)] overflow-hidden">
          <div className="grid grid-cols-3 divide-x divide-[var(--line)]">
            {(["H", "D", "A"] as const).map(k => {
              const group = pickers[k];
              const label = k === "H" ? home.code : k === "A" ? away.code : "X";
              const isWinning = isFinal && leadingPick === k;
              const isCurrentlyWinning = isLiveNow && leadingPick === k;
              const isLosing = isFinal && leadingPick !== null && leadingPick !== k;
              return (
                <div
                  key={k}
                  className={`p-2 transition-colors ${isWinning ? "bg-[rgba(20,241,149,0.10)]" : isCurrentlyWinning ? "bg-[rgba(244,63,94,0.06)]" : isLosing ? "opacity-50" : ""}`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className={`text-[10px] font-bold uppercase tracking-wider ${isWinning ? "text-[#059669]" : isCurrentlyWinning ? "text-[#F43F5E]" : "text-[var(--ink-muted)]"}`}>
                      {label}
                    </span>
                    <span className="text-[10px] font-bold tabular-nums text-[var(--ink-muted)]">{group.length}</span>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {group.slice(0, 5).map(p => (
                      <Link
                        key={p.id}
                        href={`/quiniela?view=${p.id}`}
                        onClick={e => e.stopPropagation()}
                        title={p.name}
                        className="hover:scale-110 transition-transform"
                      >
                        <PlayerAvatar player={p} size={22} enableLightbox />
                      </Link>
                    ))}
                    {group.length > 5 && (
                      <span className="w-[22px] h-[22px] rounded-full bg-[var(--line)] grid place-items-center text-[9px] font-bold text-[var(--ink-muted)]">
                        +{group.length - 5}
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Optional exact score */}
      <button
        onClick={() => setShowScore(s => !s)}
        disabled={locked}
        className="mt-3 w-full flex items-center justify-center gap-1.5 text-[11px] font-semibold text-[var(--ink-soft)] hover:text-[var(--ink)] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
      >
        <ChevronDown size={12} className={`transition-transform ${showScore ? "rotate-180" : ""}`} />
        {hasExact ? `Marcador: ${prediction?.homeGoals}-${prediction?.awayGoals} (desempate)` : "Marcador exacto (opcional · desempate)"}
      </button>

      <AnimatePresence initial={false}>
        {showScore && (
          <motion.div
            initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="mt-3 pt-3 border-t border-[var(--line)] flex items-center justify-center gap-3">
              <Stepper
                label={home.code}
                value={prediction?.homeGoals ?? 0}
                onChange={(v) => onExact("home", v)}
                accent={accent}
                set={hasExact}
              />
              <span className="font-display text-xl text-[var(--ink-muted)]">—</span>
              <Stepper
                label={away.code}
                value={prediction?.awayGoals ?? 0}
                onChange={(v) => onExact("away", v)}
                accent={accent}
                set={hasExact}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Venue — clickable → match detail */}
      <Link
        href={`/partido/${fixture.id}`}
        onClick={e => e.stopPropagation()}
        className="mt-2 flex items-center gap-1 text-[10px] text-[var(--ink-muted)] hover:text-[var(--ink)] transition-colors"
      >
        <MapPin size={10} /> {fixture.venue} · {fixture.city} →
      </Link>
    </motion.div>
  );
}

function TeamMini({ team }: { team: typeof TEAMS[number] }) {
  return (
    <Link href={`/equipos/${team.code}`} className="flex flex-col items-center gap-1 w-12 hover:opacity-80 transition-opacity group" title={team.name}>
      <div className="relative w-10 h-10 rounded-xl overflow-hidden ring-1 ring-[var(--line)] group-hover:ring-[var(--ink)] transition-all">
        <Image src={flagUrl(team.iso2, 80)} alt={team.name} fill sizes="40px" className="object-cover" unoptimized />
      </div>
      <div className="font-display font-bold text-[10px] leading-none">{team.code}</div>
      {team.ranking && (
        <div className="text-[8px] text-[var(--ink-muted)] leading-none">#{team.ranking}</div>
      )}
    </Link>
  );
}

function PickBtn({
  label, sub, active, accent, onClick, prob, highlight,
}: {
  label: string; sub: string; active: boolean; accent: string; onClick: () => void; prob?: number; highlight?: boolean;
}) {
  const fill = prob !== undefined ? `${Math.round(prob * 100)}%` : undefined;
  return (
    <button
      onClick={onClick}
      className="rounded-2xl py-2.5 px-1 transition-all flex flex-col items-center gap-0.5 active:scale-95 relative overflow-hidden"
      style={{
        background: active ? accent : "var(--bg-tint)",
        color: active ? "white" : "var(--ink-soft)",
        boxShadow: active ? `0 6px 20px -8px ${accent}CC` : "none",
        outline: highlight && !active ? `2px solid rgba(20,241,149,0.65)` : "none",
        outlineOffset: -2,
      }}
    >
      {fill && !active && (
        <span
          className="absolute bottom-0 left-0 h-[3px] rounded-full transition-all duration-700"
          style={{ width: fill, background: `${accent}60` }}
        />
      )}
      <span className="font-display font-bold text-xs leading-none relative z-10">{label}</span>
      <span className="text-[9px] font-semibold opacity-80 leading-none relative z-10">{sub}</span>
      {prob !== undefined && (
        <span className="text-[10px] font-bold tabular-nums leading-none mt-0.5 relative z-10" style={{ opacity: active ? 0.85 : 0.6 }}>
          {Math.round(prob * 100)}%
        </span>
      )}
    </button>
  );
}

function Stepper({
  label, value, onChange, accent, set,
}: {
  label: string; value: number; onChange: (v: number) => void; accent: string; set: boolean;
}) {
  return (
    <div className="flex flex-col items-center gap-1">
      <span className="text-[9px] font-bold uppercase tracking-wider text-[var(--ink-muted)]">{label}</span>
      <div className="flex items-center gap-1">
        <button
          onClick={() => onChange(value - 1)}
          disabled={value <= 0}
          className="w-7 h-7 rounded-full grid place-items-center hairline-strong bg-white hover:bg-[var(--bg-tint)] disabled:opacity-30 transition-colors"
        >
          <Minus size={11} />
        </button>
        <div
          className="w-12 h-10 rounded-xl grid place-items-center font-display font-bold text-xl tabular-nums score"
          style={{
            background: set ? accent + "1F" : "var(--bg-tint)",
            color: set ? accent : "var(--ink-soft)",
          }}
        >
          {value}
        </div>
        <button
          onClick={() => onChange(value + 1)}
          className="w-7 h-7 rounded-full grid place-items-center hairline-strong bg-white hover:bg-[var(--bg-tint)] transition-colors"
        >
          <Plus size={11} />
        </button>
      </div>
    </div>
  );
}

function ChampionPicker({
  label, basePoints, icon, color, value, lockedAt, kind, readOnly, onChange,
}: {
  label: string; basePoints: number; icon: React.ReactNode; color: string;
  value?: string; lockedAt?: ChampionLockRound; kind: "champion" | "runnerUp";
  readOnly?: boolean;
  onChange: (code: string | undefined) => void;
}) {
  const [open, setOpen] = useState(false);
  const [showSchedule, setShowSchedule] = useState(false);
  const team = value ? TEAMS.find(t => t.code === value) : null;

  // Bonus actual sellado para este pick + bonus si se cambia AHORA.
  const lockedBonus = kind === "champion"
    ? championBonusPoints(lockedAt)
    : runnerUpBonusPoints(lockedAt);
  const nowBonus = currentChampionBonusIfChangedNow();
  const ifChangedNow = kind === "champion" ? nowBonus.champion : nowBonus.runnerUp;
  const wouldDrop = team && lockedAt && lockedAt !== nowBonus.round && ifChangedNow < lockedBonus;
  const past = nowBonus.round === "FINAL" || !!readOnly;

  // Tabla resumen de la degradación.
  const schedule: { round: ChampionLockRound; pts: number }[] = [
    { round: "PRE",   pts: basePoints },
    { round: "R32",   pts: Math.round(basePoints * 0.80) },
    { round: "R16",   pts: Math.round(basePoints * 0.60) },
    { round: "QF",    pts: Math.round(basePoints * 0.40) },
    { round: "SF",    pts: Math.round(basePoints * 0.20) },
    { round: "FINAL", pts: 0 },
  ];

  return (
    <div className="glass-strong rounded-3xl p-5 relative overflow-hidden">
      <div className="absolute -top-10 -right-10 w-40 h-40 rounded-full opacity-20 blur-2xl" style={{ background: color }} />
      <div className="relative">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-11 h-11 rounded-2xl grid place-items-center text-white" style={{ background: color }}>
            {icon}
          </div>
          <div className="flex-1 min-w-0">
            <div className="font-display font-bold">{label}</div>
            <div className="text-xs text-[var(--ink-muted)]">
              Base <strong>+{basePoints} pts</strong> · degrada por fase
            </div>
          </div>
          {/* Bonus actual */}
          <div className="text-right">
            <div className="font-display font-bold text-2xl tabular-nums" style={{ color }}>
              +{team ? lockedBonus : basePoints}
            </div>
            <div className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)]">pts si aciertas</div>
          </div>
        </div>

        {/* Lock / "si lo cambias ahora" banner */}
        {team && lockedAt && (
          <div className="mb-3 flex items-center gap-2 text-[11px] rounded-xl px-3 py-2 bg-[var(--bg-tint)] text-[var(--ink-soft)]">
            <Lock size={11} className="shrink-0" />
            <span className="flex-1">
              Sellado en <strong>{CHAMPION_PHASE_LABEL[lockedAt]}</strong>.{" "}
              {past
                ? <span className="text-[var(--accent-coral)] font-semibold">Ya empezó la final, no se puede cambiar.</span>
                : wouldDrop
                  ? <>Si lo cambias hoy: <strong className="text-[var(--accent-coral)]">+{ifChangedNow} pts</strong> ({CHAMPION_PHASE_LABEL[nowBonus.round]}).</>
                  : <>Cambiar hoy mantiene <strong>+{ifChangedNow} pts</strong>.</>
              }
            </span>
          </div>
        )}

        <button
          onClick={() => setOpen(o => !o)}
          disabled={past}
          className="w-full flex items-center gap-3 p-3 rounded-2xl bg-white hairline-strong hover:border-[var(--ink)] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {team ? (
            <>
              <div className="relative w-9 h-9 rounded-lg overflow-hidden ring-1 ring-[var(--line)]">
                <Image src={flagUrl(team.iso2, 64)} alt={team.name} fill sizes="36px" className="object-cover" unoptimized />
              </div>
              <div className="flex-1 text-left">
                <div className="font-display font-bold">{team.name}</div>
                <div className="text-xs text-[var(--ink-muted)]">{team.code} · Grupo {team.group}</div>
              </div>
              <span className="text-xs text-[var(--ink-muted)]">{past ? "cerrado" : "cambiar"}</span>
            </>
          ) : (
            <>
              <div className="w-9 h-9 rounded-lg bg-[var(--bg-tint)] grid place-items-center text-[var(--ink-muted)]">
                <Sparkles size={16} />
              </div>
              <span className="text-sm font-semibold text-[var(--ink-soft)]">Elegir selección</span>
            </>
          )}
        </button>
        {team && (
          <Link href={`/equipos/${team.code}`} className="mt-1 text-[10px] text-[var(--ink-muted)] hover:text-[var(--ink)] transition-colors flex items-center justify-center gap-1">
            Ver estadísticas de {team.name} →
          </Link>
        )}

        {/* Toggle: ver tabla de degradación */}
        <button
          onClick={() => setShowSchedule(s => !s)}
          className="mt-2 w-full flex items-center justify-center gap-1 text-[11px] font-semibold text-[var(--ink-muted)] hover:text-[var(--ink)] transition-colors"
        >
          <ChevronDown size={11} className={`transition-transform ${showSchedule ? "rotate-180" : ""}`} />
          {showSchedule ? "Ocultar" : "Ver"} degradación por fase
        </button>
        <AnimatePresence initial={false}>
          {showSchedule && (
            <motion.div
              initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden"
            >
              <div className="mt-2 grid grid-cols-6 gap-1 rounded-xl bg-[var(--bg-tint)] p-2">
                {schedule.map(s => {
                  const isCurrent = s.round === nowBonus.round;
                  const isLocked = lockedAt === s.round;
                  return (
                    <div
                      key={s.round}
                      className={`rounded-lg px-1 py-1.5 text-center ${isCurrent ? "bg-white ring-2" : ""}`}
                      style={isCurrent ? { boxShadow: `0 0 0 2px ${color}` } : undefined}
                    >
                      <div className="text-[9px] font-bold uppercase tracking-wider text-[var(--ink-muted)] truncate">
                        {s.round === "PRE" ? "Pre" : s.round}
                      </div>
                      <div className="font-display font-bold text-sm tabular-nums" style={{ color: isCurrent || isLocked ? color : "var(--ink-soft)" }}>
                        +{s.pts}
                      </div>
                      {isLocked && <div className="text-[8px] text-[var(--ink-muted)] mt-0.5">tuyo</div>}
                    </div>
                  );
                })}
              </div>
              <p className="mt-2 text-[10px] text-[var(--ink-muted)] leading-snug">
                Mientras antes te decidas, más vale el bonus. Cambiar después de cada fase degrada los puntos. <strong>La fase actual aplica al guardar.</strong>
              </p>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {open && !past && (
            <motion.div
              initial={{ opacity: 0, y: -4, height: 0 }}
              animate={{ opacity: 1, y: 0, height: "auto" }}
              exit={{ opacity: 0, y: -4, height: 0 }}
              className="overflow-hidden"
            >
              <div className="mt-3 grid grid-cols-6 sm:grid-cols-8 gap-1.5 max-h-72 overflow-y-auto p-1 rounded-2xl bg-[var(--bg-tint)]">
                {TEAMS.map(t => {
                  const selected = value === t.code;
                  return (
                    <button
                      key={t.code}
                      title={t.name}
                      onClick={() => { onChange(t.code); setOpen(false); }}
                      className={`relative w-full aspect-square rounded-lg overflow-hidden transition-all ${selected ? "ring-2 ring-[var(--ink)] scale-105" : "ring-1 ring-[var(--line)] hover:ring-[var(--ink)] hover:scale-105"}`}
                    >
                      <Image src={flagUrl(t.iso2, 64)} alt={t.name} fill sizes="40px" className="object-cover" unoptimized />
                      {selected && (
                        <div className="absolute inset-0 bg-[var(--ink)]/60 grid place-items-center">
                          <CheckCircle2 size={16} className="text-white" />
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
              {team && (
                <button onClick={() => { onChange(undefined); setOpen(false); }} className="mt-2 text-xs text-[var(--accent-coral)] hover:underline">
                  Quitar selección
                </button>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

// ============================== BRACKET ==============================

function BracketSection({
  data, accent, readOnly, onPickWinner, onPickSingle, onApplyBracket,
}: {
  data: PlayerPredictions;
  accent: string;
  readOnly?: boolean;
  onPickWinner: (round: "R32" | "R16" | "QF" | "SF", idx: number, total: number, code: string) => void;
  onPickSingle: (field: "THIRD" | "FINAL", code: string) => void;
  onApplyBracket: (next: BracketPick) => void;
}) {
  const { results: real } = useGroupRealResults();
  const realCount = useMemo(() => Object.keys(real).length, [real]);
  const standings = useMemo(() => computeAllStandings(data, real), [data, real]);
  const r32Pairings = useMemo(() => computeR32Pairings(data, real), [data, real]);
  const r32Ready = r32Pairings.every(p => p.teams[0] && p.teams[1]);

  // When real results reshape the R32 pairings, any saved winner that's no
  // longer in its slot's new pair is stale → clear it and wipe downstream
  // rounds (R16/QF/SF/THIRD/FINAL) so the player re-picks against the truth.
  useEffect(() => {
    if (readOnly) return;
    if (r32Pairings.every(p => isKOSlotLocked(p.slot))) return;
    const saved = (data.bracket.R32 ?? []).slice();
    if (saved.length === 0) return;
    let mutated = false;
    for (let i = 0; i < r32Pairings.length; i++) {
      const pick = saved[i];
      if (!pick) continue;
      const [a, b] = r32Pairings[i].teams;
      if (pick !== a && pick !== b) {
        saved[i] = "";
        mutated = true;
      }
    }
    if (!mutated) return;
    onApplyBracket({
      ...data.bracket,
      R32: saved,
      R16: [], QF: [], SF: [],
      THIRD: undefined, FINAL: undefined,
    });
  }, [r32Pairings, readOnly, data.bracket, onApplyBracket]);

  const r32Winners: string[] = data.bracket.R32 ?? [];
  const r16Pairs = useMemo(() => pairWinners(r32Winners.slice(0, 16)), [r32Winners]);
  const r16Done = bracketRoundComplete(data.bracket, "R32");

  const r16Winners: string[] = data.bracket.R16 ?? [];
  const qfPairs = useMemo(() => pairWinners(r16Winners.slice(0, 8)), [r16Winners]);
  const qfReady = bracketRoundComplete(data.bracket, "R16");

  const qfWinners: string[] = data.bracket.QF ?? [];
  const sfPairs = useMemo(() => pairWinners(qfWinners.slice(0, 4)), [qfWinners]);
  const sfReady = bracketRoundComplete(data.bracket, "QF");

  const sfWinners: string[] = data.bracket.SF ?? [];
  const finalPair = sfWinners.length >= 2 ? [sfWinners[0], sfWinners[1]] as [string, string] : null;
  const finalReady = bracketRoundComplete(data.bracket, "SF");

  // 3rd place = the two SF losers (we know them once SF picks exist and we know SF inputs).
  const sfLosers: string[] = (() => {
    if (!sfReady || qfWinners.length < 4) return [];
    const losers: string[] = [];
    for (let i = 0; i < 2; i++) {
      const [a, b] = [qfWinners[i * 2], qfWinners[i * 2 + 1]];
      const winner = sfWinners[i];
      if (winner === a) losers.push(b);
      else if (winner === b) losers.push(a);
    }
    return losers;
  })();

  return (
    <div className={`mt-12 ${readOnly ? "pointer-events-none select-none" : ""}`}>
      <div className="flex items-end justify-between mb-4 gap-3 flex-wrap">
        <div>
          <h2 className="font-display text-2xl md:text-3xl font-bold flex items-center gap-2">
            <Swords size={22} /> {readOnly ? "Su bracket" : "Tu bracket"}
          </h2>
          <p className="text-sm text-[var(--ink-soft)] mt-1">
            {realCount === 0
              ? "Standings predichas con tus picks. Cuando los partidos terminen en la vida real, los resultados oficiales sustituyen a tus predicciones y el R32 se actualiza solo."
              : "Híbrido en vivo: lo ya jugado pesa el resultado real, lo que falta pesa tus picks. El R32 se reordena conforme caigan los clasificados."}
          </p>
        </div>
        {realCount > 0 && (
          <span className="chip" style={{ background: "rgba(20,241,149,0.12)", color: "var(--ink)" }}>
            <span className="live-dot" /> {realCount} partido{realCount === 1 ? "" : "s"} con resultado real
          </span>
        )}
      </div>

      {/* Aviso del scoring del bracket — los picks aquí son "de a foto" */}
      <div className="glass rounded-2xl px-4 py-3 mb-6 text-xs md:text-sm text-[var(--ink-soft)] border border-[var(--ink)]/10 flex items-start gap-2">
        <Trophy size={16} className="mt-0.5 shrink-0" />
        <span>
          Los picks de eliminatorias <strong>no suman puntos</strong> — el bracket es para
          que veas cómo va tomando forma. Lo único que paga aquí es atinarle al{" "}
          <strong>campeón del Mundial</strong> ({SCORING.bonusChampion} pts si lo fijas antes
          del R32; el bonus baja conforme avanzan las fases).
        </span>
      </div>

      {/* Standings — híbridas real + predicción */}
      <div className="mb-8">
        <h3 className="font-display font-bold text-sm uppercase tracking-[0.18em] text-[var(--ink-muted)] mb-3">
          {realCount === 0 ? "Standings predichas" : "Standings (real + predicho)"}
        </h3>
        <div className="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {GROUP_LETTERS.map(letter => (
            <MiniStandings key={letter} letter={letter} rows={standings[letter] ?? []} />
          ))}
        </div>
      </div>

      {/* R32 — per-slot locking: each matchup locks at its individual kickoff */}
      <RoundBlock title="Dieciseisavos (R32)" sub="16 partidos · informativo (0 pts)"
        disabled={!r32Ready}
        lockMsg="Faltan picks de grupos para definir los 32 clasificados.">
        {r32Ready ? (
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {r32Pairings.map((p, idx) => (
              <MatchupPicker
                key={p.slot}
                index={idx + 1}
                pair={p.teams}
                winner={r32Winners[idx]}
                accent={accent}
                locked={isKOSlotLocked(p.slot)}
                onPick={(code) => onPickWinner("R32", idx, 16, code)}
              />
            ))}
          </div>
        ) : (
          <EmptyMsg>Faltan picks de grupos para definir los 32 clasificados.</EmptyMsg>
        )}
      </RoundBlock>

      {/* R16 */}
      <RoundBlock title="Octavos" sub="8 partidos · informativo (0 pts)"
        disabled={!r16Done || isBracketRoundLocked("R16")}
        lockMsg={isBracketRoundLocked("R16") ? "Octavos ya empezó · pick cerrado" : "Completa antes los 16 picks de R32"}>
        <AnimatePresence>
          {r16Done && (
            <motion.div
              key="r16"
              initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3"
            >
              {r16Pairs.map((pair, idx) => (
                <MatchupPicker
                  key={`r16-${idx}`}
                  index={idx + 1}
                  pair={pair}
                  winner={(data.bracket.R16 ?? [])[idx]}
                  accent={accent}
                  onPick={(code) => onPickWinner("R16", idx, 8, code)}
                />
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </RoundBlock>

      {/* QF */}
      <RoundBlock title="Cuartos" sub="4 partidos · informativo (0 pts)"
        disabled={!qfReady || isBracketRoundLocked("QF")}
        lockMsg={isBracketRoundLocked("QF") ? "Cuartos ya empezó · pick cerrado" : "Completa antes los 8 picks de Octavos"}>
        <AnimatePresence>
          {qfReady && (
            <motion.div
              key="qf"
              initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3"
            >
              {qfPairs.map((pair, idx) => (
                <MatchupPicker
                  key={`qf-${idx}`}
                  index={idx + 1}
                  pair={pair}
                  winner={(data.bracket.QF ?? [])[idx]}
                  accent={accent}
                  onPick={(code) => onPickWinner("QF", idx, 4, code)}
                />
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </RoundBlock>

      {/* SF */}
      <RoundBlock title="Semifinales" sub="2 partidos · informativo (0 pts)"
        disabled={!sfReady || isBracketRoundLocked("SF")}
        lockMsg={isBracketRoundLocked("SF") ? "Semis ya empezó · pick cerrado" : "Completa antes los 4 picks de Cuartos"}>
        <AnimatePresence>
          {sfReady && (
            <motion.div
              key="sf"
              initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              className="grid sm:grid-cols-2 gap-3"
            >
              {sfPairs.map((pair, idx) => (
                <MatchupPicker
                  key={`sf-${idx}`}
                  index={idx + 1}
                  pair={pair}
                  winner={(data.bracket.SF ?? [])[idx]}
                  accent={accent}
                  onPick={(code) => onPickWinner("SF", idx, 2, code)}
                />
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </RoundBlock>

      {/* THIRD + FINAL */}
      <RoundBlock title="3er lugar y Final" sub="2 partidos · informativo (0 pts)"
        disabled={!finalReady || isBracketRoundLocked("FINAL")}
        lockMsg={isBracketRoundLocked("FINAL") ? "Final ya empezó · pick cerrado" : "Completa antes los 2 picks de Semifinales"}>
        <AnimatePresence>
          {finalReady && finalPair && (
            <motion.div
              key="final"
              initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              className="grid md:grid-cols-2 gap-3"
            >
              {sfLosers.length === 2 && (
                <MatchupPicker
                  index={1}
                  label="3er lugar"
                  pair={[sfLosers[0], sfLosers[1]]}
                  winner={data.bracket.THIRD}
                  accent={accent}
                  onPick={(code) => onPickSingle("THIRD", code)}
                />
              )}
              <MatchupPicker
                index={1}
                label="Final"
                pair={finalPair}
                winner={data.bracket.FINAL}
                accent={accent}
                onPick={(code) => onPickSingle("FINAL", code)}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </RoundBlock>
    </div>
  );
}

function MiniStandings({ letter, rows }: { letter: string; rows: Standing[] }) {
  const groupHasReal = rows.some(r => r.realCount > 0);
  return (
    <div className="glass rounded-2xl p-3">
      <div className="flex items-center justify-between mb-2">
        <div className="font-display font-bold text-sm flex items-center gap-1.5">
          Grupo {letter}
          {groupHasReal && <span className="live-dot" title="Datos en vivo" />}
        </div>
        <div className="text-[10px] text-[var(--ink-muted)] uppercase tracking-wider">Pts · DG · GF</div>
      </div>
      <ol className="space-y-1">
        {rows.map((r, i) => {
          const qualified = i < 2;
          const thirdSlot = i === 2;
          const allReal = r.played > 0 && r.realCount === r.played;
          return (
            <li key={r.team} className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2 min-w-0">
                <span
                  className="w-4 h-4 rounded-md grid place-items-center text-[9px] font-bold tabular-nums shrink-0"
                  style={{
                    background: qualified ? "var(--accent-mint, #34d399)" : thirdSlot ? "var(--accent-violet, #8b5cf6)" : "var(--bg-tint)",
                    color: qualified || thirdSlot ? "white" : "var(--ink-muted)",
                  }}
                >
                  {i + 1}
                </span>
                <TeamTag code={r.team} />
                {r.realCount > 0 && (
                  <span
                    className="text-[9px] font-bold px-1 py-0.5 rounded uppercase tracking-wider"
                    style={{
                      background: allReal ? "var(--accent-mint, #14F195)" : "rgba(20,241,149,0.18)",
                      color: allReal ? "white" : "var(--ink)",
                    }}
                    title={`${r.realCount} de ${r.played} partidos contados con resultado real`}
                  >
                    {allReal ? "REAL" : `${r.realCount}R`}
                  </span>
                )}
              </div>
              <div className="font-semibold tabular-nums text-[var(--ink-soft)]">
                {r.pts}<span className="text-[var(--ink-muted)] font-normal"> · {r.gd >= 0 ? "+" : ""}{r.gd} · {r.gf}</span>
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}

function TeamTag({ code }: { code: string }) {
  const team = TEAMS.find(t => t.code === code);
  if (!team) return <span className="text-[var(--ink-muted)]">—</span>;
  return (
    <Link href={`/equipos/${team.code}`} className="flex items-center gap-1.5 min-w-0 hover:opacity-80 transition-opacity">
      <div className="relative w-4 h-4 rounded-sm overflow-hidden ring-1 ring-[var(--line)] shrink-0">
        <Image src={flagUrl(team.iso2, 32)} alt={team.name} fill sizes="16px" className="object-cover" unoptimized />
      </div>
      <span className="font-display font-bold text-[11px] truncate">{team.code}</span>
    </Link>
  );
}

function RoundBlock({
  title, sub, disabled, lockMsg, children,
}: {
  title: string; sub: string; disabled: boolean; lockMsg: string; children: React.ReactNode;
}) {
  return (
    <div className="mt-6">
      <div className="flex items-center justify-between gap-3 mb-3">
        <div>
          <h3 className="font-display font-bold">{title}</h3>
          <div className="text-[11px] text-[var(--ink-muted)]">{sub}</div>
        </div>
        {disabled && (
          <span className="flex items-center gap-1.5 text-[11px] text-[var(--ink-muted)] glass rounded-full px-2.5 py-1" title={lockMsg}>
            <Lock size={11} /> Bloqueado
          </span>
        )}
      </div>
      <div className={disabled ? "opacity-40 pointer-events-none select-none" : ""}>
        {disabled ? <EmptyMsg>{lockMsg}</EmptyMsg> : children}
      </div>
    </div>
  );
}

function EmptyMsg({ children }: { children: React.ReactNode }) {
  return (
    <div className="glass rounded-2xl p-4 text-sm text-[var(--ink-muted)] text-center">
      {children}
    </div>
  );
}

function MatchupPicker({
  index, label, pair, winner, accent, onPick, locked,
}: {
  index: number;
  label?: string;
  pair: [string, string];
  winner?: string;
  accent: string;
  onPick: (code: string) => void;
  locked?: boolean;
}) {
  const [a, b] = pair;
  return (
    <div className="glass rounded-2xl p-3" style={locked ? { opacity: 0.55 } : {}}>
      <div className="flex items-center justify-between mb-2 text-[10px] uppercase tracking-wider text-[var(--ink-muted)]">
        <span>{label ?? `Partido ${index}`}</span>
        {locked
          ? <span className="flex items-center gap-1"><Lock size={9} /> Cerrado</span>
          : winner
            ? <span className="text-[var(--accent-mint)] font-semibold flex items-center gap-1"><CheckCircle2 size={10} /> Listo</span>
            : null}
      </div>
      <div className={`grid grid-cols-2 gap-2 ${locked ? "pointer-events-none select-none" : ""}`}>
        <TeamPickBtn code={a} active={winner === a} accent={accent} onClick={() => a && !locked && onPick(a)} />
        <TeamPickBtn code={b} active={winner === b} accent={accent} onClick={() => b && !locked && onPick(b)} />
      </div>
    </div>
  );
}

// ============================== TICKET ODDS ==============================

function TicketOdds({ data, accent }: { data: PlayerPredictions; accent: string }) {
  const odds = useMemo(() => computePlayerOdds(data), [data]);

  if (!odds.ready) {
    return (
      <div className="mt-10 glass-strong rounded-3xl p-6">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-11 h-11 rounded-2xl grid place-items-center text-white" style={{ background: accent }}>
            <Sparkles size={20} />
          </div>
          <div>
            <h3 className="font-display font-bold text-lg">Probabilidades de tu ticket</h3>
            <p className="text-xs text-[var(--ink-muted)]">Completa todo para desbloquear el análisis</p>
          </div>
        </div>
        <ul className="text-sm text-[var(--ink-soft)] space-y-1">
          {odds.missing.groupPicks > 0 && <li>· Faltan <strong>{odds.missing.groupPicks}</strong> picks de fase de grupos</li>}
          {odds.missing.champion && <li>· Falta elegir <strong>campeón</strong></li>}
          {odds.missing.runnerUp && <li>· Falta elegir <strong>subcampeón</strong></li>}
        </ul>
      </div>
    );
  }

  const champ = probLabel(odds.championProb);
  const runner = probLabel(odds.runnerUpProb);
  const strengthPct = (odds.ticketStrength * 100).toFixed(0);

  return (
    <div className="mt-10 glass-strong rounded-3xl p-6 relative overflow-hidden">
      <div className="absolute -top-16 -right-16 w-48 h-48 rounded-full opacity-15 blur-3xl" style={{ background: accent }} />
      <div className="relative">
        <div className="flex items-center justify-between gap-3 mb-4 flex-wrap">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl grid place-items-center text-white" style={{ background: accent }}>
              <Sparkles size={20} />
            </div>
            <div>
              <h3 className="font-display font-bold text-lg">Probabilidades de tu ticket</h3>
              <p className="text-xs text-[var(--ink-muted)]">Calculado con ELO + Poisson · sin amistosos recientes</p>
            </div>
          </div>
          <div className="text-right">
            <div className="font-display font-black text-3xl tabular-nums" style={{ color: accent }}>
              {odds.expectedTotalPoints.toFixed(0)}
            </div>
            <div className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)]">pts esperados</div>
          </div>
        </div>

        {/* Ticket strength bar */}
        <div className="mb-5">
          <div className="flex items-center justify-between text-xs mb-1.5">
            <span className="font-semibold text-[var(--ink-soft)]">Fuerza del ticket vs óptimo ELO</span>
            <span className="font-display font-bold tabular-nums">{strengthPct}%</span>
          </div>
          <div className="h-2 rounded-full bg-[var(--bg-tint)] overflow-hidden">
            <motion.div
              className="h-full rounded-full"
              animate={{ width: `${strengthPct}%` }}
              transition={{ duration: .6 }}
              style={{ background: `linear-gradient(90deg, ${accent}, var(--accent-violet))` }}
            />
          </div>
          <p className="text-[10px] text-[var(--ink-muted)] mt-1">
            100% = elegiste el resultado más probable (según ELO) en cada partido.
          </p>
        </div>

        {/* Champion / runner-up cards */}
        <div className="grid sm:grid-cols-2 gap-3 mb-4">
          <OddsCard
            title="Campeón correcto"
            sub={data.champion ?? "—"}
            pct={champ.pct}
            tone={champ.tone}
            label={champ.label}
            expected={`+${odds.expectedChampionBonus.toFixed(1)} pts esperados`}
          />
          <OddsCard
            title="Subcampeón correcto"
            sub={data.runnerUp ?? "—"}
            pct={runner.pct}
            tone={runner.tone}
            label={runner.label}
            expected={`+${odds.expectedRunnerUpBonus.toFixed(1)} pts esperados`}
          />
        </div>

        {/* Breakdown */}
        <div className="grid grid-cols-3 gap-2 text-center">
          <Mini label="Grupos" value={odds.expectedGroupPoints.toFixed(0)} />
          <Mini label="Bracket" value={odds.expectedBracketPoints.toFixed(0)} />
          <Mini label="Bonus" value={(odds.expectedChampionBonus + odds.expectedRunnerUpBonus).toFixed(0)} />
        </div>

        <p className="mt-4 text-[10px] text-[var(--ink-muted)] leading-relaxed">
          <strong>Cómo se calcula:</strong> cada partido usa ELO de los equipos para estimar P(local), P(empate), P(visitante). El score esperado de cada pick = P(acierto) × puntos. El bonus de campeón/subcampeón ya considera la degradación por fase actual.
        </p>
      </div>
    </div>
  );
}

function OddsCard({ title, sub, pct, tone, label, expected }: {
  title: string; sub: string; pct: string; tone: "good" | "mid" | "bad"; label: string; expected: string;
}) {
  const toneClass = tone === "good"
    ? "text-[var(--accent-mint)]"
    : tone === "mid" ? "text-[var(--accent-violet)]" : "text-[var(--accent-coral)]";
  return (
    <div className="glass rounded-2xl p-3.5">
      <div className="flex items-baseline justify-between mb-1">
        <span className="text-[11px] uppercase tracking-wider text-[var(--ink-muted)]">{title}</span>
        <span className="font-display font-bold text-[11px]">{sub}</span>
      </div>
      <div className="flex items-baseline gap-2">
        <span className={`font-display font-black text-2xl tabular-nums ${toneClass}`}>{pct}</span>
        <span className="text-[10px] text-[var(--ink-soft)] font-semibold">{label}</span>
      </div>
      <div className="mt-1 text-[10px] text-[var(--ink-muted)]">{expected}</div>
    </div>
  );
}

function Mini({ label, value }: { label: string; value: string }) {
  return (
    <div className="glass rounded-2xl p-2.5">
      <div className="font-display font-black text-xl tabular-nums">{value}</div>
      <div className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)]">{label}</div>
    </div>
  );
}

// ============================== CLOUD SYNC BADGE ==============================
// Mostrar al jugador si su quiniela está realmente en Firestore o si el sync
// está fallando (cookie expirada, sin red, etc). Antes los errores eran
// silenciados y Charal llegó al 100% local sin saber que el server tenía 0.

function CloudSyncBadge({ playerId }: { playerId: string }) {
  const [status, setStatus] = useState<SyncStatus>("idle");
  const [err, setErr] = useState<string | undefined>();

  useEffect(() => {
    let hideTimer: ReturnType<typeof setTimeout> | undefined;
    const onSync = (e: Event) => {
      const detail = (e as CustomEvent<SyncEvent>).detail;
      if (detail.playerId !== playerId) return;
      setStatus(detail.status);
      setErr(detail.error);
      if (hideTimer) clearTimeout(hideTimer);
      if (detail.status === "ok") {
        hideTimer = setTimeout(() => setStatus("idle"), 2500);
      }
    };
    window.addEventListener("q26:predictions-sync", onSync as EventListener);
    return () => {
      window.removeEventListener("q26:predictions-sync", onSync as EventListener);
      if (hideTimer) clearTimeout(hideTimer);
    };
  }, [playerId]);

  if (status === "idle") return null;

  const tone: Record<SyncStatus, { bg: string; ink: string; text: string }> = {
    idle:         { bg: "transparent",                ink: "var(--ink-muted)", text: "" },
    pending:      { bg: "rgba(125,125,125,0.12)",     ink: "var(--ink-soft)",  text: "Guardando en la nube…" },
    saving:       { bg: "rgba(14,165,233,0.12)",      ink: "#0EA5E9",          text: "Subiendo a la nube…" },
    ok:           { bg: "rgba(34,197,94,0.14)",       ink: "#16a34a",          text: "Guardado en la nube" },
    error:        { bg: "rgba(239,68,68,0.14)",       ink: "#dc2626",          text: "No se pudo guardar — reintentando" },
    unauthorized: { bg: "rgba(239,68,68,0.14)",       ink: "#dc2626",          text: "Sesión expirada — vuelve a iniciar sesión" },
  };
  const t = tone[status];

  return (
    <div className="fixed bottom-24 md:bottom-6 left-1/2 -translate-x-1/2 z-40 pointer-events-none">
      <div
        className="rounded-full px-3.5 py-1.5 text-[11px] md:text-xs font-semibold shadow-lg flex items-center gap-1.5"
        style={{ background: t.bg, color: t.ink, backdropFilter: "blur(8px)" }}
        title={err}
      >
        {(status === "pending" || status === "saving") && <Sparkles size={12} className="animate-pulse" />}
        {status === "ok" && <CheckCircle2 size={12} />}
        {(status === "error" || status === "unauthorized") && <AlertCircle size={12} />}
        {t.text}
      </div>
    </div>
  );
}

// ============================== BRACKET HELPERS ==============================

function TeamPickBtn({ code, active, accent, onClick }: { code: string; active: boolean; accent: string; onClick: () => void }) {
  const team = code ? TEAMS.find(t => t.code === code) : null;
  if (!team) {
    return (
      <div className="rounded-xl py-3 px-2 bg-[var(--bg-tint)] text-[var(--ink-muted)] text-xs text-center">
        Por definir
      </div>
    );
  }
  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={(e) => e.key === "Enter" && onClick()}
      className="rounded-xl py-2.5 px-2 flex items-center gap-2 transition-all active:scale-95 cursor-pointer select-none"
      style={{
        background: active ? accent : "var(--bg-tint)",
        color: active ? "white" : "var(--ink)",
        boxShadow: active ? `0 6px 18px -8px ${accent}` : "none",
      }}
    >
      <Link
        href={`/equipos/${team.code}`}
        onClick={(e) => e.stopPropagation()}
        className="relative w-6 h-6 rounded-md overflow-hidden ring-1 ring-[var(--line)] shrink-0 hover:ring-2 hover:ring-white/60 transition-all"
      >
        <Image src={flagUrl(team.iso2, 48)} alt={team.name} fill sizes="24px" className="object-cover" unoptimized />
      </Link>
      <span className="font-display font-bold text-xs truncate">{team.code}</span>
    </div>
  );
}
