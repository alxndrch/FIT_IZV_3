#!/usr/bin/python3.8
# coding=utf-8

import pandas as pd
# import fiona  # vyzaduje macos
import geopandas
import matplotlib.pyplot as plt
import contextily as ctx
import sklearn.cluster
import numpy as np


def make_geo(df: pd.DataFrame) -> geopandas.GeoDataFrame:
    """ Konvertovani dataframe do
        geopandas.GeoDataFrame se spravnym kodovani
    """

    # souradnice x = sloupec d
    # souradnice y = sloupec e
    gdf = geopandas.GeoDataFrame(df,
                                 geometry=geopandas.points_from_xy(x=df["d"],
                                                                   y=df["e"]),
                                 crs="EPSG:5514")

    # odstraneni zaznamu s neznamou pozici
    gdf = gdf.dropna(subset=["d", "e"])

    return gdf


def plot_geo(gdf: geopandas.GeoDataFrame, fig_location: str = None,
             show_figure: bool = False):
    """ Vykresleni grafu s dvemi podgrafy podle lokality nehody """

    paper_a4 = (15.69, 8.27)  # rozmery formatu A4

    # p5a.1 = v obci
    # p5a.2 = mimo obec
    gdf = gdf.loc[gdf["region"].isin(["ZLK"]), ["p5a", "geometry"]]

    # ----- Vytvareni grafu -----

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=paper_a4,
                             constrained_layout=True)

    # nadipisy
    fig.suptitle("Nehody ve Zlínském kraji", fontsize=14)
    fig.canvas.set_window_title("Nehody v Zlínském kraji")

    (ax1, ax2) = axes

    # nadpisy grafu
    titles = ["Nehody v obci", "Nehody mimo obec"]

    # nehody v obci
    gdf[gdf["p5a"] == 1].plot(ax=ax1, color="red", markersize=2,
                              label=titles[0], alpha=0.5)
    # nehody mimo obec
    gdf[gdf["p5a"] == 2].plot(ax=ax2, color="green", markersize=1,
                              label=titles[1], alpha=0.5)

    # nastaveni grafu
    for ax, title in zip(axes, titles):
        ax.set_title(title)
        ax.tick_params(labelbottom=False, labelleft=False)
        ax.tick_params(axis=u'both', which=u'both', length=0)
        ctx.add_basemap(ax, crs=gdf.crs.to_string(),
                        source=ctx.providers.Stamen.TonerLite)

    # ----- Vystup -----

    # ulozeni grafu
    if fig_location is not None:
        plt.savefig(fig_location, dpi=500)

    # zobrazeni grafu
    if show_figure:
        plt.show()


def plot_cluster(gdf: geopandas.GeoDataFrame, fig_location: str = None,
                 show_figure: bool = False):
    """ Vykresleni grafu s lokalitou vsech nehod
        v kraji shlukovanych do clusteru
    """
    paper_a4 = (11.69, 8.27)  # rozmery formatu A4

    gdf = gdf.loc[gdf["region"].isin(["ZLK"]), ["p5a", "geometry"]]
    gdfc = gdf.copy()
    # vytvoreni trenovaci matice
    coords = np.dstack([gdfc.geometry.x, gdfc.geometry.y]).reshape([-1, 2])

    # KMeans
    model = sklearn.cluster.KMeans(n_clusters=13).fit(coords)
    gdfc["cluster"] = model.labels_

    gdfc = gdfc.dissolve(by="cluster", aggfunc={"p5a": "count"})
    gdfc = gdfc.rename(columns={"p5a": "count"})

    gdfc_coords = geopandas.GeoDataFrame(
        geometry=geopandas.points_from_xy(model.cluster_centers_[:, 0],
                                          model.cluster_centers_[:, 1]))

    gdfc = gdfc.merge(gdfc_coords, left_on="cluster", right_index=True)
    gdfc = gdfc.set_geometry("geometry_y")

    # ----- Vytvareni grafu -----

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=paper_a4,
                           constrained_layout=True)

    # nadipisy
    fig.suptitle("Nehody ve Zlínském kraji", fontsize=14)
    fig.canvas.set_window_title("Nehody v Zlínském kraji")

    # zhluky nehod
    gdfc.plot(ax=ax, markersize=gdfc["count"]*2, column="count",
              legend=True, alpha=0.5)

    # vsechny nehody
    gdf.plot(ax=ax, color="gray", markersize=1, alpha=0.5)

    # nastaveni grafu
    ax.tick_params(labelbottom=False, labelleft=False)
    ax.tick_params(axis=u'both', which=u'both', length=0)
    ctx.add_basemap(ax, crs="EPSG:5514", source=ctx.providers.Stamen.TonerLite)

    # ----- Vystup -----

    # ulozeni grafu
    if fig_location is not None:
        plt.savefig(fig_location, dpi=500)

    # zobrazeni grafu
    if show_figure:
        plt.show()


if __name__ == "__main__":
    gdf = make_geo(pd.read_pickle("accidents.pkl.gz"))
    plot_geo(gdf, "geo1.png",)
    plot_cluster(gdf, "geo2.png")
