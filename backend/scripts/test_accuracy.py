"""
Test Sentimental against real-world crises.
Target: >=8/10 should be flagged as HIGH or CRITICAL.
"""

import asyncio
import httpx

API = "http://localhost:8000"

FAMOUS_CRISES = [
    {
        "name": "Pepsi x Kendall Jenner",
        "content": "What if we could bring the world together with a simple gesture? Watch as Kendall Jenner bridges the divide by sharing a Pepsi with a police officer at a protest. Live for Now.",
        "type": "ad_copy",
        "industry": "food",
        "expected_risk": "HIGH",
        "what_happened": "Massive backlash for trivializing BLM protests. Ad pulled within 24 hours."
    },
    {
        "name": "Bud Light x Dylan Mulvaney",
        "content": "Celebrating 365 days of girlhood with a special commemorative Bud Light can! Cheers to living authentically. #TransVisibility #BudLight",
        "type": "social_post",
        "industry": "food",
        "expected_risk": "HIGH",
        "what_happened": "$1.4B in lost market cap. Boycott from conservative customers."
    },
    {
        "name": "H&M Coolest Monkey",
        "content": "New arrivals for kids! Check out our coolest monkey in the jungle hoodie, modeled by our adorable young model. Shop now at H&M Kids.",
        "type": "ad_copy",
        "industry": "fashion",
        "expected_risk": "CRITICAL",
        "what_happened": "Racist imagery backlash. Stores vandalized. Celebrity endorsements pulled."
    },
    {
        "name": "Balenciaga Holiday Campaign",
        "content": "Our new holiday gift collection features our youngest fans posing with our latest designs, including our plush bear accessories dressed in edgy bondage-inspired outfits. Luxury meets playfulness.",
        "type": "ad_copy",
        "industry": "fashion",
        "expected_risk": "CRITICAL",
        "what_happened": "Child exploitation accusations. Brand nearly collapsed. Multiple lawsuits."
    },
    {
        "name": "Crypto Guaranteed Returns",
        "content": "Invest in our AI crypto trading bot and earn GUARANTEED 500% returns in 90 days. Zero risk. Join 50,000 smart investors. Don't miss out - offer ends Friday!",
        "type": "ad_copy",
        "industry": "fintech",
        "expected_risk": "CRITICAL",
        "what_happened": "SEC enforcement, FTC investigation, class action lawsuits."
    },
    {
        "name": "Weight Loss Miracle",
        "content": "Our revolutionary diet tea CURES obesity and eliminates belly fat in just 7 days. Doctor recommended. No exercise needed. Before and after photos speak for themselves!",
        "type": "ad_copy",
        "industry": "healthcare",
        "expected_risk": "CRITICAL",
        "what_happened": "FTC enforcement. FDA warning letter. Body shaming backlash."
    },
    {
        "name": "Tone Deaf During Crisis",
        "content": "In these unprecedented times, we want you to know that our thoughts are with everyone affected. Meanwhile, enjoy 20% off our entire summer collection! Use code TOGETHER at checkout.",
        "type": "email",
        "industry": "fashion",
        "expected_risk": "HIGH",
        "what_happened": "Profiteering accusations. Boycott campaigns. Media coverage."
    },
    {
        "name": "Diversity Washing",
        "content": "At TechCorp, diversity is in our DNA. We celebrate Black History Month with these inspiring stories. Shop our limited-edition collection with 5% of proceeds going to charity.",
        "type": "social_post",
        "industry": "tech",
        "expected_risk": "HIGH",
        "what_happened": "Performative allyship accusations. Internal employee pushback."
    },
    {
        "name": "Competitor Attack Ad",
        "content": "Unlike our competitors who use cheap overseas labor and outdated technology, we're 100% American-made with the most advanced AI in the market. They can't keep up.",
        "type": "blog_post",
        "industry": "tech",
        "expected_risk": "HIGH",
        "what_happened": "Defamation concerns. FTC 'Made in USA' scrutiny. Competitor response."
    },
    {
        "name": "Safe Content (Control)",
        "content": "We're excited to welcome 12 new team members this quarter. Our engineering and design teams are growing as we work on some exciting updates. More details coming soon!",
        "type": "blog_post",
        "industry": "tech",
        "expected_risk": "LOW",
        "what_happened": "Nothing. This should be flagged LOW."
    },
]

async def test_all():
    correct = 0
    total = len(FAMOUS_CRISES)

    print("=" * 60)
    print("SENTIMENTAL ACCURACY TEST")
    print(f"Testing against {total} real-world crisis scenarios")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=120.0) as client:
        for i, crisis in enumerate(FAMOUS_CRISES):
            print(f"\n--- Test {i+1}/{total}: {crisis['name']} ---")

            try:
                response = await client.post(f"{API}/api/analyze", json={
                    "content": crisis["content"],
                    "content_type": crisis["type"],
                    "industry": crisis["industry"],
                })

                if response.status_code == 200:
                    result = response.json()
                    risk = result.get("risk_level", "UNKNOWN")
                    confidence = result.get("confidence", 0)
                    triggers = len(result.get("trigger_phrases", []))
                    regulatory = len(result.get("regulatory_issues", []))

                    expected = crisis["expected_risk"]
                    high_risks = ["HIGH", "CRITICAL"]

                    if expected in high_risks:
                        is_correct = risk in high_risks
                    else:
                        is_correct = risk not in high_risks

                    if is_correct:
                        correct += 1

                    status = "PASS" if is_correct else "FAIL"

                    print(f"  {status} Predicted: {risk} (confidence {confidence}/10)")
                    print(f"     Expected: {expected}")
                    print(f"     Triggers: {triggers} | Regulatory: {regulatory}")
                    print(f"     What happened: {crisis['what_happened'][:80]}")

                else:
                    print(f"  FAIL HTTP Error: {response.status_code}")
                    print(f"     {response.text[:200]}")

            except Exception as e:
                print(f"  FAIL Error: {e}")

    print("\n" + "=" * 60)
    print(f"ACCURACY: {correct}/{total} ({correct/total*100:.0f}%)")
    print(f"   Target: >=80% (>={int(total*0.8)}/{total})")

    if correct / total >= 0.8:
        print("   PASSED -- Prompt is ready for production!")
    else:
        print("   NEEDS WORK -- Refine prompt and retest")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_all())
