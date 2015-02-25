from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
import math
import os
import rmtk
import rmtk.plotting.common.parse_collapse_maps as parsecm
import rmtk.plotting.common.parse_exposure as parsee 

def build_map(plotting_type,collapse_map,bounding_box,log_scale,exposure_model,marker_size,export_map_to_csv):
	
    exposure_path = os.path.dirname(rmtk.__file__) + "/plotting/input_models/" + exposure_model
		
    agg_collapses = True
    if plotting_type == 1:
        agg_collapses = False

    data = parsecm.parse_collapse_maps(collapse_map,agg_collapses,export_map_to_csv)
    box = define_bounding_box(bounding_box,data[0])

    if plotting_type == 0 or plotting_type == 2:
        locations = np.array(data[1][0])
        collapses = np.array(data[1][1])
      	plot_single_map(locations,collapses,box,log_scale,marker_size,'Aggregated Collapses per location',1)

    if plotting_type == 1 or plotting_type == 2:
        individualCollapses = data[0]
        idTaxonomies = np.array(parsee.extractIDTaxonomies(exposure_path,False))
        uniqueTaxonomies = extract_unique_taxonomies(idTaxonomies[:,1])
        collapsesTaxonomies = np.zeros((len(uniqueTaxonomies)))
        for i in range(len(uniqueTaxonomies)):
            locations,collapses = processLosses(uniqueTaxonomies[i],idTaxonomies,individualCollapses)
            collapsesTaxonomies[i] = sum(collapses)
            if locations.shape[0] > 0:
                plot_single_map(locations,collapses,box,log_scale,marker_size,'Collapse map for '+uniqueTaxonomies[i],i+2)
	plot_pie_chart_losses(uniqueTaxonomies,collapsesTaxonomies)

def plot_pie_chart_losses(uniqueTaxonomies,lossesTaxonomies):

    labels = uniqueTaxonomies
    sizes = lossesTaxonomies
    colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral']

    plt.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
    plt.title('Total loss per taxonomy')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.axis('equal')

def define_bounding_box(bounding_box,data):

    locations=[]

    for asset in data:
        locations.append(asset[1:3])
    locations = np.array(locations)

    box = {"lon_0": None, "lat_0": None, "lon_1": None, 
        "lat_1": None, "lon_2": None, "lat_2": None}

    if bounding_box == 0:
        maxCoordinates = locations.max(axis=0)
        minCoordinates = locations.min(axis=0)
    else:
        maxCoordinates = [bounding_box[2],bounding_box[3]]
        minCoordinates = [bounding_box[0],bounding_box[1]]

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

def plot_single_map(locations,losses,box,log_scale,marker_size,title,figNo):

    plt.figure(figNo, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
    map = Basemap(llcrnrlon=box["lon_1"],llcrnrlat=box["lat_1"],
        urcrnrlon=box["lon_2"],urcrnrlat=box["lat_2"],projection='mill',resolution='i')

    x, y = map(locations[:,[0]],locations[:,[1]])
    #map.shadedrelief()
    map.drawcoastlines(linewidth=0.25)
    map.drawcountries(linewidth=0.25)
    map.drawstates(linewidth=0.25)
    map.drawmapboundary(fill_color='aqua')
    map.fillcontinents(color='white',lake_color='aqua')
    
    scale = None
    if log_scale:
        scale = LogNorm()

    plt.scatter(x,y,s=marker_size,c=losses,zorder=4,cmap='YlOrRd',edgecolor='None',norm = scale)
    if locations.shape[0] > 1:
        cbar = map.colorbar(location='right',pad="5%")
        cbar.set_label('Number of collapses')

    if box["lat_length"] < 2:
        parallels = np.arange(0.,81,0.25)
    else:
        parallels = np.arange(0.,81,1.0)
    # labels = [left,right,top,bottom]
    map.drawparallels(parallels,labels=[True,False,True,False])
    if box["lon_length"] < 2:
        meridians = np.arange(0.,360,0.25)
    else:
        meridians = np.arange(0.,360,1.0)
    map.drawmeridians(meridians,labels=[True,False,False,True])

    plt.title(title)
    plt.show()

def extract_unique_taxonomies(taxonomies):

    uniqueTaxonomies = []
    for taxonomy in taxonomies:
        if taxonomy not in uniqueTaxonomies:
            uniqueTaxonomies.append(taxonomy)

    return uniqueTaxonomies

def processLosses(uniqueTaxonomy,idTaxonomies,individualLosses):

    locations = []
    losses = []
    assetIDs = idTaxonomies[:,0]
    assetTax = idTaxonomies[:,1]
    selAssetIDs = assetIDs[np.where(assetTax==uniqueTaxonomy)]
    for individualLoss in individualLosses:
        if individualLoss[0] in selAssetIDs:
            locations.append(individualLoss[1:3])
            losses.append(individualLoss[3])

    return np.array(locations),np.array(losses)

