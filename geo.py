#!/usr/bin/python3.8
# coding=utf-8

# TODO: osetrit vstup dataframe

import pandas as pd
import fiona
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
    gdf = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(
                                                x=df["d"], y=df["e"]),
                                                crs="EPSG:5514")

    # odstraneni zaznamu s neznamou pozici
    gdf = gdf.dropna(subset=["d", "e"])

    return gdf

def plot_geo(gdf: geopandas.GeoDataFrame, fig_location: str = None,
             show_figure: bool = False):
    """ Vykresleni grafu s dvemi podgrafy podle lokality nehody """

    paper_a4 = (8.27, 11.69)  # rozmery formatu A4

    # p5a.1 = v obci
    # p5a.2 = mimo obec
    gdf = gdf.loc[gdf["region"].isin(["JHM"]), ["p5a", "geometry"]]

    # ----- Vytvareni grafu -----

    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=paper_a4,
                             constrained_layout=True)

    # nadipisy
    fig.suptitle("Nehody v Jihomoravském kraji", fontsize=14)
    fig.canvas.set_window_title("Nehody v Jihomoravském kraji")

    ax1, ax2 = axes

    # nadpisy grafu
    titles = ["Nehody v obci v Jihomoravském kraji",
              "Nehody mimo obec v Jihomoravském kraji"]

    gdf[gdf["p5a"] == 1].plot(ax=ax1, markersize=2, label=titles[0])
    gdf[gdf["p5a"] == 2].plot(ax=ax2, markersize=1, label=titles[1])

    # nastaveni grafu
    for ax, title in zip(axes, titles):
        ax.set_title(title)
        ax.tick_params(labelbottom=False, labelleft=False)
        ax.tick_params(axis=u'both', which=u'both',length=0)
        ctx.add_basemap(ax, crs=gdf.crs.to_string(), source=ctx.providers.Stamen.TonerLite)

    # ----- Vystup -----

    # ulozeni grafu
    if fig_location is not None:
        plt.savefig(fig_location)

    # zobrazeni grafu
    if show_figure:
        plt.show()



def plot_cluster(gdf: geopandas.GeoDataFrame, fig_location: str = None,
                 show_figure: bool = False):
    """ Vykresleni grafu s lokalitou vsech nehod
        v kraji shlukovanych do clusteru
    """


if __name__ == "__main__":
    gdf = make_geo(pd.read_pickle("accidents.pkl.gz"))
    plot_geo(gdf, "geo1.png")
    #plot_cluster(gdf, "geo2.png", True)
