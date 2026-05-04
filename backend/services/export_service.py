import os
from datetime import datetime
from fpdf import FPDF
from typing import Dict

class ExportService:
    """
    SentiFlow V6 Strategic Brief Export Service (Institutional-Grade PDF).
    Blueprint Page 35-36.
    """
    
    def __init__(self, export_dir: str = "storage/exports"):
        self.export_dir = export_dir
        os.makedirs(self.export_dir, exist_ok=True)

    def generate_strategic_brief(self, project_id: str, debate_results: Dict, queries: Dict = None) -> str:
        """
        Generates a comprehensive PDF strategic brief.
        """
        filename = f"Strategic_Brief_{project_id}_{int(datetime.now().timestamp())}.pdf"
        filepath = os.path.join(self.export_dir, filename)
        
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # 1. Header (Institutional Branding)
        pdf.set_fill_color(2, 6, 23) # Dark Navy
        pdf.rect(0, 0, 210, 40, 'F')
        
        pdf.set_font("Helvetica", "B", 24)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(10, 10)
        pdf.cell(0, 15, "SENTIFLOW V6", ln=True)
        
        pdf.set_font("Helvetica", "", 10)
        pdf.set_xy(10, 25)
        pdf.cell(0, 5, "INSTITUTIONAL STRATEGIC INTELLIGENCE BRIEF // CONFIDENTIAL", ln=True)
        
        pdf.set_text_color(0, 0, 0)
        pdf.ln(20)
        
        # 2. Executive Summary (Arbiter Verdict)
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "1. EXECUTIVE ARBITRATION VERDICT", ln=True)
        pdf.set_font("Helvetica", "", 11)
        verdict = debate_results.get("judge_verdict", {}).get("consolidated_verdict", "No verdict available.")
        pdf.multi_cell(0, 6, verdict)
        pdf.ln(10)
        
        # 3. Sentiment Cascade (R0 & Infection)
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "2. NARRATIVE CONTAGION ANALYSIS", ln=True)
        pdf.set_font("Helvetica", "", 11)
        cascade = debate_results.get("cascade", {}).get("metadata", {})
        pdf.cell(0, 8, f"Narrative R0 (Contagion Rate): {cascade.get('r_naught', 'N/A')}", ln=True)
        pdf.cell(0, 8, f"Peak Infection (Pop. Impact): {cascade.get('peak_infection', 'N/A')}", ln=True)
        pdf.cell(0, 8, f"Total Affected Agents: {cascade.get('total_affected', 'N/A')}", ln=True)
        pdf.ln(10)
        
        # 4. Hierarchical Consensus
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "3. HIERARCHICAL CONSENSUS MATRICS", ln=True)
        consensus = debate_results.get("consensus", {})
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, f"Final Confidence Index: {consensus.get('final_confidence', 'N/A')}", ln=True)
        
        pdf.set_font("Helvetica", "", 10)
        scores = consensus.get("layer_scores", {})
        pdf.cell(0, 8, f"- Mass Consensus Layer: {scores.get('mass', 'N/A')}", ln=True)
        pdf.cell(0, 8, f"- Representative Layer: {scores.get('representative', 'N/A')}", ln=True)
        pdf.cell(0, 8, f"- Institutional Arbiter Layer: {scores.get('judge', 'N/A')}", ln=True)
        pdf.ln(10)
        
        # 5. Multi-Perspective Insights (if available)
        if queries:
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, "4. MULTI-PERSPECTIVE INTELLIGENCE", ln=True)
            for p_name, data in queries.items():
                pdf.set_font("Helvetica", "B", 12)
                pdf.set_text_color(100, 100, 255)
                pdf.cell(0, 10, f"LENS: {p_name.upper()}", ln=True)
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Helvetica", "I", 10)
                pdf.multi_cell(0, 6, f"Synthesis: {data.get('synthesis', 'N/A')}")
                pdf.ln(5)
        
        # 6. Topology Metadata
        pdf.set_y(-30)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(0, 10, f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} // Project ID: {project_id}", align='C')
        
        pdf.output(filepath)
        return filename
