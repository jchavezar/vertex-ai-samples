"use client";

// Thin compatibility re-export. The goal-only overlay was superseded by
// <LiveEventOverlay>, which handles goals + red cards + penalties + subs +
// VAR with a catch-up queue. Anything still importing the old name keeps
// working unchanged.

export { LiveEventOverlay as GoalCelebrationOverlay } from "@/components/LiveEventOverlay";
