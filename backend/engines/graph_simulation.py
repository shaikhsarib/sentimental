"""
SentiFlow V5: SEIR Epidemiological Narrative Projection Engine
==============================================================
Real timestep-by-timestep SEIR simulation with sentiment-modulated parameters.
Models narrative spread across a 10M node population using differential equations.

Compartments:
  S(t) — Susceptible: People unaware of the narrative
  E(t) — Exposed: People who've seen it but haven't engaged
  I(t) — Infected: People actively spreading/amplifying the narrative
  R(t) — Recovered: People who've moved on or become desensitized

Sentiment-Modulated Parameters:
  β (beta)  — Infection rate: How quickly narrative spreads (driven by virality score)
  σ (sigma) — Incubation rate: How fast exposed become active spreaders (1/incubation_period)
  γ (gamma) — Recovery rate: How fast people lose interest (1/recovery_period)
  
The Narrative R0 Index = β / γ (basic reproduction number for narrative spread)
"""

import numpy as np
from typing import Dict, List, Optional


class GraphSimulation:
    """
    Production-grade SEIR epidemiological projection engine.
    Simulates narrative spread across a population using timestep-based
    differential equations with sentiment-modulated transmission parameters.
    """

    # ─── DEFAULT POPULATION & SIMULATION CONFIG ───
    DEFAULT_POPULATION = 10_000_000
    DEFAULT_TIMESTEPS = 336      # 14 days of hourly resolution
    DT = 1.0                     # timestep = 1 hour

    # ─── EPIDEMIOLOGICAL PARAMETER BOUNDS ───
    # These are calibrated from real social media crisis velocity data
    BETA_MAP = {
        # virality_score → base infection rate per hour
        1: 0.001, 2: 0.005, 3: 0.015, 4: 0.035,
        5: 0.065, 6: 0.10,  7: 0.16,  8: 0.25,
        9: 0.38,  10: 0.55
    }

    # Sentiment-to-parameter modifiers
    EMOTION_MULTIPLIERS = {
        "anger":        {"beta": 1.8, "sigma": 1.5, "gamma": 0.6},
        "outrage":      {"beta": 2.0, "sigma": 1.8, "gamma": 0.5},
        "fear":         {"beta": 1.5, "sigma": 1.3, "gamma": 0.7},
        "disgust":      {"beta": 1.4, "sigma": 1.2, "gamma": 0.8},
        "anxiety":      {"beta": 1.3, "sigma": 1.1, "gamma": 0.75},
        "sadness":      {"beta": 0.8, "sigma": 0.7, "gamma": 1.3},
        "amusement":    {"beta": 1.6, "sigma": 1.4, "gamma": 1.1},
        "shock":        {"beta": 1.7, "sigma": 1.6, "gamma": 0.9},
        "contempt":     {"beta": 1.2, "sigma": 1.0, "gamma": 0.85},
        "resignation":  {"beta": 0.5, "sigma": 0.4, "gamma": 1.5},
        "neutral":      {"beta": 1.0, "sigma": 1.0, "gamma": 1.0},
    }

    def __init__(self, population: int = DEFAULT_POPULATION):
        self.population = population

    def _get_base_parameters(self, virality_score: int) -> Dict[str, float]:
        """
        Convert virality score (1-10) to base SEIR parameters.
        These are hourly rates for a social media narrative crisis.
        """
        score = max(1, min(10, int(virality_score)))
        beta = self.BETA_MAP.get(score, 0.05)

        # Incubation period scales inversely with virality
        # High virality = faster engagement (shorter incubation)
        incubation_hours = max(0.5, 8.0 - (score * 0.7))
        sigma = 1.0 / incubation_hours

        # Recovery period scales with virality (high virality = longer memory)
        recovery_hours = 24.0 + (score * 8.0)
        gamma = 1.0 / recovery_hours

        return {"beta": beta, "sigma": sigma, "gamma": gamma}

    def _apply_emotion_modifiers(
        self, params: Dict[str, float], emotions: List[str]
    ) -> Dict[str, float]:
        """
        Modulate SEIR parameters based on aggregate emotional state of agents.
        Anger/outrage accelerates spread. Sadness/resignation dampens it.
        """
        if not emotions:
            return params

        # Compute average modifier across all detected emotions
        beta_mods, sigma_mods, gamma_mods = [], [], []
        for emotion in emotions:
            key = emotion.lower().strip()
            mods = self.EMOTION_MULTIPLIERS.get(key, self.EMOTION_MULTIPLIERS["neutral"])
            beta_mods.append(mods["beta"])
            sigma_mods.append(mods["sigma"])
            gamma_mods.append(mods["gamma"])

        params["beta"] *= float(np.mean(beta_mods))
        params["sigma"] *= float(np.mean(sigma_mods))
        params["gamma"] *= float(np.mean(gamma_mods))
        return params

    def run_seir_simulation(
        self,
        virality_score: int,
        emotions: Optional[List[str]] = None,
        initial_infected: int = 100,
        timesteps: Optional[int] = None,
    ) -> Dict:
        """
        Execute a full SEIR simulation with sentiment-modulated parameters.

        Args:
            virality_score: Max virality risk score from agent swarm (1-10)
            emotions: List of primary emotions detected across agents
            initial_infected: Seed population (initial spreaders)
            timesteps: Number of hourly timesteps to simulate (default: 336 = 14 days)

        Returns:
            Complete simulation result with time series, peak analysis,
            Narrative R0, and trajectory classification.
        """
        T = timesteps or self.DEFAULT_TIMESTEPS
        N = self.population

        # ── Step 1: Compute sentiment-modulated parameters ──
        params = self._get_base_parameters(virality_score)
        if emotions:
            params = self._apply_emotion_modifiers(params, emotions)

        beta = params["beta"]
        sigma = params["sigma"]
        gamma = params["gamma"]

        # ── Step 2: Calculate Narrative R0 ──
        R0 = beta / gamma if gamma > 0 else 0.0

        # ── Step 3: Initialize compartments ──
        S = np.zeros(T)
        E = np.zeros(T)
        I = np.zeros(T)
        R = np.zeros(T)

        I_0 = min(initial_infected, N)
        S[0] = N - I_0
        E[0] = 0
        I[0] = I_0
        R[0] = 0

        # ── Step 4: Run SEIR differential equations (Euler method) ──
        for t in range(1, T):
            # Force of infection
            force = beta * S[t - 1] * I[t - 1] / N

            dS = -force
            dE = force - sigma * E[t - 1]
            dI = sigma * E[t - 1] - gamma * I[t - 1]
            dR = gamma * I[t - 1]

            S[t] = max(0, S[t - 1] + dS * self.DT)
            E[t] = max(0, E[t - 1] + dE * self.DT)
            I[t] = max(0, I[t - 1] + dI * self.DT)
            R[t] = max(0, R[t - 1] + dR * self.DT)

        # ── Step 5: Analyze results ──
        peak_infected_idx = int(np.argmax(I))
        peak_infected = int(I[peak_infected_idx])
        total_exposed = int(R[-1] + I[-1] + E[-1])
        total_exposed_pct = round((total_exposed / N) * 100, 2)

        # Time to thresholds
        thresholds = {
            "100K": self._time_to_threshold(I, 100_000),
            "1M": self._time_to_threshold(I, 1_000_000),
            "10M": self._time_to_threshold(I, 10_000_000),
        }

        # Trajectory classification
        if R0 < 1.0:
            trajectory = "CONTAINED"
            severity = "LOW"
            summary = f"Narrative R0 = {R0:.2f}. Below epidemic threshold. The narrative will remain in small echo chambers and naturally decay."
        elif R0 < 2.5:
            trajectory = "SLOW_BURN"
            severity = "MEDIUM"
            summary = f"Narrative R0 = {R0:.2f}. Moderate spread across 2-3 platforms. Expect sustained engagement but not mainstream crossover."
        elif R0 < 5.0:
            trajectory = "VIRAL_OUTBREAK"
            severity = "HIGH"
            summary = f"Narrative R0 = {R0:.2f}. Rapid cross-platform spread. Mainstream news coverage within {peak_infected_idx} hours. Proactive response required."
        else:
            trajectory = "SUPERCRITICAL"
            severity = "CRITICAL"
            summary = f"Narrative R0 = {R0:.2f}. Supercritical cascade. Narrative will dominate news cycle within {min(peak_infected_idx, 24)} hours. War-room activation recommended."

        # Cross-contamination assessment
        if R0 > 5.0:
            contamination = "Jumps from niche social platforms to Mainstream News / Fox / CNN within 12 hours."
        elif R0 > 3.0:
            contamination = "Jumps across 3+ major social networks (Twitter, TikTok, LinkedIn)."
        elif R0 > 1.5:
            contamination = "Contained to 1-2 platforms with organic leakage to news aggregators."
        else:
            contamination = "Contained within the initial triggering platform."

        # ── Step 6: Build time series for frontend charting ──
        # Downsample to every 4 hours for reasonable chart resolution
        sample_interval = 4
        time_series = {
            "hours": list(range(0, T, sample_interval)),
            "susceptible": [int(S[t]) for t in range(0, T, sample_interval)],
            "exposed": [int(E[t]) for t in range(0, T, sample_interval)],
            "infected": [int(I[t]) for t in range(0, T, sample_interval)],
            "recovered": [int(R[t]) for t in range(0, T, sample_interval)],
        }

        return {
            "will_go_viral": R0 >= 1.0,
            "narrative_r0": round(R0, 3),
            "trajectory": trajectory,
            "severity": severity,

            # Peak analysis
            "peak_infected": peak_infected,
            "peak_hour": peak_infected_idx,
            "projected_peak_impressions": peak_infected,
            "hours_to_peak": peak_infected_idx,

            # Total impact
            "total_narrative_reach": total_exposed,
            "population_penetration_pct": total_exposed_pct,

            # Time thresholds
            "time_to_100k": thresholds["100K"],
            "time_to_1m": thresholds["1M"],
            "time_to_10m": thresholds["10M"],

            # SEIR Parameters (for auditability / citation traceback)
            "parameters": {
                "beta": round(beta, 6),
                "sigma": round(sigma, 6),
                "gamma": round(gamma, 6),
                "population": N,
                "initial_infected": I_0,
                "emotion_modifiers_applied": emotions or [],
            },

            # Cross-contamination
            "cross_contamination": contamination,

            # Time series for charting
            "time_series": time_series,

            # Summary
            "summary": summary,

            # Legacy compatibility
            "r0_score": round(R0, 2),
        }

    def simulate_cascade(self, max_virality_score: int, emotions: Optional[List[str]] = None) -> Dict:
        """
        Primary interface — backwards compatible with existing code.
        Wraps the full SEIR simulation for use in simulation_runner.py.
        """
        return self.run_seir_simulation(
            virality_score=max_virality_score,
            emotions=emotions,
        )

    @staticmethod
    def _time_to_threshold(infected_series: np.ndarray, threshold: int) -> str:
        """Calculate hours until infected count reaches a given threshold."""
        indices = np.where(infected_series >= threshold)[0]
        if len(indices) > 0:
            return f"{int(indices[0])} hours"
        return "Never"
