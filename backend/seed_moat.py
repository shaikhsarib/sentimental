"""
SentiFlow V5: Tactical Moat Seeder
==================================
Bulk-injects high-stakes historical crises into the CrisisDatabase.
Targets the same database path as main.py (data/sentimental.db).
"""

import sqlite3
import json
import os
import uuid

# Configuration
DB_PATH = "data/sentimental.db"

CRISES = [
    {
        "id": "crowdstrike-outage-2024",
        "brand": "CrowdStrike",
        "date": "2024-07-19",
        "original_content": "A faulty sensor configuration update for Windows systems. Triggered Blue Screen of Death (BSOD) globally.",
        "content_type": "text",
        "industry": "technology",
        "crisis_summary": "Largest IT outage in history. Affected airlines, hospitals, banks, and government services globally.",
        "trigger_phrases": json.dumps(["Blue Screen of Death", "BSOD", "Falcon Sensor update", "FalconAgent.sys"]),
        "first_platform": "Reddit/Twitter",
        "primary_attacker_type": "journalist",
        "coalition_formed": json.dumps(["journalist", "regulator", "competitor"]),
        "hour_1": "IT admins report mass BSODs on Reddit and X. Initial panic as cyberattack suspected.",
        "hour_6": "CrowdStrike CEO confirms it's not a cyberattack but a faulty update. Global travel halted.",
        "hour_24": "George Kurtz apologizes on NBC. Recovery estimates stretch to weeks.",
        "day_7": "8.5 million devices affected. Total economic loss estimated at $5.4B.",
        "revenue_impact": "$500M+ in direct remediation costs. Billions in potential lawsuits.",
        "stock_impact": "-25% in 48 hours.",
        "brand_sentiment_change": "-60% among IT Decision Makers.",
        "root_cause": "Failed CI/CD pipeline and lack of staged rollout for critical kernel-level drivers.",
        "warning_signs": json.dumps(["Automatic updates for kernel drivers", "Single point of failure", "Global deployment without canary testing"]),
        "what_would_have_prevented_it": "Staged rollouts, local testing before global push, and enhanced kernel-level safety checks.",
        "sources": json.dumps(["CNBC", "The Verge", "Reuters"])
    },
    {
        "id": "svb-bank-run-2023",
        "brand": "Silicon Valley Bank",
        "date": "2023-03-09",
        "original_content": "Announcement of $1.75B capital raise after selling $21B of bonds at a $1.8B loss. Keywords: capital raise, bond sale, loss.",
        "content_type": "press_release",
        "industry": "finance",
        "crisis_summary": "First social-media fueled bank run. VC influencers on X triggered mass withdrawals in 48 hours.",
        "trigger_phrases": json.dumps(["liquidity concerns", "capital raise", "bank run", "withdraw your funds", "get your cash out"]),
        "first_platform": "Twitter (X)",
        "primary_attacker_type": "investor",
        "coalition_formed": json.dumps(["investor", "journalist", "regulator"]),
        "hour_1": "VCs begin DM-ing portfolio companies to move cash. Public tweets begin appearing.",
        "hour_6": "Founders post screenshots of stuck wire transfers. 'SVB is insolvent' goes viral.",
        "hour_24": "Bank stock halted after 60% drop. FDIC steps in.",
        "day_7": "Bank seized. Emergency measures taken by Fed to prevent systemic contagion.",
        "revenue_impact": "Total collapse of the institution.",
        "stock_impact": "-100% (delisted).",
        "brand_sentiment_change": "Total loss of trust.",
        "root_cause": "Interest rate risk mismanagement combined with a highly concentrated, digitally connected depositor base.",
        "warning_signs": json.dumps(["High concentration of uninsured deposits", "Viral panic among influential DMs", "Digital-speed withdrawals"]),
        "what_would_have_prevented_it": "Earlier capital raise, better interest rate hedging, and communication with key VC influencers.",
        "sources": json.dumps(["WSJ", "Bloomberg", "FT"])
    },
    {
        "id": "peloton-tread-recall-2021",
        "brand": "Peloton",
        "date": "2021-04-17",
        "original_content": "CPSC warning to stop using Tread+ after child death and multiple injuries. Peloton initially refused to recall.",
        "content_type": "press_release",
        "industry": "consumer_goods",
        "crisis_summary": "Brand prioritized legal defense over safety. Initially fought federal safety warnings, alienating parents.",
        "trigger_phrases": json.dumps(["safety warning", "child death", "recall refused", "not a design flaw"]),
        "first_platform": "Facebook/News Outlets",
        "primary_attacker_type": "parent",
        "coalition_formed": json.dumps(["parent", "regulator", "journalist"]),
        "hour_1": "CPSC issues 'urgent' warning. Peloton calls it 'inaccurate and misleading'.",
        "hour_6": "Outrage among parent groups on Facebook. Viral videos of Tread+ safety issues.",
        "hour_24": "Major news networks cover the child death and Peloton's refusal to recall.",
        "day_7": "Stock plummets. Peloton finally issues full recall and apology.",
        "revenue_impact": "$400M+ in lost revenue and recall costs.",
        "stock_impact": "-35% in one week.",
        "brand_sentiment_change": "-45% among primary target demographic (parents).",
        "root_cause": "Initial defensive legal posture over consumer safety empathy.",
        "warning_signs": json.dumps(["Federal agency safety warnings", "Child safety incidents", "Defensive response to tragic news"]),
        "what_would_have_prevented_it": "Immediate recall and humble response to the first safety report.",
        "sources": json.dumps(["NYT", "CNN", "The Verge"])
    },
    {
        "id": "united-3411-2017",
        "brand": "United Airlines",
        "date": "2017-04-09",
        "original_content": "Video of Dr. David Dao being forcibly dragged off an overbooked flight. Keywords: overbooked, dragged, police on board.",
        "content_type": "social_post",
        "industry": "travel",
        "crisis_summary": "Viral video of customer mistreatment. CEO's initial response blamed the passenger, fueling global outrage.",
        "trigger_phrases": json.dumps(["overbooked flight", "re-accommodate", "forcibly removed", "belligerent passenger"]),
        "first_platform": "Twitter (X)",
        "primary_attacker_type": "genz",
        "coalition_formed": json.dumps(["genz", "journalist", "regulator"]),
        "hour_1": "Cell phone video posted on Twitter. Reaches 1M views in 2 hours.",
        "hour_6": "CEO Oscar Munoz issues internal memo calling passenger 'disruptive and belligerent'. Memo leaks.",
        "hour_24": "Global boycott calls. United stock drops $250M in value.",
        "day_7": "United reaches settlement with Dao. Announces policy changes for overbooked flights.",
        "revenue_impact": "$250M+ in market cap lost. $10M+ estimated settlement.",
        "stock_impact": "-4% in 24 hours.",
        "brand_sentiment_change": "Net Sentiment dropped from +15 to -70 in one week.",
        "root_cause": "Prioritizing internal policy and bureaucratic efficiency over basic human dignity.",
        "warning_signs": json.dumps(["Viral video of physical mistreatment", "CEO doubling down on victim-blaming", "Overbooking policies"]),
        "what_would_have_prevented_it": "Better overbooking incentives and an immediate, non-defensive apology.",
        "sources": json.dumps(["CNN", "Reuters", "BBC"])
    },
    {
        "id": "balenciaga-gift-shop-2022",
        "brand": "Balenciaga",
        "date": "2022-11-16",
        "original_content": "Holiday campaign featuring children holding teddy bears in BDSM gear. Keywords: holiday gift shop, teddy bear.",
        "content_type": "ad_copy",
        "industry": "fashion",
        "crisis_summary": "Luxury brand accused of sexualizing children. Social media conspiracy theories (QAnon-adjacent) amplified the outrage.",
        "trigger_phrases": json.dumps(["child models", "BDSM bears", "inappropriate imagery", "sexualizing children"]),
        "first_platform": "Twitter (X)",
        "primary_attacker_type": "parent",
        "coalition_formed": json.dumps(["parent", "conservative", "genz"]),
        "hour_1": "Users spot BDSM gear on bears. Screenshots circulate.",
        "hour_6": "Second campaign spotted with legal documents about child pornography laws. Outrage explodes.",
        "hour_24": "Balenciaga pulls ads. Blames third-party production team.",
        "day_7": "#CancelBalenciaga trending worldwide. Brand loses celebrity ambassadors.",
        "revenue_impact": "Significant loss in Q4 sales. Celebrity fallout.",
        "stock_impact": "N/A (Private company parent Kering dropped 5%).",
        "brand_sentiment_change": "-80% in US market.",
        "root_cause": "Extreme 'edge' marketing without basic child safety or decency review.",
        "warning_signs": json.dumps(["Controversial child imagery", "Overlapping controversies in short period", "Blaming third parties"]),
        "what_would_have_prevented_it": "External sensitivity review for all marketing campaigns.",
        "sources": json.dumps(["Vogue", "NYT", "Fox News"])
    },
    {
        "id": "terra-luna-crash-2022",
        "brand": "Terraform Labs",
        "date": "2022-05-07",
        "original_content": "UST stablecoin loses 1:1 peg with USD. Keywords: de-peg, death spiral, burn LUNA.",
        "content_type": "text",
        "industry": "technology",
        "crisis_summary": "Collateralized algorithmic stablecoin collapse. Erased $40B in market value in one week.",
        "trigger_phrases": json.dumps(["UST de-peg", "death spiral", "LUNA collapse", "Do Kwon"]),
        "first_platform": "Twitter (Crypto Twitter)",
        "primary_attacker_type": "investor",
        "coalition_formed": json.dumps(["investor", "regulator", "journalist"]),
        "hour_1": "UST hits $0.98. Do Kwon tweets 'Steady lads. Deploying more capital.'",
        "hour_6": "UST falls to $0.90. LUNA supply hyper-inflating.",
        "hour_24": "Total panic. Crypto exchanges halt trading. UST at $0.60.",
        "day_7": "UST at $0.05. LUNA effectively zero. $40B vanished.",
        "revenue_impact": "$40B market cap loss. Dozen crypto firms bankrupted by association.",
        "stock_impact": "N/A.",
        "brand_sentiment_change": "Total collapse of trust in algorithmic stablecoins.",
        "root_cause": "Flawed economic design (algorithmic peg) combined with lack of transparency.",
        "warning_signs": json.dumps(["Unbacked algorithmic peg", "Unsustainable high-yield promises", "Aggressive CEO behavior"]),
        "what_would_have_prevented_it": "Earlier de-leveraging and transparent collateralization.",
        "sources": json.dumps(["Coindesk", "FT", "Bloomberg"])
    },
    {
        "id": "ftx-insolvency-2022",
        "brand": "FTX",
        "date": "2022-11-06",
        "original_content": "CoinDesk report showing Alameda Research's balance sheet is mostly FTT. CZ (Binance) announces selling all FTT.",
        "content_type": "text",
        "industry": "finance",
        "crisis_summary": "Fraudulent use of customer funds revealed. Collapsed in 7 days. CEO SBF arrested.",
        "trigger_phrases": json.dumps(["insolvency", "customer funds", "Alameda Research", "FTT liquidations", "SBF"]),
        "first_platform": "Twitter (X)",
        "primary_attacker_type": "investor",
        "coalition_formed": json.dumps(["investor", "regulator", "journalist"]),
        "hour_1": "Binance CEO tweets intention to liquidate FTT. Bank run begins.",
        "hour_6": "FTX withdrawal times spike. SBF tweets 'FTX is fine. Assets are fine.' (Later deleted).",
        "hour_24": "Withdrawals halted. FTX seeks $8B emergency funding.",
        "day_7": "FTX files for Chapter 11 bankruptcy. SBF resigns.",
        "revenue_impact": "$32B valuation to zero. $8B in missing customer funds.",
        "stock_impact": "N/A.",
        "brand_sentiment_change": "Total trust collapse. Becomes symbol of crypto fraud.",
        "root_cause": "Commingling customer funds and massive corporate fraud.",
        "warning_signs": json.dumps(["Close relationship with trading arm", "Illiquid token as primary asset", "Lack of independent board"]),
        "what_would_have_prevented_it": "Regulatory oversight and honest accounting.",
        "sources": json.dumps(["NYT", "CoinDesk", "WSJ"])
    }
]

def init_db(cursor):
    """Ensure tables exist before seeding."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crises (
            id TEXT PRIMARY KEY, brand TEXT, date TEXT,
            original_content TEXT, content_type TEXT, industry TEXT,
            crisis_summary TEXT, trigger_phrases TEXT, first_platform TEXT,
            primary_attacker_type TEXT, attacker_demographics TEXT, coalition_formed TEXT,
            hour_1 TEXT, hour_6 TEXT, hour_24 TEXT, day_7 TEXT, day_30 TEXT,
            revenue_impact TEXT, stock_impact TEXT, brand_sentiment_change TEXT,
            customer_churn TEXT, legal_consequences TEXT,
            brand_response TEXT, response_effectiveness TEXT, recovery_timeline TEXT,
            root_cause TEXT, warning_signs TEXT, what_would_have_prevented_it TEXT,
            similar_crises TEXT, sources TEXT, confidence_in_data TEXT,
            added_date TEXT DEFAULT CURRENT_TIMESTAMP, last_updated TEXT
        )
    """)
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS crises_fts 
        USING fts5(brand, original_content, crisis_summary, trigger_phrases, root_cause, warning_signs, content='crises', content_rowid='rowid')
    """)

def seed_database():
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    init_db(cursor)

    print(f"[*] Seeding {len(CRISES)} high-stakes crises into {DB_PATH}...")

    for c in CRISES:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO crises (
                    id, brand, date, original_content, content_type, industry,
                    crisis_summary, trigger_phrases, first_platform,
                    primary_attacker_type, coalition_formed,
                    hour_1, hour_6, hour_24, day_7,
                    revenue_impact, stock_impact, brand_sentiment_change,
                    root_cause, warning_signs, what_would_have_prevented_it, sources
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                c["id"], c["brand"], c["date"], c["original_content"], c["content_type"], c["industry"],
                c["crisis_summary"], c["trigger_phrases"], c["first_platform"],
                c["primary_attacker_type"], c["coalition_formed"],
                c["hour_1"], c["hour_6"], c["hour_24"], c["day_7"],
                c["revenue_impact"], c["stock_impact"], c["brand_sentiment_change"],
                c["root_cause"], c["warning_signs"], c["what_would_have_prevented_it"], c["sources"]
            ))
            print(f"  [+] Seeded: {c['brand']}")
        except Exception as e:
            print(f"  [!] Error seeding {c['brand']}: {e}")

    conn.commit()
    conn.close()
    print("[*] Seeding complete. Your 'Collective Memory' has been upgraded.")

if __name__ == "__main__":
    seed_database()
