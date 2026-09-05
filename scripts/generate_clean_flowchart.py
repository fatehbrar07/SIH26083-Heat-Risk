import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

os.makedirs("/home/ubuntu/sih26083-heat-risk/docs/sih", exist_ok=True)

def generate_clean_architecture_flowchart():
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis("off")

    # Colors
    c_bg = "#F8FAFC"
    c_navy = "#0F2C59"
    c_blue = "#0284C7"
    c_blue_light = "#F0F9FF"
    c_green = "#16A34A"
    c_green_light = "#F0FDF4"
    c_red = "#DC2626"
    c_red_light = "#FEF2F2"
    c_orange = "#EA580C"
    c_orange_light = "#FEF3C7"
    c_purple = "#7C3AED"
    c_purple_light = "#F5F3FF"
    c_text_dark = "#1E293B"
    c_text_muted = "#475569"

    # Main canvas
    bg_rect = patches.FancyBboxPatch((0.2, 0.2), 15.6, 8.6, boxstyle="round,pad=0.2", fc=c_bg, ec="#E2E8F0", lw=2)
    ax.add_patch(bg_rect)

    # Title Banner
    title_rect = patches.FancyBboxPatch((0.6, 7.8), 14.8, 0.85, boxstyle="round,pad=0.1", fc=c_navy, ec="none")
    ax.add_patch(title_rect)
    ax.text(8.0, 8.35, "THERMOSHIELD — END-TO-END SYSTEM ARCHITECTURE FLOWCHART", ha="center", va="center", fontsize=16, fontweight="bold", color="#FFFFFF", fontfamily="sans-serif")
    ax.text(8.0, 7.98, "From Numerical Weather Prediction → Physiological Thermal Stress → Ward Vulnerability → Multi-Sector Automated Action", ha="center", va="center", fontsize=10, color="#BAE6FD", fontfamily="sans-serif")

    # 4 Main Columns / Pipeline Stages
    col_w = 3.35
    col_gap = 0.35
    left_start = 0.8
    card_y = 1.3
    card_h = 6.1

    stages = [
        ("STAGE 1: DATA INGESTION", c_blue, c_blue_light, [
            ("Atmospheric NWP Feeds", "• Open-Meteo 0.1° ECMWF/GFS\n• 5-Day hourly: T, RH, Wind, Rad\n• Automated keyless API pipeline"),
            ("Climatological Baseline", "• NASA POWER MERRA-2\n• 40-Year normal thresholds\n• Historical temperature anomalies"),
            ("Demographic & Urban Data", "• Census 2011 PCA (Ward level)\n• Slum density, elderly, laborers\n• Landsat/Sentinel NDVI canopy")
        ]),
        ("STAGE 2: THERMAL STRESS", c_green, c_green_light, [
            ("UTCI Physiological Model", "• Universal Thermal Climate Index\n• 6th-Order 187-Node Fiala Poly\n• Acc. for radiation & wind chill"),
            ("ISO 7243 WBGT Standard", "• Wet-Bulb Globe Temperature\n• Stull psychrometric Tw formula\n• Liljegren globe Tg calculation"),
            ("Persistence Multipliers", "• Multi-day duration penalty (Dmult)\n• Night recovery deficit (Tmin > 28°C)\n• Cumulative metabolic strain")
        ]),
        ("STAGE 3: AI RISK & HVI", c_red, c_red_light, [
            ("Heat Vulnerability Index", "• Multi-criteria demographic HVI\n• Slum housing & tin-roof factor\n• Outdoor gig worker density"),
            ("Epidemiological Dose-Response", "• Calibrated to Indian studies\n• Azhar et al. (PLoS ONE 2014)\n• Mazdiyasni et al. (PNAS 2017)"),
            ("Dynamic 0–100 Risk Score", "• Normalized Heat-Health Index\n• Relative risk categorization\n• Bounded scientific estimation")
        ]),
        ("STAGE 4: ACTION & DISPATCH", c_orange, c_orange_light, [
            ("Interactive Leaflet GIS", "• Live ward choropleth maps\n• 5-Day hourly trend curves\n• Real-time ward search & filtering"),
            ("Institutional Triggers", "• Hospital surge bed alerts (72h)\n• Municipal water tanker routes\n• NIOSH work halt (11 AM–4 PM)"),
            ("Public Alerting Channels", "• Vernacular WhatsApp/SMS\n• Telegram Alert Bot\n• 25 Production REST APIs")
        ])
    ]

    for idx, (s_title, s_border, s_bg, items) in enumerate(stages):
        cx = left_start + idx * (col_w + col_gap)
        
        # Outer Card
        card = patches.FancyBboxPatch((cx, card_y), col_w, card_h, boxstyle="round,pad=0.15", fc="#FFFFFF", ec=s_border, lw=2)
        ax.add_patch(card)

        # Stage Header Box
        s_hdr = patches.FancyBboxPatch((cx + 0.1, card_y + card_h - 0.65), col_w - 0.2, 0.55, boxstyle="round,pad=0.08", fc=s_bg, ec=s_border, lw=1.2)
        ax.add_patch(s_hdr)
        ax.text(cx + col_w / 2, card_y + card_h - 0.38, s_title, ha="center", va="center", fontsize=10.5, fontweight="bold", color=s_border)

        # 3 Inner Sub-Cards
        sub_y_start = card_y + card_h - 0.9
        sub_h = 1.6
        sub_gap = 0.15

        for sub_idx, (sub_title, sub_desc) in enumerate(items):
            sy = sub_y_start - (sub_idx + 1) * sub_h - sub_idx * sub_gap + 0.15
            sub_card = patches.FancyBboxPatch((cx + 0.15, sy), col_w - 0.3, sub_h, boxstyle="round,pad=0.08", fc=c_bg, ec="#CBD5E1", lw=1)
            ax.add_patch(sub_card)

            # Sub-card Title
            ax.text(cx + 0.3, sy + sub_h - 0.25, sub_title, ha="left", va="center", fontsize=9, fontweight="bold", color=c_navy)
            # Sub-card Body
            ax.text(cx + 0.3, sy + (sub_h - 0.35) / 2, sub_desc, ha="left", va="center", fontsize=7.8, color=c_text_dark, linespacing=1.35)

        # Connecting Arrow to Next Stage
        if idx < 3:
            arrow_x1 = cx + col_w + 0.05
            arrow_x2 = cx + col_w + col_gap - 0.05
            arrow_y = card_y + card_h / 2
            ax.annotate("", xy=(arrow_x2, arrow_y), xytext=(arrow_x1, arrow_y),
                        arrowprops=dict(arrowstyle="-|>", color=c_navy, lw=2.5, mutation_scale=15))

    # Bottom Tech Stack Banner
    b_rect = patches.FancyBboxPatch((0.6, 0.45), 14.8, 0.65, boxstyle="round,pad=0.08", fc=c_purple_light, ec=c_purple, lw=1.2)
    ax.add_patch(b_rect)
    ax.text(8.0, 0.88, "CORE TECH STACK: Python 3.11 • FastAPI • NumPy • GeoPandas • Shapely • Leaflet.js • Chart.js • Open-Meteo • NASA POWER • Docker",
            ha="center", va="center", fontsize=9, fontweight="bold", color=c_purple)
    ax.text(8.0, 0.62, "Validated via WMO UTCI Polynomial, ISO 7243:2017 WBGT, NIOSH Criteria (Pub 2016-106), and Census 2011 Primary Census Abstract",
            ha="center", va="center", fontsize=8, color=c_text_muted)

    plt.tight_layout()
    out_file = "/home/ubuntu/sih26083-heat-risk/docs/sih/thermoshield_architecture_flowchart.png"
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close()
    print("Master architecture flowchart generated:", out_file)

if __name__ == "__main__":
    generate_clean_architecture_flowchart()
