import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

os.makedirs("/home/ubuntu/sih26083-heat-risk/docs/sih", exist_ok=True)

def generate_vertical_flowchart():
    # Vertical aspect ratio (approx 6:8 or 3:4), perfect for the right half of a 16:9 slide
    fig, ax = plt.subplots(figsize=(6.5, 8.5), dpi=300)
    ax.set_xlim(0, 6.5)
    ax.set_ylim(0, 8.5)
    ax.axis("off")

    # Colors
    c_bg = "#FFFFFF"
    c_canvas_bg = "#F8FAFC"
    c_navy = "#0F2C59"
    c_blue = "#0284C7"
    c_blue_bg = "#F0F9FF"
    c_green = "#16A34A"
    c_green_bg = "#F0FDF4"
    c_red = "#DC2626"
    c_red_bg = "#FEF2F2"
    c_orange = "#EA580C"
    c_orange_bg = "#FEF3C7"
    c_text_dark = "#1E293B"

    # Background canvas
    canvas = patches.FancyBboxPatch((0.1, 0.1), 6.3, 8.3, boxstyle="round,pad=0.1", fc=c_canvas_bg, ec="#CBD5E1", lw=1.5)
    ax.add_patch(canvas)

    # Title Header Badge
    hdr = patches.FancyBboxPatch((0.3, 7.7), 5.9, 0.55, boxstyle="round,pad=0.08", fc=c_navy, ec="none")
    ax.add_patch(hdr)
    ax.text(3.25, 7.97, "THERMOSHIELD PIPELINE", ha="center", va="center", fontsize=11, fontweight="bold", color="#FFFFFF")

    # 4 Vertical Stage Cards
    stages = [
        ("1. DATA INGESTION LAYER", c_blue, c_blue_bg, 5.9, [
            "• Open-Meteo 0.1° NWP (5-Day Hourly Weather)",
            "• NASA POWER 40-Yr Climatological Baseline",
            "• Census 2011 PCA Demographics & Ward Maps",
            "• Satellite LST & NDVI Canopy Deficit"
        ]),
        ("2. THERMAL STRESS ENGINE", c_green, c_green_bg, 4.15, [
            "• UTCI 6th-Order Poly (Fiala 187-Node Body)",
            "• ISO 7243 WBGT Psychrometrics (Tw + Tg)",
            "• Multi-Day Persistence Multiplier (Dmult)",
            "• Nocturnal Recovery Deficit (Tmin > 28°C)"
        ]),
        ("3. AI RISK & HVI SYNTHESIS", c_red, c_red_bg, 2.4, [
            "• Heat Vulnerability Index (Slums, Elderly, Labor)",
            "• Epidemiological Curve (Azhar 2014 / PNAS)",
            "• Composite 0–100 Human Heat-Health Score",
            "• Hyper-Local Ward Risk Stratification"
        ]),
        ("4. ACTION & DISPATCH LAYER", c_orange, c_orange_bg, 0.65, [
            "• Interactive Leaflet GIS Ward Choropleth",
            "• 72h Early Hospital Surge Bed Alerts",
            "• Mandatory NIOSH Labor Halts (11 AM–4 PM)",
            "• Bilingual Hindi/English SMS & Telegram Alerts"
        ])
    ]

    card_w = 5.9
    card_h = 1.35
    card_x = 0.3

    for idx, (s_title, s_col, s_bg, card_y, bullets) in enumerate(stages):
        # Card outer container
        card = patches.FancyBboxPatch((card_x, card_y), card_w, card_h, boxstyle="round,pad=0.08", fc=c_bg, ec=s_col, lw=1.6)
        ax.add_patch(card)

        # Stage Header Ribbon
        rib = patches.FancyBboxPatch((card_x + 0.05, card_y + card_h - 0.32), card_w - 0.1, 0.28, boxstyle="round,pad=0.04", fc=s_bg, ec=s_col, lw=1)
        ax.add_patch(rib)
        ax.text(card_x + card_w / 2, card_y + card_h - 0.18, s_title, ha="center", va="center", fontsize=9, fontweight="bold", color=s_col)

        # Bullet text
        b_y_start = card_y + card_h - 0.48
        for b_idx, bullet in enumerate(bullets):
            by = b_y_start - b_idx * 0.22
            ax.text(card_x + 0.2, by, bullet, ha="left", va="center", fontsize=7.2, color=c_text_dark, fontweight="medium")

        # Downward Arrow to next stage
        if idx < 3:
            arrow_x = card_x + card_w / 2
            arrow_y1 = card_y - 0.02
            arrow_y2 = card_y - 0.38
            ax.annotate("", xy=(arrow_x, arrow_y2), xytext=(arrow_x, arrow_y1),
                        arrowprops=dict(arrowstyle="-|>", color=c_navy, lw=2.2, mutation_scale=12))

    plt.tight_layout()
    out_file = "/home/ubuntu/sih26083-heat-risk/docs/sih/thermoshield_flowchart_vertical.png"
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close()
    print("Vertical flowchart successfully generated:", out_file)

if __name__ == "__main__":
    generate_vertical_flowchart()
