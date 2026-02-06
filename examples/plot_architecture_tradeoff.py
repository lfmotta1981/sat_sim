import csv
import matplotlib.pyplot as plt


def main():
    totals = []
    max_gaps = []
    revisits = []

    with open("architecture_tradeoff.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            totals.append(int(row["total_sats"]))
            max_gaps.append(float(row["max_gap_h"]))
            revisits.append(float(row["mean_revisit_h"]))

    # -------------------------------
    # Figura única com dois subplots
    # -------------------------------
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

    # Plot 1: Max Gap
    ax1.plot(totals, max_gaps, marker="o")
    ax1.set_ylabel("Gap máximo [min]")
    ax1.set_title("Trade-off de cobertura (SSO, Svalbard)")
    ax1.grid(True)

    # Plot 2: Revisit
    ax2.plot(totals, revisits, marker="o")
    ax2.set_xlabel("Total de satélites")
    ax2.set_ylabel("Revisit médio [min]")
    ax2.grid(True)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
