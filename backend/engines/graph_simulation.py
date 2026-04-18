import math

class GraphSimulation:
    """
    Epidemiological projection engine.
    Uses an SEIR (Susceptible, Exposed, Infected, Recovered) model to estimate
    how fast a controversy spreads across a large population.
    """
    def __init__(self, population=10000000):
        self.population = population
        
    def simulate_cascade(self, max_virality_score: int) -> dict:
        """
        Calculate time to reach critical mass (e.g. 1M+ views/anger)
        based on the highest virality risk score (1-10) from the personas.
        """
        # Base R0 calculations mapped from Virality Score (1-10)
        # Low risk (1-3) -> R0 < 1 (dies out)
        # Med risk (4-6) -> R0 ~ 1.5 - 2.5 (slow spread)
        # High risk (7-10) -> R0 ~ 3.0 - 8.0 (viral explosion)
        R0 = max(0.5, (max_virality_score - 2) * 1.2)
        
        # If R0 < 1, outbreak doesn't happen
        if R0 < 1.0:
            return {
                "will_go_viral": False,
                "projected_peak_impressions": int(self.population * 0.001 * max_virality_score),
                "hours_to_peak": 48,
                "time_to_10m": "Never",
                "r0_score": round(R0, 2),
                "summary": "The outrage will remain contained in small echo chambers and naturally dissipate."
            }
            
        # Simplified logistic growth / SEIR peak approximation
        # For a viral event, peak infection rate hits quickly based on R0
        # t_peak roughly proportional to ln(Population) / ln(R0) * contact_time
        contact_time_hours = 2.0  # Time for one person to expose others
        
        math_factor = math.log(self.population) / math.log(max(1.1, R0))
        hours_to_peak = min(168.0, round(math_factor * contact_time_hours, 1))
        
        # Final herd immunity / total exposed
        # If R0 > 3, it hits almost everyone quickly
        final_exposed_ratio = min(0.95, 1.0 - math.exp(-R0))
        peak_impressions = int(self.population * final_exposed_ratio)
        
        # Determine cross-contamination based on R0 severity
        if R0 > 5.0:
            contamination = "Jumps from niche social platforms to Mainstream News / Fox / CNN within 12 hours."
        elif R0 > 3.0:
            contamination = "Jumps across 3+ major social networks (Twitter, TikTok, LinkedIn)."
        else:
            contamination = "Contained primarily within the initial triggering platform."
            
        return {
            "will_go_viral": True,
            "projected_peak_impressions": peak_impressions,
            "hours_to_peak": hours_to_peak,
            "time_to_10m": f"{round(hours_to_peak * 1.5, 1)} hours" if peak_impressions >= 10000000 else "Does not reach 10M",
            "r0_score": round(R0, 2),
            "cross_contamination": contamination,
            "summary": f"With an R0 of {round(R0, 2)}, this will exponentially infect {peak_impressions:,} nodes. Expect peak crisis volume in {hours_to_peak} hours."
        }
