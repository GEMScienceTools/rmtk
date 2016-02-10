from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
import os
import rmtk.plotting.common.parse_damage_maps as parsedm
import rmtk.plotting.common.parse_exposure as parsee


def build_map(plotting_type, nrml_damage_map, damage_state, exposure_model, bounding_box=False, log_scale=True, marker_size=12, export_map_to_csv=False):
    '''
    build_map(plotting_type, damage_map, damage_state, bounding_box, log_scale, exposure_model, marker_size, export_map_to_csv):

    build map for spatial distribution of building damage

    plotting_type:
        0 - Aggregated damage map only,
        1 - damage maps per taxonomy only,
        2 - Both aggregated and taxonomy-based
    '''

    #exposure_path = exposure_model

    agg_damages = True
    if plotting_type == 1:
        agg_damages = False

    data = parsedm.parse_damage_maps(nrml_damage_map, agg_damages, export_map_to_csv)
    box = define_bounding_box(bounding_box, data[0])

    if plotting_type == 0 or plotting_type == 2:  # aggregated
        locations = data[1].loc[:, ['lon', 'lat']].values
        damages = data[1].loc[:, damage_state].values
        plot_single_map(locations, damages, box, log_scale, marker_size,
                        'Aggregated damages per location: ' + damage_state, 1)

    if plotting_type == 1 or plotting_type == 2:
        individualdamages = data[0].copy()
        idTaxonomies = np.array(parsee.extractIDTaxonomies(exposure_model, False))
        dict_idTaxonomies = {assetID: taxonomy for assetID, taxonomy in idTaxonomies}

        individualdamages['asset'].replace(dict_idTaxonomies, inplace=True)

        uniqueTaxonomies = []
        damagesTaxonomies = []
        for i, (taxonomy, sub_group) in enumerate(individualdamages.groupby('asset')):
            df_agg_damage = parsedm.agg_damage_map(sub_group)
            locations = df_agg_damage.loc[:, ['lon', 'lat']].values
            damages = df_agg_damage.loc[:, damage_state].values

            if locations.shape[0] > 0:
                plot_single_map(locations, damages, box, log_scale,
                                marker_size, damage_state + ' damage map for ' + taxonomy, i + 2)
            uniqueTaxonomies.append(taxonomy)
            damagesTaxonomies.append(damages.sum())

    plot_pie_chart_losses(uniqueTaxonomies, damagesTaxonomies, damage_state, i + 1)


def plot_pie_chart_losses(uniqueTaxonomies, lossesTaxonomies, damage_state, figNo):

    labels = uniqueTaxonomies
    sizes = lossesTaxonomies
    #colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral']

    plt.figure(figNo, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
    plt.title('Total assets in {} damage per taxonomy'.format(damage_state))
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.axis('equal')
    plt.show()


def define_bounding_box(bounding_box, data):

    locations = data.loc[:, ['lon', 'lat']].values

    box = {"lon_0": None, "lat_0": None, "lon_1": None,
           "lat_1": None, "lon_2": None, "lat_2": None}

    if bounding_box == 0:
        maxCoordinates = locations.max(axis=0)
        minCoordinates = locations.min(axis=0)
    else:
        maxCoordinates = [bounding_box[2], bounding_box[3]]
        minCoordinates = [bounding_box[0], bounding_box[1]]

    lengthLon = abs(maxCoordinates[0]-minCoordinates[0])
    lengthLat = abs(maxCoordinates[1]-minCoordinates[1])

    box["lon_0"] = (minCoordinates[0]+maxCoordinates[0])/2
    box["lat_0"] = (minCoordinates[1]+maxCoordinates[1])/2
    box["lon_1"] = minCoordinates[0]-0.1*lengthLon
    box["lat_1"] = minCoordinates[1]-0.1*lengthLat
    box["lon_2"] = maxCoordinates[0]+0.1*lengthLon
    box["lat_2"] = maxCoordinates[1]+0.1*lengthLat
    box["lon_length"] = lengthLon
    box["lat_length"] = lengthLat
    return box


def plot_single_map(locations, losses, box, log_scale, marker_size, title, figNo):

    plt.figure(figNo, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
    map = Basemap(llcrnrlon=box["lon_1"], llcrnrlat=box["lat_1"],
                  urcrnrlon=box["lon_2"], urcrnrlat=box["lat_2"], projection='mill', resolution='i')

    x, y = map(locations[:, [0]], locations[:, [1]])
    #map.shadedrelief()
    map.drawcoastlines(linewidth=0.25)
    map.drawcountries(linewidth=0.25)
    map.drawstates(linewidth=0.25)
    map.drawmapboundary(fill_color='aqua')
    map.fillcontinents(color='white', lake_color='aqua')

    scale = None
    if log_scale:
        scale = LogNorm()

    plt.scatter(x, y, s=marker_size, c=losses, zorder=4, cmap='YlOrRd', edgecolor='None', norm=scale)
    if locations.shape[0] > 1:
        cbar = map.colorbar(location='right', pad="5%")
        cbar.set_label('Number of damages')

    if box["lat_length"] < 2:
        parallels = np.arange(0., 81, 0.25)
    else:
        parallels = np.arange(0., 81, 1.0)
    # labels = [left,right,top,bottom]
    map.drawparallels(parallels, labels=[True, False, True, False])
    if box["lon_length"] < 2:
        meridians = np.arange(0., 360, 0.25)
    else:
        meridians = np.arange(0., 360, 1.0)
    map.drawmeridians(meridians, labels=[True, False, False, True])

    plt.title(title)
    plt.show()


# def extract_unique_taxonomies(taxonomies):

#     uniqueTaxonomies = []
#     for taxonomy in taxonomies:
#         if taxonomy not in uniqueTaxonomies:
#             uniqueTaxonomies.append(taxonomy)

#     return uniqueTaxonomies


# def processLosses(uniqueTaxonomy, idTaxonomies, individualLosses):

#     locations = []
#     losses = []
#     assetIDs = idTaxonomies[:, 0]
#     assetTax = idTaxonomies[:, 1]
#     selAssetIDs = assetIDs[np.where(assetTax == uniqueTaxonomy)]
#     for individualLoss in individualLosses:
#         if individualLoss[0] in selAssetIDs:
#             locations.append(individualLoss[1:3])
#             losses.append(individualLoss[3])

#     return np.array(locations), np.array(losses)
