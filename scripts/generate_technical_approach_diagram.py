import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

os.makedirs("/tmp/sih_assets", exist_ok=True)

def generate_technical_approach_exact_reference_diagram():
    # 16:9 widescreen canvas matching official SIH template slide dimensions
    fig, ax = plt.subplots(figsize=(12, 4.8), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4.8)
    ax.axis("off")

    # Clean styling colors from reference
    c_orange_border = "#EA580C"
    c_blue_border = "#2563EB"
    c_purple_border = "#7C3AED"
    c_red_border = "#DC2626"
    c_green_border = "#16A34A"
    c_text_dark = "#0F172A"
    c_text_muted = "#475569"
    c_arrow = "#2563EB"

    # =========================================================================
    # 1. INPUT CIRCULAR CONTAINER (Leftmost Orange Circle)
    # =========================================================================
    # Circle outline
    input_circle = patches.Circle((1.1, 2.4), 1.0, fill=True, fc="#FFF7ED", ec=c_orange_border, lw=2.0)
    ax.add_patch(input_circle)

    # Sub-card 1: Weather Grid
    card1 = patches.FancyBboxPatch((0.35, 2.55), 1.5, 0.6, boxstyle="round,pad=0.04", fc="#FFFFFF", ec="#CBD5E1", lw=1.2)
    ax.add_patch(card1)
    ax.text(1.1, 2.85, "NWP Weather Grid", ha="center", va="center", fontsize=8, fontweight="bold", color=c_text_dark)

    # Sub-card 2: Demographic Data
    card2 = patches.FancyBboxPatch((0.35, 1.65), 1.5, 0.6, boxstyle="round,pad=0.04", fc="#FFFFFF", ec="#CBD5E1", lw=1.2)
    ax.add_patch(card2)
    ax.text(1.1, 1.95, "Census Demographics", ha="center", va="center", fontsize=8, fontweight="bold", color=c_text_dark)

    ax.text(1.1, 1.15, "INPUT", ha="center", va="center", fontsize=9, fontweight="bold", color=c_orange_border)

    # Arrow to Dual Branch Router
    ax.annotate("", xy=(2.4, 2.4), xytext=(2.1, 2.4), arrowprops=dict(arrowstyle="->", color=c_arrow, lw=2.0))

    # =========================================================================
    # 2. DUAL BRANCH ROUTER (Diamond Shape)
    # =========================================================================
    diamond = patches.Polygon([[2.85, 2.4], [3.35, 3.1], [3.85, 2.4], [3.35, 1.7]], closed=True, fc="#EFF6FF", ec=c_blue_border, lw=2.0)
    ax.add_patch(diamond)
    ax.text(3.35, 2.48, "Dual Branch", ha="center", va="center", fontsize=7.5, fontweight="bold", color=c_blue_border)
    ax.text(3.35, 2.32, "Hybrid Engine", ha="center", va="center", fontsize=6.5, fontweight="bold", color=c_blue_border)

    # Branch routing arrows
    # Top branch: Atmospheric
    ax.annotate("", xy=(4.3, 3.4), xytext=(3.55, 2.85), arrowprops=dict(arrowstyle="->", color=c_blue_border, lw=1.8))
    ax.text(3.7, 3.3, "Atmospheric Branch", fontsize=7, fontweight="bold", color=c_blue_border, rotation=25)

    # Bottom branch: Demographic
    ax.annotate("", xy=(4.3, 1.4), xytext=(3.55, 1.95), arrowprops=dict(arrowstyle="->", color=c_blue_border, lw=1.8))
    ax.text(3.7, 1.35, "Vulnerability Branch", fontsize=7, fontweight="bold", color=c_blue_border, rotation=-25)

    # =========================================================================
    # 3. ENCODER MODULES (Purple Rounded Boxes)
    # =========================================================================
    # Top Encoder: Thermal Physics Engine
    enc_top = patches.FancyBboxPatch((4.3, 2.9), 1.9, 1.25, boxstyle="round,pad=0.06", fc="#FAF5FF", ec=c_purple_border, lw=2.0)
    ax.add_patch(enc_top)
    ax.text(5.25, 3.85, "Physics Engine (UTCI)", ha="center", va="center", fontsize=7.5, fontweight="bold", color=c_purple_border)
    ax.text(5.25, 3.5, "• Fiala 187-Node Human Poly", ha="center", va="center", fontsize=6.5, color=c_text_dark)
    ax.text(5.25, 3.3, "• ISO 7243 WBGT Psychrometric", ha="center", va="center", fontsize=6.5, color=c_text_dark)
    ax.text(5.25, 3.1, "• Sweating & Latent Heat Flux", ha="center", va="center", fontsize=6.5, color=c_text_dark)
    ax.text(5.25, 2.75, "Physiological Hazard Features", ha="center", va="center", fontsize=6.5, style="italic", color="#6D28D9")

    # Bottom Encoder: Socio-Demographic HVI Engine
    enc_bot = patches.FancyBboxPatch((4.3, 0.65), 1.9, 1.25, boxstyle="round,pad=0.06", fc="#FAF5FF", ec=c_purple_border, lw=2.0)
    ax.add_patch(enc_bot)
    ax.text(5.25, 1.6, "HVI Vulnerability Model", ha="center", va="center", fontsize=7.5, fontweight="bold", color=c_purple_border)
    ax.text(5.25, 1.25, "• Census 2011 Ward PCA Baseline", ha="center", va="center", fontsize=6.5, color=c_text_dark)
    ax.text(5.25, 1.05, "• Slum Density & Tin Roof Ratio", ha="center", va="center", fontsize=6.5, color=c_text_dark)
    ax.text(5.25, 0.85, "• Elderly & Outdoor Labor Share", ha="center", va="center", fontsize=6.5, color=c_text_dark)
    ax.text(5.25, 0.5, "Demographic Risk Features", ha="center", va="center", fontsize=6.5, style="italic", color="#6D28D9")

    # Arrows to Feature Fusion
    ax.annotate("", xy=(6.55, 2.7), xytext=(6.2, 3.3), arrowprops=dict(arrowstyle="->", color=c_purple_border, lw=1.8))
    ax.annotate("", xy=(6.55, 2.1), xytext=(6.2, 1.5), arrowprops=dict(arrowstyle="->", color=c_purple_border, lw=1.8))

    # =========================================================================
    # 4. FEATURE FUSION CAPSULE (Blue Vertical Hatching Capsule)
    # =========================================================================
    fusion_cap = patches.FancyBboxPatch((6.55, 1.3), 0.95, 2.2, boxstyle="round,pad=0.1", fc="#EFF6FF", ec=c_blue_border, lw=2.0, hatch="//")
    ax.add_patch(fusion_cap)
    
    # White background text box inside capsule
    tb_fusion = patches.FancyBboxPatch((6.6, 1.9), 0.85, 1.0, boxstyle="round,pad=0.02", fc="#FFFFFF", ec=c_blue_border, lw=1.0)
    ax.add_patch(tb_fusion)
    ax.text(7.02, 2.55, "Feature", ha="center", va="center", fontsize=7.5, fontweight="bold", color=c_blue_border)
    ax.text(7.02, 2.4, "Fusion", ha="center", va="center", fontsize=7.5, fontweight="bold", color=c_blue_border)
    ax.text(7.02, 2.15, "Hazard * HVI", ha="center", va="center", fontsize=6.5, fontweight="bold", color=c_orange_border)
    ax.text(7.02, 2.0, "+ Dmult Penalty", ha="center", va="center", fontsize=5.5, color=c_text_muted)

    # Arrow from Fusion to Decoder
    ax.annotate("", xy=(7.9, 2.4), xytext=(7.5, 2.4), arrowprops=dict(arrowstyle="->", color=c_blue_border, lw=2.0))
    ax.text(7.7, 2.55, "Fused Risk", ha="center", va="center", fontsize=6.5, fontweight="bold", color=c_blue_border)

    # =========================================================================
    # 5. DECODER MODULE (Ward Spatial & Action Decoder)
    # =========================================================================
    dec = patches.FancyBboxPatch((7.9, 1.4), 1.9, 2.0, boxstyle="round,pad=0.06", fc="#FAF5FF", ec=c_purple_border, lw=2.0)
    ax.add_patch(dec)
    ax.text(8.85, 3.15, "Action & Spatial Decoder", ha="center", va="center", fontsize=7.5, fontweight="bold", color=c_purple_border)
    ax.text(8.85, 2.75, "Reconstructing Ward Risk", ha="center", va="center", fontsize=7, color=c_text_dark)
    ax.text(8.85, 2.5, "& Generating Advisories", ha="center", va="center", fontsize=7, color=c_text_dark)
    ax.text(8.85, 2.05, "• 0–100 Human Risk Index", ha="center", va="center", fontsize=6.5, color=c_text_dark)
    ax.text(8.85, 1.85, "• Automated NDMA Alerts", ha="center", va="center", fontsize=6.5, color=c_text_dark)
    ax.text(8.85, 1.65, "• NIOSH Work-Rest Ratios", ha="center", va="center", fontsize=6.5, color=c_text_dark)

    # =========================================================================
    # 6. EVALUATION, CONSTRAINTS & RISK CRITERIA (Red Top-Right Boxes)
    # =========================================================================
    # Top Box: Mathematical Loss / Calibration Constraints
    loss_box = patches.FancyBboxPatch((10.15, 2.65), 1.75, 1.5, boxstyle="round,pad=0.04", fc="#FEF2F2", ec=c_red_border, lw=1.8)
    ax.add_patch(loss_box)
    ax.text(11.02, 3.9, "Validation Criteria:", ha="center", va="center", fontsize=7.5, fontweight="bold", color=c_red_border)
    ax.text(10.25, 3.6, "• Epidemiological Calibration", fontsize=6, color=c_text_dark)
    ax.text(10.25, 3.4, "  (Azhar 2014, Mazdiyasni 2017)", fontsize=5.5, color=c_text_muted)
    ax.text(10.25, 3.15, "• Monotonicity Verification", fontsize=6, color=c_text_dark)
    ax.text(10.25, 2.9, "• Nocturnal Strain (Tmin>28°C)", fontsize=6, color=c_text_dark)

    # Bottom Box: Decision Rule Model
    rule_box = patches.FancyBboxPatch((10.15, 1.0), 1.75, 1.45, boxstyle="round,pad=0.04", fc="#FEF2F2", ec=c_red_border, lw=1.8)
    ax.add_patch(rule_box)
    ax.text(11.02, 2.2, "Decision Logic Engine", ha="center", va="center", fontsize=7.5, fontweight="bold", color=c_red_border)
    ax.text(10.25, 1.9, "• Multi-Tier Severity Gates", fontsize=6, color=c_text_dark)
    ax.text(10.25, 1.65, "• Gig Worker Hydration Trigger", fontsize=6, color=c_text_dark)
    ax.text(10.25, 1.4, "• Hospital Surge Bed Alert", fontsize=6, color=c_text_dark)
    ax.text(10.25, 1.15, "• Labor Moratorium (11-4 PM)", fontsize=6, color=c_text_dark)

    # Connecting arrows between Decoder and Logic
    ax.annotate("", xy=(10.15, 3.4), xytext=(9.8, 2.8), arrowprops=dict(arrowstyle="->", color=c_red_border, lw=1.5))
    ax.annotate("", xy=(10.15, 1.7), xytext=(9.8, 2.0), arrowprops=dict(arrowstyle="->", color=c_red_border, lw=1.5))

    # Output Arrow to Final Deliverable
    ax.annotate("", xy=(8.85, 0.6), xytext=(8.85, 1.4), arrowprops=dict(arrowstyle="->", color=c_green_border, lw=2.0))

    # Output Final Pill
    out_pill = patches.FancyBboxPatch((7.7, 0.08), 2.3, 0.5, boxstyle="round,pad=0.04", fc="#F0FDF4", ec=c_green_border, lw=1.8)
    ax.add_patch(out_pill)
    ax.text(8.85, 0.33, "Ward Heat Risk GIS & C2 Alerts", ha="center", va="center", fontsize=7.5, fontweight="bold", color=c_green_border)

    # Evaluation Metrics Callout Pill (Rightmost bottom)
    eval_pill = patches.FancyBboxPatch((10.15, 0.08), 1.75, 0.5, boxstyle="round,pad=0.04", fc="#EFF6FF", ec=c_blue_border, lw=1.5)
    ax.add_patch(eval_pill)
    ax.text(11.02, 0.33, "Lead Time: 72h–120h", ha="center", va="center", fontsize=7.5, fontweight="bold", color=c_blue_border)

    plt.tight_layout()
    out_path = "/tmp/sih_assets/slide3_technical_approach_reference.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print("Exact reference architecture diagram saved to:", out_path)

if __name__ == "__main__":
    generate_technical_approach_exact_reference_diagram()
