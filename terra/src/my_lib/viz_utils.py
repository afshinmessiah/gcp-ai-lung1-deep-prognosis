"""
    ----------------------------------------
    IDC MedIA use case (Colab Demo)
    
    useful functions (data viz)
    ----------------------------------------
    
    ----------------------------------------
    Author: Dennis Bontempi
    Email:  dennis_bontempi@dfci.harvard.edu
    Modified: 01 FEB 21
    ----------------------------------------
    
"""

import os
import lifelines
import numpy as np

from sklearn import metrics

## ----------------------------------------

#everything that has to do with plotting goes here below

import matplotlib
matplotlib.use('agg')

import matplotlib.pyplot as plt

## ----------------------------------------
## ----------------------------------------

def get_roc_fig(axis, colors, event, event_name, predictors_list, predictors_names):
    
  # "event" should be a list or a ndarray
  assert isinstance(event, np.ndarray) or isinstance(event, list)
  
  # if list, convert into np.ndarray for simplicity
  if isinstance(event, list): event = np.array(event)
  
  
  # predictors_list should be a list of ndarray(s) or lists
  assert isinstance(predictors_list, list)
  assert isinstance(predictors_list[0], np.ndarray) or isinstance(predictors_list[0], list)
  
  # if list(s), convert into np.ndarray(s) for simplicity
  for idx, predictor in enumerate(predictors_list):
    if isinstance(predictor, list): predictors_list[idx] = np.array(predictor)
   
  for idx, predictor in enumerate(predictors_list):
    fpr, tpr, thresh = metrics.roc_curve(event, predictor)
    roc_auc = metrics.roc_auc_score(event, predictor)
    
    axis.plot(fpr, tpr, 
              color = colors[idx],
              label = '%s : (AUC: %2.3f)'%(predictors_names[idx], roc_auc))
  
  
  axis.plot([0, 1], [0, 1], color = "k", linestyle = "dashed", linewidth = .75)
  axis.legend()
  axis.set_xlabel('False Positive Rate')
  axis.set_ylabel('True Positive Rate')
  axis.set_title("ROC - %s\n"%(event_name))
  axis.set_xlim([0, 1])
  axis.set_ylim([0, 1])
  
## ----------------------------------------
  
def plot_km(axis, subgroups_to_plot, labels, colors, num_xticks = 5,
            ci_show = False, show_censors = True, at_risk_counts = False):
  
  # "subgroups_to_plot" should be a list of dataframes
  assert isinstance(subgroups_to_plot, list)

  kmf = lifelines.KaplanMeierFitter() 

  leg_list = list()
    
  for idx, subgroup in enumerate(subgroups_to_plot):
    
    leg_list.append(matplotlib.lines.Line2D(xdata = [0], ydata = [0],
                                            color = colors[idx],
                                            linewidth = 1))
    try:
      # maximum days survived (dead patients)
      tmp_max = max(subgroup["Survival.time"].fillna(value = 0).values)
      
      # set days_survived = max(...) for all the patients which are still alive (otherwise NaN)
      kmf.fit(durations = subgroup["Survival.time"].fillna(value = tmp_max).values,
              event_observed = subgroup["deadstatus.event"].values)
      
      # append the km plot object to the axis "axis"
      kmf.plot(ax = axis,
               ci_show = ci_show,
               show_censors = show_censors,
               at_risk_counts = at_risk_counts,
               color = colors[idx])
    except:
      pass
      
      
  axis.set_xlabel("\nTimeline")
  axis.set_ylim([0, 1])
  axis.set_xlim([0, 365*num_xticks])
  axis.set_xticks(365*np.arange(0, num_xticks))
  xticklabels = [str(y) + "y" if y > 0 else "" for y in range(0, num_xticks)]
  axis.set_xticklabels(xticklabels)

  return leg_list

## ----------------------------------------

def plot_distr(axis, colors, attr_list, attr_names, xlim):

  leg_list = list()

  for idx, attr in enumerate(attr_list):
    
    leg_entry = matplotlib.patches.Patch(facecolor = colors[idx],
                                         edgecolor = 'k',
                                         linewidth = 0.7,
                                         label = attr_names[idx])
    
    leg_list.append(leg_entry)
    
    v = axis.violinplot(attr,
                        showmeans = False,
                        showextrema = False,
                        showmedians = False,
                        vert = False)

    for b in v['bodies']:
      m = np.mean(b.get_paths()[0].vertices[:, 0])
      b.get_paths()[0].vertices[:, 1] = np.clip(b.get_paths()[0].vertices[:, 1], 1, np.inf)
      b.set_color(colors[idx])
      b.set_alpha(0.8)
      b.set_linewidth(0.7)
      b.set_edgecolor("k")

  axis.set_ylabel('Relative Frequency\n')
  axis.set_yticks([ 1, 1.1, 1.2])
  axis.set_yticklabels(["0", "0.1", "0.2"])
  axis.set_ylim([1, 1.3])
  axis.set_xlim(xlim)
  
  return leg_list