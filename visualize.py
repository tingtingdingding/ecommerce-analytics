import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

DATA_DIR = r"/Users/xiaoting/Desktop/EDHEC/职业规划/BA project/archive"
OUT_DIR  = os.path.join(DATA_DIR, "charts")
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams.update({
    "figure.facecolor":  "#FAFAFA",
    "axes.facecolor":    "#FAFAFA",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.spines.left":  False,
    "axes.spines.bottom":False,
    "axes.grid":         True,
    "grid.color":        "#E5E5E5",
    "grid.linewidth":    0.8,
    "font.family":       "DejaVu Sans",
    "font.size":         11,
    "axes.titlesize":    14,
    "axes.titleweight":  "bold",
    "axes.titlepad":     14,
    "axes.labelsize":    11,
    "xtick.bottom":      False,
    "ytick.left":        False,
})

PURPLE = "#7F77DD"
TEAL   = "#1D9E75"
CORAL  = "#D85A30"
AMBER  = "#BA7517"
GRAY   = "#888780"
LIGHT  = "#E5E3F8"


# ══════════════════════════════════════════════════════════════
# Plot 1:Seller Tier — Seller Count vs Revenue Share
# ══════════════════════════════════════════════════════════════
df1 = pd.read_csv(os.path.join(DATA_DIR, "module1_seller_tiers_summary.csv"))
tiers        = ["Tier 1\nStar", "Tier 2\nGrowth", "Tier 3\nAverage", "Tier 4\nAt Risk"]
counts       = df1["seller_count"].tolist()
rev_pct      = df1["revenue_share_pct"].tolist()
colors_bar   = [PURPLE, TEAL, AMBER, CORAL]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("Module 1 · Seller Segmentation", fontsize=15, fontweight="bold", y=1.01)

# Left: Seller Count
bars = ax1.bar(tiers, counts, color=colors_bar, width=0.55, zorder=3)
ax1.set_title("Seller Count by Tier")
ax1.set_ylabel("Number of sellers")
for bar, val in zip(bars, counts):
    ax1.text(bar.get_x() + bar.get_width()/2,
             bar.get_height() + 10,
             f"{val:,}", ha="center", va="bottom", fontsize=10)

# Right: Revenue Share
bars2 = ax2.bar(tiers, rev_pct, color=colors_bar, width=0.55, zorder=3)
ax2.set_title("Revenue Share by Tier (%)")
ax2.set_ylabel("Revenue share (%)")
for bar, val in zip(bars2, rev_pct):
    ax2.text(bar.get_x() + bar.get_width()/2,
             bar.get_height() + 0.4,
             f"{val}%", ha="center", va="bottom", fontsize=10)

# Annotation: Key Insight
fig.text(0.5, -0.04,
         "Key insight: Top 21% of sellers (Tier 1) drive 61% of platform revenue — "
         "a classic power-law distribution.",
         ha="center", fontsize=10, color="#555555", style="italic")

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "module1_seller_tiers.png"),
            dpi=150, bbox_inches="tight")
plt.close()
print("✅ Plot 1 saved")


# ══════════════════════════════════════════════════════════════
# Plot 2: Cohort Retention Curve
# ══════════════════════════════════════════════════════════════
df2 = pd.read_csv(os.path.join(DATA_DIR, "module2_cohort_summary.csv"))
df2 = df2[df2["month_offset"] > 0]   # Remove month 0 (100% baseline)

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df2["month_offset"], df2["avg_retention_rate"],
        color=PURPLE, linewidth=2.5, marker="o", markersize=6, zorder=3)

# Fill the area below the curve
ax.fill_between(df2["month_offset"], df2["avg_retention_rate"],
                alpha=0.12, color=PURPLE)

# Label the key number for month 1
m1_val = df2[df2["month_offset"] == 1]["avg_retention_rate"].values[0]
ax.annotate(f"Month 1: {m1_val}%",
            xy=(1, m1_val),
            xytext=(2.2, m1_val + 0.08),
            fontsize=10, color=CORAL,
            arrowprops=dict(arrowstyle="->", color=CORAL, lw=1.2))

ax.set_title("Module 2 · Average Cohort Retention Rate (Month 1–12)")
ax.set_xlabel("Months since first purchase")
ax.set_ylabel("Avg retention rate (%)")
ax.set_xticks(df2["month_offset"])
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f%%"))

fig.text(0.5, -0.04,
         "Key insight: 99.5% of customers never return after first purchase. "
         "First-order experience is the single highest-leverage retention lever.",
         ha="center", fontsize=10, color="#555555", style="italic")

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "module2_cohort_retention.png"),
            dpi=150, bbox_inches="tight")
plt.close()
print("✅ Plot 2 saved")


# ══════════════════════════════════════════════════════════════
# Plot 3: Order Conversion Funnel
# ══════════════════════════════════════════════════════════════
df3 = pd.read_csv(os.path.join(DATA_DIR, "module3_funnel.csv"))

stages = ["Orders\nPlaced", "Approved", "Shipped", "Delivered"]
values = [
    int(df3["total_orders"].iloc[0]),
    int(df3["approved"].iloc[0]),
    int(df3["shipped"].iloc[0]),
    int(df3["delivered"].iloc[0]),
]
total  = values[0]
widths = [v / total for v in values]
colors_funnel = [PURPLE, TEAL, TEAL, TEAL]

fig, ax = plt.subplots(figsize=(10, 5))

bar_height = 0.5
y_positions = [3, 2, 1, 0]

for i, (stage, val, w, col) in enumerate(zip(stages, values, widths, colors_funnel)):
    left = (1 - w) / 2
    ax.barh(y_positions[i], w, left=left, height=bar_height,
            color=col, alpha=0.85 if i > 0 else 1.0, zorder=3)
    # Value labels
    ax.text(0.5, y_positions[i],
            f"{val:,}  ({val/total*100:.1f}%)",
            ha="center", va="center",
            fontsize=11, fontweight="bold", color="white", zorder=4)
    # Stage names
    ax.text(0.02, y_positions[i], stage,
            ha="left", va="center", fontsize=10, color="#333333")

# Delivery metrics annotation box
ax.text(0.85, 1.5,
        f"Avg delivery: {df3['avg_delivery_days'].iloc[0]} days\n"
        f"Late delivery: {df3['late_delivery_pct'].iloc[0]}%",
        ha="center", va="center", fontsize=10,
        bbox=dict(boxstyle="round,pad=0.5", facecolor=LIGHT,
                  edgecolor=PURPLE, linewidth=1))

ax.set_title("Module 3 · Order Conversion Funnel")
ax.set_xlim(0, 1)
ax.set_ylim(-0.5, 3.8)
ax.axis("off")

fig.text(0.5, -0.02,
         "Key insight: Funnel completion rate is 97%. However, 7.9% late delivery rate "
         "risks permanent customer loss given near-zero repeat purchase behavior.",
         ha="center", fontsize=10, color="#555555", style="italic")

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "module3_funnel.png"),
            dpi=150, bbox_inches="tight")
plt.close()
print("✅ Plot 3 saved")


# ══════════════════════════════════════════════════════════════
# Plot 4: Revenue Attribution — New vs Returning Customers
# ══════════════════════════════════════════════════════════════
df4 = pd.read_csv(os.path.join(DATA_DIR, "module4_revenue.csv"))
df4["order_month"] = pd.to_datetime(df4["order_month"])
df4 = df4.sort_values("order_month")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
fig.suptitle("Module 4 · Revenue Attribution: New vs Returning Customers",
             fontsize=15, fontweight="bold")

# 上图：堆叠面积图
ax1.stackplot(df4["order_month"],
              df4["new_customer_revenue"],
              df4["returning_customer_revenue"],
              labels=["New customer revenue", "Returning customer revenue"],
              colors=[PURPLE, TEAL], alpha=0.85)
ax1.set_title("Monthly Revenue Decomposition")
ax1.set_ylabel("Revenue (BRL)")
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.0f}K"))
ax1.legend(loc="upper left", frameon=False, fontsize=10)

# Black Friday标注
bf_month = pd.Timestamp("2017-11-01")
bf_rev   = df4[df4["order_month"] == bf_month]["total_revenue"].values
if len(bf_rev):
    ax1.annotate("Black Friday\npeak",
                 xy=(bf_month, bf_rev[0]),
                 xytext=(pd.Timestamp("2017-08-01"), bf_rev[0] * 1.05),
                 fontsize=9, color=CORAL,
                 arrowprops=dict(arrowstyle="->", color=CORAL, lw=1.2))

# 下图：回头客占比趋势
df4["returning_pct"] = (df4["returning_customer_revenue"] /
                         df4["total_revenue"] * 100).round(2)
ax2.bar(df4["order_month"], df4["returning_pct"],
        color=TEAL, alpha=0.75, width=20, zorder=3)
ax2.set_title("Returning Customer Revenue Share (%)")
ax2.set_ylabel("Share (%)")
ax2.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f%%"))
ax2.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%Y-%m"))
plt.xticks(rotation=45, ha="right")

fig.text(0.5, -0.01,
         "Key insight: New customers drive 97–99% of monthly revenue throughout. "
         "Returning customer share grows from 0.02% to 2.3% — but remains negligible.",
         ha="center", fontsize=10, color="#555555", style="italic")

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "module4_revenue_attribution.png"),
            dpi=150, bbox_inches="tight")
plt.close()
print("✅ Plot 4 saved")

print(f"\n🎉 All charts saved to: {OUT_DIR}")