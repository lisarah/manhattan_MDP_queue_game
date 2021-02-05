# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 22:56:42 2021

Manhattan visualization - 
following here: https://chih-ling-hsu.github.io/2018/05/14/NYC#location-data

Code requires descartes, shapefile and shapely. 
With anaconda: 
    - conda install -c conda-forge pyshp shapely descartes
@author: Sarah Li
"""
import shapefile
from shapely.geometry import Polygon
from descartes.patch import PolygonPatch
import math
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import models.taxi_dynamics.manhattan_neighbors as m_neighbors

_borough_index ={
    'Staten Island':1, 
    'Queens':2, 
    'Bronx':3, 
    'Manhattan':4, 
    'EWR':5, 
    'Brooklyn':6}

def get_boundaries(shape_file, record_fields, borough_str):
    """ Return the lat lon boundaries of the input shape."""
    lat, lon = [], []
    for zone in shape_file.shapeRecords():
        if zone.record[record_fields['borough']] == borough_str:
            lat.extend([zone.shape.bbox[0], zone.shape.bbox[2]])
            lon.extend([zone.shape.bbox[1], zone.shape.bbox[3]])

    margin = 1e-12 # buffer to add to the range
    lat_min = min(lat) - margin
    lat_max = max(lat) + margin
    lon_min = min(lon) - margin
    lon_max = max(lon) + margin

    return lat_min, lat_max, lon_min, lon_max

 

def get_lat_lon(shape_file, record_fields):
    """ Return the lat, lon, and location id of the input shape."""
    content = []
    loc_id_str = 'LocationID'
    lon_str = 'longitude'
    lat_str = 'latitude'
    for shape_record in shape_file.shapeRecords():
        shape = shape_record.shape
        loc_id = shape_record.record[record_fields[loc_id_str]]
        
        x = (shape.bbox[0]+shape.bbox[2])/2
        y = (shape.bbox[1]+shape.bbox[3])/2
        
        content.append((loc_id, x, y))
    return pd.DataFrame(content, columns=[loc_id_str, lon_str, lat_str])

def get_zone_locations(borough_str):
    """ Return each zone's longitude/latitude as a dictionary of tuples."""
    shape_file = shapefile.Reader("models/taxi_dynamics/shape/taxi_zones.shp")
    fields_name = [field[0] for field in shape_file.fields[1:]]
    shape_fields = dict(zip(fields_name, list(range(len(fields_name)))))
    attributes = shape_file.records()
    shape_attributes = [dict(zip(fields_name, attr)) for attr in attributes]

    id_str = "LocationID"
    df_loc = pd.DataFrame(shape_attributes).join(
        get_lat_lon(shape_file, shape_fields).set_index(id_str), 
        on=id_str)  
    borough_only = df_loc[df_loc.borough == borough_str]
    zone_geography = {}
    for data in borough_only.itertuples():
        zone_geography[data.LocationID] = (data.latitude, data.longitude)
    return zone_geography
    
    
def draw_shape(ax, shape, color):
    """ Draw the given shape using Polygons.
    
    Args:
        ax: matplotlib Axis object.
        shape: shapefile Shape object.
    """
    nparts = len(shape.parts) # total parts
    if nparts == 1:
        polygon = Polygon(shape.points)
        patch = PolygonPatch(polygon, facecolor=color, alpha=1.0, zorder=2)
        ax.add_patch(patch)
    else: # loop over parts of each shape, plot separately
        for ip in range(nparts): # loop over parts, plot separately
            i0 = shape.parts[ip]
            if ip < nparts-1:
                i1 = shape.parts[ip+1]-1
            else:
                i1 = len(shape.points)

            polygon = Polygon(shape.points[i0:i1+1])
            patch = PolygonPatch(polygon, facecolor=color, alpha=1.0, zorder=2)
            ax.add_patch(patch)

            
def draw_borough(ax, shape_file, densities, record_fields, borough_str):
    """ Plot the given zone densities in the borough of interest.
    
    Args:
        ax: a matplotlib Axis object.
        shape_file: the ShapeRecords object containing zone information.
        densities: a dictionary of densities, with zone id as key, and density
            as value.
        record_fields: a dictionary of the record indices with record name as
            key, and record index as value.        
        borough_str: the name of the borough whose density is plotted..
    """
    ocean_color = (89/256, 171/256, 227/256) 
    ax.set_facecolor(ocean_color)
    zone_x = []
    zone_y = []
    # colorbar
    norm = mpl.colors.Normalize(vmin=math.sqrt(min(densities.values())), 
                                vmax=math.sqrt(max(densities.values()))) 
    color_map=plt.get_cmap('Reds')
    for shape_entry in shape_file.shapeRecords():
        shape = shape_entry.shape
        record = shape_entry.record
        borough_name = record[record_fields['borough']]
        
        if (record[record_fields['zone']] ==
            "Governor's Island/Ellis Island/Liberty Island"):
            continue            
        elif borough_name != borough_str:
            continue
        zone_ind = m_neighbors.ZONE_IND[record[record_fields['zone']]]
        if zone_ind in [103, 104, 105, 153, 194, 202]:
            continue
            
        R,G,B,A = color_map(norm(math.sqrt(densities[zone_ind])))
        color = [R,G,B]              
        draw_shape(ax, shape, color)

        zone_x.append((shape.bbox[0] + shape.bbox[2]) / 2)
        zone_y.append((shape.bbox[1] + shape.bbox[3]) / 2)
            
    # display borough name  
    plt.text(np.min(zone_x)+0.01, np.max(zone_y) - 1e-3, borough_str, 
              horizontalalignment='center', verticalalignment='center', 
              bbox=dict(facecolor='black', alpha=0.5), 
              color="white", fontsize=24) 
     
    # display
    limits = get_boundaries(shape_file, record_fields, borough_str)
    plt.xlim(limits[0], limits[1])
    plt.ylim(limits[2], limits[3])
    plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=color_map), ax=ax)
    # plt.grid()
 
def animate_borough(borough_str, densities):
    shape_file = shapefile.Reader("models/taxi_dynamics/shape/taxi_zones.shp")
    fields_name = [field[0] for field in shape_file.fields[1:]]
    shape_fields = dict(zip(fields_name, list(range(len(fields_name)))))

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(5.2,8))
    ax = plt.subplot(1, 1, 1)
    # ax.set_title(f"NYC {borough_str}")
    
    draw_borough(ax, shape_file, densities, shape_fields, borough_str)
    # ax = plt.subplot(1, 2, 2)
    # ax.set_title("Zones in NYC")
    # draw_zone_map(ax, sf)
    plt.show()
