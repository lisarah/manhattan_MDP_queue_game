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
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import ImageMagickWriter
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
_shape_file = shapefile.Reader("models/taxi_dynamics/shape/taxi_zones.shp")
_fields_name = [field[0] for field in _shape_file.fields[1:]]
_shape_fields = dict(zip(_fields_name, list(range(len(_fields_name)))))

def label_states(violation_density):
    """ Find the name that corresponds to states violating density constraints.
    """
    violation_states = list(violation_density.keys())
    if type(violation_states[0]) == tuple:
        violation_states = [v[0] for v in violation_states]
    bar_labels = [m_neighbors.ZONE_NAME[k] for k in violation_states]  
    return bar_labels


def get_boundaries(borough_str):
    """ Return the lat lon boundaries of the input shape."""
    lat, lon = [], []
    for zone in _shape_file.shapeRecords():
        if zone.record[_shape_fields['borough']] == borough_str:
            lat.extend([zone.shape.bbox[0], zone.shape.bbox[2]])
            lon.extend([zone.shape.bbox[1], zone.shape.bbox[3]])

    margin = 1e-12 # buffer to add to the range
    lat_min = min(lat) - margin
    lat_max = max(lat) + margin
    lon_min = min(lon) - margin
    lon_max = max(lon) + margin

    return lat_min, lat_max, lon_min, lon_max

 

def get_lat_lon():
    """ Return the lat, lon, and location id of the input shape."""
    content = []
    loc_id_str = 'LocationID'
    lon_str = 'longitude'
    lat_str = 'latitude'
    for shape_record in _shape_file.shapeRecords():
        shape = shape_record.shape
        loc_id = shape_record.record[_shape_fields[loc_id_str]]
        
        x = (shape.bbox[0]+shape.bbox[2])/2
        y = (shape.bbox[1]+shape.bbox[3])/2
        
        content.append((loc_id, x, y))
    return pd.DataFrame(content, columns=[loc_id_str, lon_str, lat_str])

def get_zone_locations(borough_str):
    """ Return each zone's longitude/latitude as a dictionary of tuples."""
    attributes = _shape_file.records()
    shape_attributes = [dict(zip(_fields_name, attr)) for attr in attributes]

    id_str = "LocationID"
    df_loc = pd.DataFrame(shape_attributes).join(
        get_lat_lon().set_index(id_str), 
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
    patch_list = []
    if nparts == 1:
        polygon = Polygon(shape.points)
        patch = PolygonPatch(polygon, facecolor=color, alpha=1.0, zorder=2)
        patch_list.append(ax.add_patch(patch))
    else: # loop over parts of each shape, plot separately
        for ip in range(nparts): # loop over parts, plot separately
            i0 = shape.parts[ip]
            if ip < nparts-1:
                i1 = shape.parts[ip+1]-1
            else:
                i1 = len(shape.points)

            polygon = Polygon(shape.points[i0:i1+1])
            patch = PolygonPatch(polygon, facecolor=color, alpha=1.0, zorder=2)
            patch_list.append(ax.add_patch(patch))
    return patch_list

def update_borough(t, patch_dict, densities, color_map, norm):
    for zone_ind, patches in patch_dict.items():
        R,G,B,A = color_map(norm((densities[(zone_ind, 0)])))
        color = [R,G,B]    
        for patch in patches:
            patch.set_facecolor(color)
            
def draw_borough(ax, densities, borough_str, color_map, norm):
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
    ocean_color = (89/256/3, 171/256/3, 227/256/3) 
    ax.set_facecolor(ocean_color)
    zone_x = []
    zone_y = []
    patch_dict = {}
    # colorbar
    if norm == None:
        norm = mpl.colors.Normalize(vmin=min(densities.values()), 
                                    vmax=max(densities.values()))
    if color_map is None:
        color_map=plt.get_cmap('Reds')
        
    for shape_entry in _shape_file.shapeRecords():
        shape = shape_entry.shape
        record = shape_entry.record
        borough_name = record[_shape_fields['borough']]
        
        if (record[_shape_fields['zone']] ==
            "Governor's Island/Ellis Island/Liberty Island"):
            continue            
        elif borough_name != borough_str:
            continue
        zone_ind = m_neighbors.ZONE_IND[record[_shape_fields['zone']]]
        if zone_ind in [103, 104, 105, 153, 194, 202]:
            continue
        
        R,G,B,A = color_map(norm((densities[zone_ind])))
        color = [R,G,B]              
        patch_list = draw_shape(ax, shape, color)
        zone_x.append((shape.bbox[0] + shape.bbox[2]) / 2)
        zone_y.append((shape.bbox[1] + shape.bbox[3]) / 2)
        
        patch_dict[zone_ind] = patch_list
            
    # display borough name  
    plt.text(np.min(zone_x)+0.05, np.max(zone_y) - 1e-3, borough_str, 
              horizontalalignment='center', verticalalignment='center', 
              bbox=dict(facecolor='black', alpha=0.5), 
              color="white", fontsize=18) 
     
    # display
    limits = get_boundaries(borough_str)
    plt.xlim(limits[0]+0.025, limits[1])
    plt.ylim(limits[2]+0.015, limits[3])
    cbar = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=color_map), ax=ax)
    cbar.ax.tick_params(labelsize=13) 
    # plt.grid()
    return patch_dict

def set_axis_limits(ax_bar, ax_time, T, is_toll, max_d, min_d, constrained_val):
    if not is_toll:
        ax_bar.set_ylim([constrained_val-10, max_d+10])
    else:
        ax_bar.set_ylim([0, 0.5]) # when drawing tolling value        
        ax_bar.set_xlim([0, T-1])
        ax_bar.grid(True)


    ax_bar.xaxis.set_visible(False)           
    ax_time.set_xlim([0, T-1])
    ax_time.set_ylim([min_d-10, 550])
    ax_time.set_xlabel(r"Time",fontsize=13)
    ax_time.grid(True)

def animate_combo(file_name, z_density, violation_density, 
                  constraint_violation, toll_val=None, max_d=None, min_d=None,
                  plot_toll=None):
    T = len(z_density)
    # determine min/max density levels
    min_density = 1
    max_density = 1
    for t in range(T): 
        min_density = min(list(z_density[t].values()) + [min_density])
        max_density = max(list(z_density[t].values()) + [max_density])
    if max_d != None:
        max_density = max_d
    if min_d != None:
        min_density = min_d
    print(f'minimum density = {min_density}')
    print(f'maximum density = {max_density}')

    # set up figure
    fig_width = 5.3 * 2
    f = plt.figure(figsize=(fig_width,8))
    ax_bar = f.add_subplot(2, 2, 1)
    ax_time = f.add_subplot(2, 2, 3)
    ax_map = f.add_subplot(1, 2, 2)
    ax_map.xaxis.set_visible(False)
    ax_map.yaxis.set_visible(False)
    set_axis_limits(ax_bar, ax_time, T, plot_toll is not None, 
                    max_density, min_density, toll_val)
    
    # set up heat map color map and bar plot legend
    norm = mpl.colors.Normalize(vmin=(min_density), vmax=(max_density))
    color_map = plt.get_cmap('coolwarm') # Spectral
    bar_labels = label_states(violation_density)
    
    
    d_0 = {z_ind[0]: z_density[0][z_ind] for z_ind in z_density[0].keys() 
           if z_ind[1] == 0}
    patch_dict = draw_borough(ax_map, d_0, 'Manhattan', color_map, norm)      
    plt.show()
    def animate(i):
        ax_bar.clear()
        ax_time.clear()
        ax_time.plot([toll_val]*T, linewidth=6, alpha=0.5, color=[0.1,0.1,0.1])
        
        loc_ind = 0
        time_step = min(i % T , T-1)
        d_t = {z_ind: z_density[time_step][z_ind] 
               for z_ind in z_density[time_step].keys() if z_ind[1] == 0}
            
        set_axis_limits(ax_bar, ax_time, T, plot_toll is not None, 
                        max_density, min_density, toll_val)
        for violation in violation_density.keys():
            v_ind = (violation, 0) if type(violation) == int else violation
            bar_val = z_density[time_step][v_ind]
            if plot_toll is not None:
                for z_ind, t_toll in plot_toll.items():
                    ax_bar.plot(t_toll[:time_step], linewidth=3, 
                                label=m_neighbors.ZONE_NAME[z_ind], marker='D', 
                                markersize=8)
            else:   
                ax_bar.bar(loc_ind, bar_val, width = 0.8, 
                           label=bar_labels[loc_ind])
            
            ax_time.plot([z_density[t][v_ind] for t in range(time_step)],
                          linewidth=3, label=bar_labels[loc_ind], marker='D', 
                          markersize=8)
            loc_ind +=1
        ax_time.legend(loc='lower right', fontsize=13)
        # ax_bar.legend(loc='lower right', fontsize=13)
        update_borough(time_step, patch_dict, z_density[time_step], 
                       color_map, norm)
  
    ani = animation.FuncAnimation(f, animate, frames=range(T), interval=250)
    plt.show()
    ani.save(file_name, writer='ffmpeg')  # imagemagick
    
    
def plot_borough_progress(borough_str, plot_density, times):
    subplot_num = len(times)
    state_ind  = m_neighbors.zone_to_state(m_neighbors.zone_neighbors)
    density_dicts = []
    min_density = 999999
    max_density = -1
    for plot_ind in range(subplot_num):
        density_dicts.append({})
        for zone_ind in m_neighbors.zone_neighbors.keys():
            density_dicts[-1][zone_ind] = np.sum(
                plot_density[state_ind[zone_ind], :, times[plot_ind]])

            min_density = min(list(density_dicts[-1].values()) + [min_density])
            max_density = max(list(density_dicts[-1].values()) + [max_density])
       
    norm = mpl.colors.Normalize(vmin=(min_density), vmax=(max_density))
    color_map = plt.get_cmap('Reds')
    
    fig_width = 5.3 * subplot_num
    # plt.figure(figsize=(fig_width,8))
    f = plt.figure(figsize=(fig_width,8))
    # fig, _ = plt.subplots(nrows=1, ncols=subplot_num, figsize=(fig_width,8))
    for plot_ind in range(subplot_num):
        ax = f.add_subplot(1, subplot_num, 1 + plot_ind)
        draw_borough(ax, density_dicts[plot_ind], borough_str, 
                     times[plot_ind], color_map, norm)
    plt.show()
    
    
def summary_plot(z_density, constraint_violation, violation_density, 
                 avg_density, constrained_value, tolls=None, max_d=None, 
                 min_d=None, return_min_max=False):
    T = len(z_density)
    # determine min/max density levels
    min_density = 1
    max_density = 1
    for t in range(T): 
        min_density = min(list(z_density[t].values()) + [min_density])
        max_density = max(list(z_density[t].values()) + [max_density])
    heat_max = max_density
    heat_min = min_density
    if max_d == None:
        max_d = max_density
    if min_d == None:
        min_d = min_density
    print(f'minimum density = {min_d}')
    print(f'maximum density = {max_d}')

    # set up heat map color map and bar plot legend
    norm = mpl.colors.Normalize(vmin=(heat_min), vmax=(heat_max))
    color_map = plt.get_cmap('coolwarm') # Spectral
    bar_labels = label_states(violation_density)
   

    # overall summary plot        
    fig_width = 5.3 * 2
    f = plt.figure(figsize=(fig_width,8))
    ax_bar = f.add_subplot(2,2,1)
    ax_time = f.add_subplot(2,2,3)
    ax_map = f.add_subplot(1,2,2)
    set_axis_limits(ax_bar, ax_time, T, tolls is not None, max_d, min_d, 
                    constrained_value)
    seq = [i for i in range(len(violation_density))] #
    # if toll values are given, plot tolls on upper left
    if tolls != None:
        print('printing tolls')
        toll_time_vary = []
        for line in tolls.values(): 
            toll_time_vary.append(line)
        for line_ind in seq:
            ax_bar.plot(toll_time_vary[line_ind], linewidth=3, 
                        label=bar_labels[line_ind])
    else:
    # bar plot upper left        
        violations = []
        for v in constraint_violation.values(): 
            violations.append(v)
        loc_ind = 0
        for bar_ind in seq:
            ax_bar.bar(loc_ind, violations[bar_ind] + constrained_value, 
                    width = 0.8,  
                    label=bar_labels[bar_ind])
            loc_ind +=1
        ax_bar.legend(fontsize=13)

    # line plot lower left
    ax_time.plot(constrained_value * np.ones(T), 
              linewidth = 6, alpha = 0.5, color=[0,0,0])
    lines = []
    for line in violation_density.values(): 
        lines.append(line)
    for line_ind in seq:
        ax_time.plot(lines[line_ind], linewidth=3, label=bar_labels[line_ind], 
                     marker='D', markersize=8)
    ax_time.legend(fontsize=13)
    
    
    # heat map right side
    draw_borough(ax_map, avg_density, 'Manhattan', color_map, norm)
    ax_map.xaxis.set_visible(False)
    ax_map.yaxis.set_visible(False)
    plt.show()
    
    if return_min_max:
        return heat_min, heat_max
    
def toll_summary_plot(violation_density, tolls,
                   constrained_value, max_d, min_d=150, T=12):
    bar_labels = label_states(violation_density)

    # overall summary plot        
    fig_width = 5.3 * 2
    f = plt.figure(figsize=(fig_width,8))
    seq = [i for i in range(len(violation_density))] #
    # if toll values are given, plot tolls on upper left
    ax_toll_val = f.add_subplot(2,1,1) # (2,2,2)
    toll_time_vary = []
    for line in tolls.values(): 
        toll_time_vary.append(line)
    for line_ind in seq:
        ax_toll_val.plot(toll_time_vary[line_ind], linewidth=3, 
                         label=bar_labels[line_ind], marker='D', markersize=10)
    plt.setp(ax_toll_val.get_xticklabels(), visible=False)
    plt.grid()

    # line plot lower left
    ax_time = f.add_subplot(2, 1, 2,sharex=ax_toll_val)
    ax_time.plot(constrained_value * np.ones(T), 
              linewidth = 6, alpha = 0.5, color=[0,0,0])
    lines = []
    for line in violation_density.values(): 
        lines.append(line)
    for line_ind in seq:
        plt.plot(lines[line_ind], linewidth=3, 
                  label=bar_labels[line_ind], marker='D', markersize=10)
    ax_time.set_ylim([min_d, max_d])
    plt.xlabel(r"Time",fontsize=12)
    plt.grid()
    plt.legend(fontsize=10)
    plt.subplots_adjust(hspace=0.05)   
    plt.show()
    