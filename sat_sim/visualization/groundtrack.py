import matplotlib.pyplot as plt
import cartopy.crs as ccrs

def plot_groundtrack(latitudes, longitudes, title="Ground Track"):
    fig = plt.figure(figsize=(12, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())

    ax.coastlines()
    ax.gridlines(draw_labels=True)

    ax.plot(
        longitudes,
        latitudes,
        '.',
        markersize=2,
        transform=ccrs.PlateCarree()
    )

    ax.set_title(title)
    plt.show()
