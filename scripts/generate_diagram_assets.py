import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

os.makedirs("/tmp/sih_assets", exist_ok=True)

# 1. Slide 2 Architecture Flow Diagram
def generate_slide2_diagram():
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.5)
    ax.axis("off")

    # Colors
    c_blue = "#0284C7"
    c_navy = "#0F2C59"
    c_orange = "#EA580C"
    c_green = "#16A34A"
    c_red = "#DC2626"
    c_gray_bg = "#F8FAFC"

    # Background canvas
    rect_bg = patches.FancyBboxPatch((0.1, 0.1), 9.8, 4.3, boxstyle="round,pad=0.1", fc=c_gray_bg, ec="#CBD5E1", lw=1.5)
    ax.add_patch(rect_bg)

    # Box 1: Ingestion
    b1 = patches.FancyBboxPatch((0.4, 0.6), 2.0, 3.2, boxstyle="round,pad=0.08", fc="#F0F9FF", ec=c_blue, lw=1.5)
    ax.add_patch(b1)
    ax.text(1.4, 3.4, "1. INGESTION", ha="center", va="center", fontsize=10, fontweight="bold", color=c_navy)
    ax.text(1.4, 2.3, "• NWP 5-Day Hourly\n  (T, RH, Wind, Rad)\n• NASA 40-Yr Normal\n• Census 2011 PCA\n• Satellite LST / NDVI", ha="center", va="center", fontsize=8, color="#1E293B", linespacing=1.4)

    # Arrow 1 -> 2
    ax.annotate("", xy=(2.75, 2.2), xytext=(2.45, 2.2), arrowprops=dict(arrowstyle="->", color=c_blue, lw=2))

    # Box 2: Thermal & HVI Engines
    b2 = patches.FancyBboxPatch((2.8, 0.6), 2.1, 3.2, boxstyle="round,pad=0.08", fc="#F0FDF4", ec=c_green, lw=1.5)
    ax.add_patch(b2)
    ax.text(3.85, 3.4, "2. THERMAL ENGINE", ha="center", va="center", fontsize=10, fontweight="bold", color=c_green)
    ax.text(3.85, 2.3, "• UTCI 6th-Order Poly\n  (Fiala 187-node)\n• ISO 7243 WBGT\n• Heat Index (NOAA)\n• Night Strain (Tmin)", ha="center", va="center", fontsize=8, color="#1E293B", linespacing=1.4)

    # Arrow 2 -> 3
    ax.annotate("", xy=(5.25, 2.2), xytext=(4.95, 2.2), arrowprops=dict(arrowstyle="->", color=c_green, lw=2))

    # Box 3: AI & Risk Synthesis
    b3 = patches.FancyBboxPatch((5.3, 0.6), 2.1, 3.2, boxstyle="round,pad=0.08", fc="#FEF2F2", ec=c_red, lw=1.5)
    ax.add_patch(b3)
    ax.text(6.35, 3.4, "3. AI RISK MODEL", ha="center", va="center", fontsize=10, fontweight="bold", color=c_red)
    ax.text(6.35, 2.3, "• Demographic HVI\n• Relative Risk Curve\n  (Azhar/Mazdiyasni)\n• Multi-Day Dmult\n• 0–100 Health Score", ha="center", va="center", fontsize=8, color="#1E293B", linespacing=1.4)

    # Arrow 3 -> 4
    ax.annotate("", xy=(7.75, 2.2), xytext=(7.45, 2.2), arrowprops=dict(arrowstyle="->", color=c_red, lw=2))

    # Box 4: Action & Dispatch
    b4 = patches.FancyBboxPatch((7.8, 0.6), 1.8, 3.2, boxstyle="round,pad=0.08", fc="#FEF3C7", ec=c_orange, lw=1.5)
    ax.add_patch(b4)
    ax.text(8.7, 3.4, "4. ACTION LAYER", ha="center", va="center", fontsize=10, fontweight="bold", color=c_orange)
    ax.text(8.7, 2.3, "• Ward GIS Map\n• Hospital Surge Alert\n• NIOSH Labor Halt\n• NDMA Playbooks\n• WhatsApp/SMS", ha="center", va="center", fontsize=8, color="#1E293B", linespacing=1.4)

    plt.tight_layout()
    out_path = "/tmp/sih_assets/slide2_flowchart.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved:", out_path)

# 2. Slide 3 Working Prototype & GIS UI Mockup
def generate_slide3_ui_mockup():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2), dpi=300, gridspec_kw={'width_ratios': [1.2, 1]})
    
    # Left: GIS Ward Risk Map (Simulated Delhi/Ahmedabad Ward Choropleth)
    ax1.set_title("Live GIS Ward-Level Heat Risk Choropleth", fontsize=10, fontweight="bold", color="#0F2C59")
    np.random.seed(42)
    wards = ["Ward A (Slum Hub)", "Ward B (Industrial)", "Ward C (Residential)", "Ward D (Affluent/Greened)", "Ward E (Commercial)"]
    risk_scores = [88.5, 76.2, 54.0, 32.8, 69.4]
    colors = ["#DC2626", "#EA580C", "#FBBF24", "#16A34A", "#F97316"]
    
    y_pos = np.arange(len(wards))
    bars = ax1.barh(y_pos, risk_scores, color=colors, height=0.55, edgecolor="#334155")
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(wards, fontsize=8, fontweight="bold")
    ax1.set_xlabel("Relative Human Heat-Health Risk Index (0–100)", fontsize=8, fontweight="bold")
    ax1.set_xlim(0, 100)
    ax1.grid(axis="x", linestyle="--", alpha=0.5)
    
    for bar, score in zip(bars, risk_scores):
        ax1.text(score + 1.5, bar.get_y() + bar.get_height()/2, f"{score:.1f}", va="center", fontsize=8, fontweight="bold", color="#0F172A")
    ax1.invert_yaxis()

    # Right: 5-Day Multi-Metric Forecast Curve (UTCI vs WBGT vs Air Temp)
    ax2.set_title("5-Day Lead Biometeorological Forecast", fontsize=10, fontweight="bold", color="#0F2C59")
    days = ["D-5", "D-4", "D-3", "D-2", "D-1"]
    temp = [38, 40, 42, 44, 43]
    utci = [42, 45, 48, 51, 49]
    wbgt = [29, 31, 33, 35, 34]
    
    ax2.plot(days, utci, marker="o", color="#DC2626", linewidth=2, label="UTCI (°C - Fiala)")
    ax2.plot(days, temp, marker="s", color="#EA580C", linewidth=2, linestyle="--", label="Dry-Bulb (°C)")
    ax2.plot(days, wbgt, marker="^", color="#0284C7", linewidth=2, label="ISO WBGT (°C)")
    
    # Critical threshold lines
    ax2.axhline(46, color="#991B1B", linestyle=":", label="UTCI Extreme (>46°C)")
    ax2.axhline(32, color="#0369A1", linestyle=":", label="NIOSH Work Halt (>32°C)")
    
    ax2.set_ylabel("Temperature / Index (°C)", fontsize=8, fontweight="bold")
    ax2.set_xlabel("Forecast Lead Time", fontsize=8, fontweight="bold")
    ax2.legend(fontsize=7, loc="lower left", framealpha=0.8)
    ax2.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    out_path = "/tmp/sih_assets/slide3_gis_curves.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved:", out_path)

# 3. Slide 5 Pre-Emptive Timeline Diagram
def generate_slide5_timeline_diagram():
    fig, ax = plt.subplots(figsize=(10, 2.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 2.5)
    ax.axis("off")

    # Horizontal backbone line
    ax.plot([0.8, 9.2], [1.2, 1.2], color="#0F2C59", lw=4, zorder=1)

    milestones = [
        ("D-5 (120h)", "Thermal Moisture\nSurge Detected", "#0284C7", 1.2),
        ("D-3 (72h)", "Water Tankers &\nCool Shelters", "#EA580C", 3.2),
        ("D-2 (48h)", "Hospital Surge Beds\n& ORS Staged", "#DC2626", 5.2),
        ("D-1 (24h)", "Mandatory NIOSH\nLabor Halts", "#D97706", 7.2),
        ("D-Day (Peak)", "Zero Mass-Casualty\nHeat Disasters", "#16A34A", 8.8)
    ]

    for label, desc, col, x in milestones:
        # Circle node
        circle = patches.Circle((x, 1.2), 0.28, fc=col, ec="#FFFFFF", lw=2, zorder=2)
        ax.add_patch(circle)
        ax.text(x, 1.2, label.split()[0], ha="center", va="center", color="#FFFFFF", fontsize=7.5, fontweight="bold", zorder=3)
        
        # Label above
        ax.text(x, 1.8, label, ha="center", va="center", color=col, fontsize=8.5, fontweight="bold")
        # Description below
        ax.text(x, 0.55, desc, ha="center", va="center", color="#1E293B", fontsize=7.5, fontweight="bold", linespacing=1.2)

    plt.tight_layout()
    out_path = "/tmp/sih_assets/slide5_timeline.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved:", out_path)

generate_slide2_diagram()
generate_slide3_ui_mockup()
generate_slide5_timeline_diagram()
