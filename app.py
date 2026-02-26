import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.ticker import MaxNLocator

from sat_sim.analysis.sweep_local_geom import run_sweep_local_geom_analysis
from sat_sim.coverage.grid import compute_grid_coverage
from sat_sim.coverage.grid_gap import compute_grid_max_gap
from sat_sim.orbits.constellation import generate_constellation
from sat_sim.orbits.elements import coe_to_rv
from sat_sim.orbits.propagator import propagate_orbit
from sat_sim.constants import R_EARTH, DEG2RAD
from sat_sim.time import TimeArray
from sat_sim.ground.stations import GroundStation
from sat_sim.frames.transforms import eci_to_ecef

st.set_page_config(layout="wide")
st.title("Constellation Explorer")
st.markdown("Orbit Analysis")

# =============================
# Sidebar
# =============================

st.sidebar.header("Mission Parameters")

altitude_km = st.sidebar.number_input("Altitude [km]", 300.0, 2000.0, 550.0)
inclination_deg = st.sidebar.number_input("Inclination [deg]", 0.0, 180.0, 98.0)
duration_h = st.sidebar.number_input("Simulation Duration [h]", 1.0, 72.0, 24.0)
dt_s = st.sidebar.number_input("Time Step [s]", 10.0, 300.0, 60.0)
min_elev_deg = st.sidebar.number_input("Min Elevation [deg]", 0.0, 45.0, 0.0)

st.sidebar.header("Ground Location")

lat = st.sidebar.number_input("Latitude [deg]", -90.0, 90.0, 57.02868)
lon = st.sidebar.number_input("Longitude [deg]", -180.0, 180.0, 9.94350)

st.sidebar.header("Architecture Sweep")
n_max = st.sidebar.number_input("Max Total Satellites", 1, 30, 8)

run_button = st.sidebar.button("Run Analysis")

# =============================
# Run Analysis + Persist
# =============================

if run_button:
    with st.spinner("Running analysis..."):
        st.session_state["results"] = run_sweep_local_geom_analysis(
            station_lat_deg=lat,
            station_lon_deg=lon,
            altitude_km=altitude_km,
            inclination_deg=inclination_deg,
            duration_h=duration_h,
            dt_s=dt_s,
            min_elev_deg=min_elev_deg,
            n_max=n_max,
        )
        st.session_state.pop("show_maps", None)
        st.session_state.pop("selected_arch", None)

if "results" not in st.session_state:
    st.info("Configure parameters and click 'Run Analysis'.")
    st.stop()

results = st.session_state["results"]

if not results:
    st.warning("No architectures evaluated.")
    st.stop()

df = pd.DataFrame(results).sort_values("worst_gap_min").reset_index(drop=True)
df.insert(0, "rank", df.index + 1)

# =============================
# Ranking Table
# =============================

st.subheader("Architecture Ranking")

df_display = df.copy()
df_display["Select"] = False

edited_df = st.data_editor(
    df_display,
    hide_index=True,
    use_container_width=True,
    column_config={"Select": st.column_config.CheckboxColumn(required=False)},
    key="architecture_table"
)

selected_rows = edited_df[edited_df["Select"] == True]
selected_row = selected_rows.iloc[0] if len(selected_rows) == 1 else None

# =============================
# Trade Space Plots (Always)
# =============================

col1, col2 = st.columns(2)

with col1:
    fig1, ax1 = plt.subplots()
    ax1.plot(df["total_sats"], df["worst_gap_min"], marker="o")

    if selected_row is not None:
        ax1.scatter(
            selected_row["total_sats"],
            selected_row["worst_gap_min"],
            color="red",
            s=120,
            zorder=5
        )

    ax1.set_xlabel("Total Satellites")
    ax1.set_ylabel("Max Gap [min]")
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.xaxis.set_major_locator(MaxNLocator(integer=True))
    st.pyplot(fig1)

with col2:
    fig2, ax2 = plt.subplots()
    ax2.plot(df["total_sats"], df["availability_percent"], marker="o")

    if selected_row is not None:
        ax2.scatter(
            selected_row["total_sats"],
            selected_row["availability_percent"],
            color="red",
            s=120,
            zorder=5
        )

    ax2.set_xlabel("Total Satellites")
    ax2.set_ylabel("Availability [%]")
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.xaxis.set_major_locator(MaxNLocator(integer=True))
    st.pyplot(fig2)

st.divider()

# =============================
# Button to Generate Coverage
# =============================

if selected_row is not None:
    if st.button("Show Coverage"):
        st.session_state["show_maps"] = True
        st.session_state["selected_arch"] = selected_row.to_dict()

if "show_maps" not in st.session_state:
    st.info("Select an architecture and click 'Show Coverage'.")
    st.stop()

selected_row = pd.Series(st.session_state["selected_arch"])

# =============================
# Compute Coverage
# =============================

station = GroundStation(lat_deg=lat, lon_deg=lon)
timeline = TimeArray(0.0, duration_h * 3600.0, dt_s)

constellation_coe = generate_constellation(
    altitude=R_EARTH + altitude_km * 1000.0,
    inclination=inclination_deg * DEG2RAD,
    n_planes=int(selected_row["n_planes"]),
    sats_per_plane=int(selected_row["sats_per_plane"]),
)

constellation = [coe_to_rv(coe) for coe in constellation_coe]

lat_grid = np.arange(-90, 91, 20)
lon_grid = np.arange(-180, 181, 20)

coverage = compute_grid_coverage(
    constellation=constellation,
    timeline=timeline,
    propagate_fn=lambda r0, v0, tl: propagate_orbit(r0, v0, tl, use_j2=True),
    min_elevation_rad=min_elev_deg * DEG2RAD,
    lat_grid_deg=lat_grid,
    lon_grid_deg=lon_grid,
)

coverage_min = coverage * (duration_h * 60.0)

max_gap = compute_grid_max_gap(
    constellation=constellation,
    timeline=timeline,
    propagate_fn=lambda r0, v0, tl: propagate_orbit(r0, v0, tl, use_j2=True),
    min_elevation_rad=min_elev_deg * DEG2RAD,
    lat_grid_deg=lat_grid,
    lon_grid_deg=lon_grid,
)

max_gap_min = max_gap / 60.0

# =============================
# Maps
# =============================

st.subheader("Coverage Maps")

col3, col4 = st.columns(2)

with col3:
    fig3 = plt.figure(figsize=(6,4))
    ax3 = plt.axes(projection=ccrs.PlateCarree())
    ax3.set_global()
    ax3.add_feature(cfeature.LAND, facecolor="lightgray")
    ax3.add_feature(cfeature.OCEAN, facecolor="white")
    ax3.add_feature(cfeature.COASTLINE, linewidth=0.6)

    im = ax3.imshow(
        coverage_min,
        extent=[-180,180,-90,90],
        origin="lower",
        transform=ccrs.PlateCarree(),
        cmap="RdYlGn",
        alpha=0.85,
    )

    ax3.scatter(lon, lat, color="blue", marker="x", s=80, transform=ccrs.PlateCarree())
    plt.colorbar(im, ax=ax3, label="Coverage [min]")
    ax3.set_title("Coverage")

    st.pyplot(fig3)

with col4:
    fig4 = plt.figure(figsize=(6,4))
    ax4 = plt.axes(projection=ccrs.PlateCarree())
    ax4.set_global()
    ax4.add_feature(cfeature.LAND, facecolor="lightgray")
    ax4.add_feature(cfeature.OCEAN, facecolor="white")
    ax4.add_feature(cfeature.COASTLINE, linewidth=0.6)

    im2 = ax4.imshow(
        max_gap_min,
        extent=[-180,180,-90,90],
        origin="lower",
        transform=ccrs.PlateCarree(),
        cmap="RdYlGn_r",
        alpha=0.85,
    )

    ax4.scatter(lon, lat, color="blue", marker="x", s=80, transform=ccrs.PlateCarree())
    plt.colorbar(im2, ax=ax4, label="Max Gap [min]")
    ax4.set_title("Max Gap")

    st.pyplot(fig4)

# =============================
# Snapshot
# =============================

st.divider()
st.subheader("Constellation Geometry (t0)")


fig5 = plt.figure(figsize=(8, 5))
ax5 = plt.axes(projection=ccrs.PlateCarree())
ax5.set_global()

ax5.add_feature(cfeature.LAND, facecolor="lightgray")
ax5.add_feature(cfeature.OCEAN, facecolor="white")
ax5.add_feature(cfeature.COASTLINE, linewidth=0.6)

n_planes = int(selected_row["n_planes"])
sats_per_plane = int(selected_row["sats_per_plane"])

# Uma cor por plano
plane_colors = plt.cm.tab10(np.linspace(0, 1, n_planes))

for p in range(n_planes):

    plane_color = plane_colors[p]

    for s in range(sats_per_plane):

        idx = p * sats_per_plane + s
        r0, v0 = constellation[idx]

        # Gerar órbita (~1 revolução)
        orbit_timeline = TimeArray(0.0, 5400.0, 60.0)
        rs_orbit, _ = propagate_orbit(r0, v0, orbit_timeline)

        lats = []
        lons = []

        for k, r_eci in enumerate(rs_orbit):
            t = orbit_timeline.times[k]
            r_ecef = eci_to_ecef(r_eci, t)

            x, y, z = r_ecef
            r_norm = np.sqrt(x**2 + y**2 + z**2)

            lat_sat = np.degrees(np.arcsin(z / r_norm))
            lon_sat = np.degrees(np.arctan2(y, x))

            lats.append(lat_sat)
            lons.append(lon_sat)

        # Linha da órbita (cor do plano)
        ax5.plot(
            lons,
            lats,
            linestyle="--",
            linewidth=1.5,
            color=plane_color,
            transform=ccrs.PlateCarree()
        )

        # Posição atual (t0)
        r_ecef_now = eci_to_ecef(r0, 0.0)

        x, y, z = r_ecef_now
        r_norm = np.sqrt(x**2 + y**2 + z**2)

        lat_now = np.degrees(np.arcsin(z / r_norm))
        lon_now = np.degrees(np.arctan2(y, x))

        ax5.scatter(
            lon_now,
            lat_now,
            color=plane_color,
            s=70,
            edgecolors="black",
            linewidth=0.5,
            transform=ccrs.PlateCarree()
        )

# Estação terrestre
ax5.scatter(
    lon,
    lat,
    color="blue",
    marker="x",
    s=120,
    linewidth=2,
    transform=ccrs.PlateCarree()
)

ax5.set_title("Orbital Planes and Satellite Positions")

st.pyplot(fig5)
