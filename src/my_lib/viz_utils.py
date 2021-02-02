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

def get_roc_fig(event, event_name, predictors_list, predictors_names):
    
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
      

  # plot    
  fig, ax = plt.subplots(1, 1, figsize = (8, 8))
  
  colors = ["tab:orange",
            "tab:blue"]
   
  for idx, predictor in enumerate(predictors_list):
    fpr, tpr, thresh = metrics.roc_curve(event, predictor)
    roc_auc = metrics.roc_auc_score(event, predictor)
    
    ax.plot(fpr, tpr, 
            color = colors[idx],
            label = '%s : (AUC: %2.3f)'%(predictors_names[idx], roc_auc))
  
  
  ax.plot([0, 1], [0, 1], color = "k", linestyle = "dashed", linewidth = .75)
  ax.legend()
  ax.set_xlabel('False Positive Rate')
  ax.set_ylabel('True Positive Rate')
  ax.set_title("ROC - %s\n"%(event_name))
  ax.set_xlim([0, 1])
  ax.set_ylim([0, 1])
  
## ----------------------------------------
  
def plot_km(axis, subgroups_to_plot, labels, colors, num_xticks = 14,
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