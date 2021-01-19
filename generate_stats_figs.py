import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import t
from pptx.util import Cm, Pt
import os


def calc_stain_index(pos, neg, rsd):
    return (pos-neg)/(2*rsd)

def calc_SN(pos, neg):
    return pos/neg

def calc_pct4C(ref, pos):
    return (pos/ref)*100


def generate_meta_dct(rm_si_sn):
    dct = {'mfi_v_conc' :
                {'title': 'MFI vs. Concentration', 'ylim_label': 'median_pos',
                 'ylabel': 'MFI', 'xlabel':'Concentration'},
            'mfi_v_time' :
                {'title': 'MFI vs. Time', 'ylim_label': 'median_pos',
                 'ylabel': 'MFI', 'xlabel': 'Time'},
            'pos_v_conc' :
                {'title': 'Positive vs. Concentration', 'ylim_label': 'pos_pct',
                 'ylabel': '% (+)', 'xlabel': 'Concentration'},
            'pct_4c_ref' :
                {'title': '% of 4C Reference MFI', 'ylim_label': 'pct4C',
                 'ylabel': '%', 'xlabel': 'Time'},
            'stain_index' :
                {'title': 'Stain Index', 'ylim_label': 'stain_index',
                 'ylabel': 'Stain Index', 'xlabel': 'Time'},
            'signal_noise':
                {'title': 'Signal/Noise', 'ylim_label': 'signal_noise',
                 'ylabel': 'S/N', 'xlabel': 'Time'},
           }
    if rm_si_sn:
        dct.pop('signal_noise', None)
        dct.pop('stain_index', None)
    return dct

def colnames():
    return ['filename', 'condition', 'concentration', 'pos_pct', 'median_pos', 'median_neg', 'rsd']

def category_set(df):
    # convert to custom category dtype
    sorter = ['4C', '0.5y', '1.0y', '1.5y', '2.0y', '3.0y', '4.0y', '5.0y']
    df.condition = df.condition.astype("category")
    df.condition.cat.set_categories(sorter, inplace=True)
    return df

def add_sn_si(df):
    """
    add signal to noise and stain index columns
    """
    # add stain index column
    df['stain_index'] = df.apply(lambda x: calc_stain_index(x['median_pos'],
                                    x['median_neg'], x['rsd']), axis = 1)
    # add signal to noise column
    df['signal_noise'] = df.apply(lambda x: calc_SN(x['median_pos'],
                                    x['median_neg']), axis = 1)
    return df

def produce_ref_mfi_list(df):
    # replicate the ref mfis of 4c 8x and flatten list
    ref_mfis = [[e]*8 for e in df['median_pos'][df['condition']=='4C'].tolist()]
    ref_mfis = [item for sublist in ref_mfis for item in sublist]
    return ref_mfis

def tidy_data(csv_file):
    """
    tidy up data and add necessary columns
    prepare for plotting
    """

    rm_si_sn = True
    df = pd.read_csv(csv_file)
    df.drop(axis=1, labels=['Unnamed: 7'], inplace=True)
    # set column names
    df.columns = colnames()
    # remove mean and SD rows
    df = df.iloc[:len(df)-2, :]
    if (~df['rsd'].isnull().any() and ~df['median_pos'].isnull().any()):
        df = add_sn_si(df)
        rm_si_sn = False
    # convert to int32 dtype
    df['concentration'] = df['concentration'].astype({'concentration': 'int32'})
    df = category_set(df)
    # sort on concnetration first then condition to calc the 4C ref MFI
    df = df.sort_values(['concentration','condition'])
    ref_mfis = produce_ref_mfi_list(df)
    # create percent 4C column
    df['pct4C'] = [calc_pct4C(a,b) for a,b in zip(ref_mfis, df['median_pos'])]
    # ensure the order
    df = df.sort_values(["condition", "concentration"]).groupby('condition').head(8)
    # print()
    # print(df.head(2))
    return df, rm_si_sn


def create_stats_plot(df, meta_dct, plot_type, wd):
    """
    parse df to plot line charts for stability tests

    args:
    ====
    df - pandas dataframe object
    plot_type - 1) mfi_v_conc 2) stain_index 3) signal_noise
                4) mfi_v_time 5) pct_4c_ref 6) pos_v_conc
    """
    fig, ax = plt.subplots(figsize=(11.5,6.5))
    ylim_label = meta_dct[plot_type]['ylim_label']
    ylims = df[ylim_label].max()
    ylower = 0
    if plot_type == 'signal_noise':
        ylower = df[ylim_label].min()
        ylower = ylower - (ylower*0.04)
    ax.set_ylim(ylower,ylims+(ylims*0.04))
    ax.set_xticks([])
    ax.set_ylabel(meta_dct[plot_type]['ylabel'])
    xlabel = meta_dct[plot_type]['xlabel']
    ax.set_xlabel(xlabel)
    ax.set_title(meta_dct[plot_type]['title'], y=1.1)
    metric = 'concentration'
    other_metric = 'condition'
    if xlabel.lower() == 'time':
        metric, other_metric = 'condition', 'concentration'
    data_x = df[metric].unique().tolist()
    columns = tuple(data_x)
    rows = df[other_metric].unique().tolist()
    colours = plt.get_cmap('Set1')
    cell_text = []
    for i,cond in enumerate(rows):
        data_y = df[ylim_label][df[other_metric] == cond].round(1)
        ax.plot(data_x,
                data_y,
                label = cond if type(cond) == str else f'{cond} ng',
                marker='o',
                color = colours(i))
        cell_text.append(data_y.tolist())

    if other_metric == 'concentration':
        rows = [f'{r} ng' for r in rows]
    the_table = plt.table(cellText = cell_text,
                          rowLabels = rows,
                          colLabels = [f'{c} ng' if type(c) != str else c for c
                                       in columns],
                          rowColours = [colours(i) for i in range(len(rows))],
                          loc = 'bottom')

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.xaxis.labelpad = 120
    # Put a legend above
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1),
              ncol=8, fancybox=True)

    plt.savefig(os.path.join(wd, f'{plot_type}.png'),
                format='png', bbox_inches='tight')

#REGRESSION
def prepare_regr_df(df):
    # subset dataframe
    dfr = df[['pct4C','condition', 'concentration']]
    # change from long to wide dataframe
    dfr = dfr.pivot(index= 'condition', columns = 'concentration', values = 'pct4C')
    # add average column
    dfr['average'] = pd.Series(dfr.mean(axis=1))
    return dfr

def output_time_xvals(df):
    # remove the 'C' or 'y' from the year
    return [float(x[:-1]) if i>0 else 0 for i,x in enumerate(df.index.tolist())]

def calc_thresCI(thres, dct):
    noCI =  (thres - dct['intercept'])/dct['slope']
    CI =  (thres - dct['intercept_lowerCI'])/dct['slope_lowerCI']
    print(f'noCI {thres}%: {noCI}\nCI {thres}%: {CI}')
    return noCI, CI


def generate_regr_vals(time_xvals, df):
    fit = np.polyfit(time_xvals,np.array(df['average']),deg=1)
    count = len(time_xvals)
    slope = fit[0]
    intercept = fit[1]
    x_bar = np.mean(time_xvals)
    correlation_matrix = np.corrcoef(time_xvals, df['average'])
    correlation_xy = correlation_matrix[0,1]
    r_squared = correlation_xy**2
    return {
            'count': count,
            'slope': slope,
            'intercept': intercept,
            'x_bar': x_bar,
            'r_squared': r_squared,
            'xvals': np.array(time_xvals)
            }

def output_stats(dct, df):
    y_pred = dct['slope']*dct['xvals']+dct['intercept']
    STEYX = (((np.array(df['average'])-y_pred)**2).sum()/(dct['count']-2))**0.5
    SSX = sum((x-dct['x_bar'])** 2 for x in dct['xvals'])
    dof = len(dct['xvals']) - 2
    alpha = 0.05
    tinv = t.ppf(1-alpha, dof)
    # calculate CI
    CI = tinv*STEYX*np.sqrt(1/dct['count'] + ((dct['xvals'] - dct['x_bar'])**2)/SSX)
    y_plusCI = (dct["slope"]*dct['xvals']+dct['intercept']) + CI
    y_minusCI = (dct["slope"]*dct['xvals']+dct['intercept']) - CI
    fit_lowerCI = np.polyfit(dct['xvals'],y_minusCI,deg=1)
    slope_lowerCI = fit_lowerCI[0]
    intercept_lowerCI = fit_lowerCI[1]
    return {
            'STEYX': STEYX,
            'SSX': SSX,
            'tinv': tinv,
            'dof': dof,
            'y_pred': y_pred,
            'CI': CI,
            'y_plusCI': y_plusCI,
            'y_minusCI': y_minusCI,
            'fit_lowerCI': fit_lowerCI,
            'slope_lowerCI': slope_lowerCI,
            'intercept_lowerCI': intercept_lowerCI
            }

def create_regr_plot(df, dct, wd):
    # regression plot
    fig, ax = plt.subplots(figsize=(10,7))
    for i,col in enumerate(df.columns):
            data_y = df[col].round(2)
            ax.plot(dct['xvals'],
                    data_y,
                    label = f'{col} ng' if col != 'average' else col,
                    marker='o',
                    linestyle="None")
    # slope line
    ax.plot(dct['xvals'],
            dct['slope']*dct['xvals']+dct['intercept'],
            linestyle='dotted',
            label='slope')
    # confidence interval
    ax.plot(dct['xvals'],
            dct['y_plusCI'],
            linestyle='solid',
            color='#2471A3',
            label='CI')
    ax.plot(dct['xvals'],
            dct['y_minusCI'],
            linestyle='solid',
            color='#2471A3')

    ax.set_title('% of 4C Reference MFI')
    ax.set_xlabel('Time (years)')
    ax.set_ylabel('% of 4C Ref. MFI')

    # Shrink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    # Put a legend to the right of the current axis
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    xypos = (3.8, 145)
    ax.annotate('y = {:.4g}x + {:.4g}\nR^2 = {:.3g}'.format(round(dct['slope'],2),
                                                    round(dct['intercept'],2),
                                                    round(dct['r_squared'],3)),
                xy=xypos,
                xytext=xypos)
    plt.savefig(os.path.join(wd, 'regression.png'),
                format='png',
                bbox_inches='tight')
