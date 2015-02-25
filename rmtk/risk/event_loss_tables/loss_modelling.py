from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
import math
import os
import rmtk
import parse_ses
import parse_elt

def lossModelling(event_loss_table_folder,save_ses_csv,save_elt_csv,total_cost,return_periods):
	
    investigationTime, ses = parse_ses.parse_ses(event_loss_table_folder,save_ses_csv)
#    investigationTime = 170000
    event_loss_table = parse_elt.parse_elt(event_loss_table_folder,save_elt_csv)
    losses, rateOfExceedance = estimateLosses(event_loss_table,investigationTime)
    maxLoss, aal, aalr, lossLevels = estimateLossStatistics(losses,rateOfExceedance,investigationTime,total_cost,return_periods)
    plotCurves(losses,rateOfExceedance,return_periods,lossLevels)

def selectRuptures(event_loss_table_folder,return_periods,rups_for_return_period):
    
    investigationTime, ses = parse_ses.parse_ses(event_loss_table_folder,False)
    event_loss_table = parse_elt.parse_elt(event_loss_table_folder,False)
    losses, rateOfExceedance = estimateLosses(event_loss_table,investigationTime)
  
    if rups_for_return_period > 0:
        ruptures = captureRuptures(losses,rateOfExceedance,ses,event_loss_table,return_periods,rups_for_return_period)
        for i in range(len(ruptures)):
            plotCapturedRuptures(ruptures[i],return_periods[i])

def exportInfo(event_loss_table_folder):
    
    investigationTime, ses = parse_ses.parse_ses(event_loss_table_folder,False)
    event_loss_table = parse_elt.parse_elt(event_loss_table_folder,False)
    losses, rateOfExceedance = estimateLosses(event_loss_table,investigationTime)
    results = open('results.txt',"w")


    for loss in event_loss_table:
        rup = ses[np.where(ses[:,0]==loss[0]),:][0][0]
        idrup = rup[0]
        mag = rup[1]
        lon = str((float(rup[6])+float(rup[9])+float(rup[12])+float(rup[15]))/4)
        lat = str((float(rup[7])+float(rup[10])+float(rup[13])+float(rup[16]))/4)
        depth = str((float(rup[8])+float(rup[11])+float(rup[14])+float(rup[17]))/4)
        lossValue = loss[2]
        results.write(idrup+','+mag+','+lon+','+lat+','+depth+','+lossValue+'\n')

def plotCapturedRuptures(ruptures,return_period):
            
    mag = []
    lons = []
    lats = []
    depths = []
    
    print 'Ruptures causing losses for a return period of '+str(return_period)+' years'
    print ' '
    for rup in ruptures:
        mag.append(float(rup[1]))
        lon = [float(rup[6]),float(rup[9]),float(rup[12]),float(rup[15])]
        lat = [float(rup[7]),float(rup[10]),float(rup[13]),float(rup[16])]
        depth = [float(rup[8]),float(rup[11]),float(rup[14]),float(rup[17])]
        lons.append(lon)
        lats.append(lat)
        depths.append(depth)
        print rup[0]
        print 'Mag: '+rup[1]+' Lon:%.2f' % round(np.mean(lon),2)+' Lat:%.2f' % round(np.mean(lat),2)+' Depth:%.2f' % round(np.mean(depth),2)
    print ' '

    box = define_bounding_box(lons,lats)
    plt.figure(3, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
    map = Basemap(llcrnrlon=box["lon_1"],llcrnrlat=box["lat_1"],
        urcrnrlon=box["lon_2"],urcrnrlat=box["lat_2"],projection='mill',resolution='i')
    for i in range(len(lons)):
        x, y = map(np.array(lons[i]),np.array(lats[i]))
        plt.plot(x,y,zorder=4,color='red')
    map.drawcoastlines(linewidth=0.25)
    map.drawcountries(linewidth=0.25)
    map.drawstates(linewidth=0.25)
    map.drawmapboundary(fill_color='aqua')
    map.fillcontinents(color='white',lake_color='aqua')

    if box["lat_length"]+2 < 4:
        parallels = np.arange(0.,81,0.5)
    else:
        parallels = np.arange(0.,81,1.0)
    # labels = [left,right,top,bottom]
    map.drawparallels(parallels,labels=[True,False,True,False])
    if box["lon_length"]+2 < 4:
        meridians = np.arange(0.,360,0.5)
    else:
        meridians = np.arange(0.,360,1.0)
    map.drawmeridians(meridians,labels=[True,False,False,True])

    plt.title('Ruptures causing losses for a return periods of '+str(return_period)+' years.')
    plt.show()

def define_bounding_box(lons,lats):

    locations=[]

    for i in range(len(lons)):
        for j in range(len(lons[0])):
            locations.append([lons[i][j],lats[i][j]])
    locations = np.array(locations)

    box = {"lon_0": None, "lat_0": None, "lon_1": None, 
        "lat_1": None, "lon_2": None, "lat_2": None}

    maxCoordinates = locations.max(axis=0)
    minCoordinates = locations.min(axis=0)
    lengthLon = abs(maxCoordinates[0]-minCoordinates[0])
    lengthLat = abs(maxCoordinates[1]-minCoordinates[1])

    box["lon_0"] = (minCoordinates[0]+maxCoordinates[0])/2
    box["lat_0"] = (minCoordinates[1]+maxCoordinates[1])/2
    box["lon_1"] = minCoordinates[0]-1
    box["lat_1"] = minCoordinates[1]-1
    box["lon_2"] = maxCoordinates[0]+1
    box["lat_2"] = maxCoordinates[1]+1
    box["lon_length"] = lengthLon
    box["lat_length"] = lengthLat

    return box

def captureRuptures(losses,rateOfExceedance,ses,event_loss_table,return_periods,rups_for_return_period):
    
    annual_rate_exc = 1.0/np.array(return_periods)
    ruptures = []
    for rate in annual_rate_exc:
        if rate > min(rateOfExceedance):
            diff = np.abs(rateOfExceedance-rate)
            idx = diff.argsort()[0:rups_for_return_period]
            ruptures.append(selectSubRuptures(idx,losses,event_loss_table,ses))
        else:
            print 'Return period of %.0f' % round(1/rate)+' years is above the time length of the stochastic event set.'

    return ruptures

def selectSubRuptures(idx,losses,event_loss_table,ses):

    subRupture = []
    event_losses = np.array(event_loss_table[:,2],dtype=float)
    for ind in idx:
        ruptureTag = event_loss_table[find_nearest(event_losses,losses[ind]),0]
        subRupture.append(ses[np.where(ses[:,0]==ruptureTag),:][0][0])

    return subRupture

def plotCurves(losses,rateOfExceedance,return_periods,lossLevels):

    plt.figure(1, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
    plt.scatter(losses,rateOfExceedance,s=20)
    if len(return_periods) > 0:
        annual_rate_exc = 1.0/np.array(return_periods)
        for rate in annual_rate_exc:
            if rate > min(rateOfExceedance):
                plt.plot([min(losses),max(losses)],[rate,rate],color='red') 
                plt.annotate('%.6f' % rate,xy=(max(losses),rate),fontsize = 12)

    plt.yscale('log')
    plt.xscale('log')
    plt.ylim([min(rateOfExceedance),1])
    plt.xlim([min(losses),max(losses)])
    plt.xlabel('Losses', fontsize = 16)
    plt.ylabel('Annual rate of exceedance', fontsize = 16)

    setReturnPeriods = 1/rateOfExceedance
    plt.figure(2, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
    plt.scatter(setReturnPeriods,losses,s=20)
    if len(return_periods) > 0:
        for period in return_periods:
            if period < max(setReturnPeriods):
                plt.plot([period,period],[min(losses),max(losses)],color='red') 
                plt.annotate(str(period),xy=(period,max(losses)),fontsize = 12)

    plt.xscale('log')
    plt.xlim([min(setReturnPeriods),max(setReturnPeriods)])
    plt.ylim([min(losses),max(losses)])
    plt.xlabel('Return period (years)', fontsize = 16)
    plt.ylabel('Losses', fontsize = 16)

def estimateLossStatistics(losses,rateOfExceedance,investigationTime,total_cost,return_periods):

    maxLoss = losses[0]
    aal = sum(losses)/investigationTime
    aalr = aal/total_cost*100
    lossLevels = []
    print 'Maximum loss:'
    print maxLoss
    print 'Average annual loss:'
    print aal
    print 'Average annual loss ratio (%):'
    print aalr

    if len(return_periods) > 0:
        annual_rate_exc = 1.0/np.array(return_periods)
        for i in range(len(annual_rate_exc)):
            if annual_rate_exc[i] > min(rateOfExceedance):
                idx = find_nearest(rateOfExceedance,annual_rate_exc[i])
                lossLevels.append(losses[idx])
                print 'Loss for a return period of '+str(return_periods[i])+' years.'
                print losses[idx]
            else:
                print 'Return period of '+str(return_periods[i])+' years is above the time length of the stochastic event set.'

    return maxLoss, aal, aalr, lossLevels

def estimateLosses(event_loss_table,investigationTime):

    allLosses = map(float, event_loss_table[:,2])
    allLosses.sort(reverse=True)
    print investigationTime
    print len(allLosses)
    rates = np.arange(1,len(allLosses)+1)/float(investigationTime)

    return allLosses, rates

def find_nearest(array,value):

    return (np.abs(array-value)).argmin()
    

#hist(x, bins=10, range=None, normed=False, weights=None, cumulative=False, bottom=None, histtype=u'bar', align=u'mid', orientation=u'vertical', rwidth=None, log=False, color=None, label=None, stacked=False, **kwargs)
