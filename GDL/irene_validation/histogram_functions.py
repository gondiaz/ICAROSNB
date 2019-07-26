import numpy             as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors

def histo1D(*args, **kwargs):

    """
    Function to plot 1D histograms

    Arguments:
    Numpy arrays with the data to be histogramed

    Kwargs:
    xlabel:str. Label in the x axis.
    bins  : histogram binning, it can be in any
    allowed form by numpy.histogram function.
    scale :str. y scale of the histogram plot,
    it can be any matplotlib allowed scale.
    xlims :two value list. x limits on data
    ylimis:two value list. y limits in the histogram plot
    Bbox  :bool. Plot box with histogram info
    Label[number]: str. Label to be given to data
    inserted as [number] argument
    eps: float between 0 and 1. Sets the distance
    between histogram edges and axes edges

    """

    #Default histogram parameters
    params = {"xlabel": 'X',
              "bins":   10,
              "scale": 'linear',
              "xlims": [None, None],
              "ylims": [0   , None],
              "Bbox" : True,
              "normalize": False}

    for i in range(0, len(args)):
        params[f"Label{i}"] = f"Label{i}"

    #KWARGS
    for k, v in kwargs.items():
        if k in params: params[k] = v
        else: raise Exception(f"{k} is not an allowed kwarg")

    #CREATE THE FIGURE AND AXES
    fig = plt.figure(figsize=[10, 5])
    ax  = fig.add_subplot(111)

    #ARGS
    mins, maxs = [], []
    for arg in args:
        mins.append(np.min(arg))
        maxs.append(np.max(arg))
    xmin, xmax = np.min(mins), np.max(maxs)

    nplots = 4
    exception = f"For clarity, up to {nplots} plots are not allowed if Bbox is True"
    if len(args)>nplots and params["Bbox"] is True:
        raise Exception(exception)

    colors = ['b', 'r', 'c', 'm', 'y', 'k']

    for i, arg in enumerate(args):
        data = arg
        N    = len(data)

        #SET X LIMITS
        if params["xlims"][0] is None:
            nl = 0
            params["xlims"][0] = xmin
        else:
            data = data[data>=params["xlims"][0]]
            nl   = N-len(data)
            xmin = params["xlims"][0]

        if params["xlims"][1] is None:
            nu = 0
            params["xlims"][1] = xmax
        else:
            data = data[data<=params["xlims"][1]] ## note the less equal, not less
            nu   = N-len(data)
            xmax = params["xlims"][1]

        #HISTOGRAM THE DATA
        hist, edges = np.histogram(data, bins=params["bins"], range=(xmin, xmax))
        hist           = np.append(hist, 0)
        params["bins"] = edges

        H = hist
        if params["normalize"]: H = H / H.sum()

        ax.step(edges, H, where = 'post'       , linewidth = 1, color = colors[i], label=params[f"Label{i}"])
        ax.plot([edges[0], edges[0]], [0, H[0]], linewidth = 1, color = colors[i])

        #BOUNDING BOX
        if params["Bbox"] is True:
            l0 =  " {} \n".format(params[f"Label{i}"])
            l1 = f" Entries: {hist.sum()} \n"
            l2 = f" Out: [{int(nl/N*100)}, {int(nu/N*100)}] % \n"
            l3 = f" Total out: {int((1-hist.sum()/N)*100)} %"

            s  = l0 + l1 + l2 + l3

            bbox = dict(fc='white', color=colors[i])
            ax.text(0.9, 0.8 - i*0.25, s=s,
                    bbox=bbox,
                    transform=ax.transAxes,
                    fontsize = 8)

    # SET HISTOGRAM SCALE
    ax.set_yscale(params["scale"])

    #PLOT LABELS
    ax.set_xlabel(params["xlabel"])
    ax.set_ylabel('Entries')

    #PLOT LEGEND
    if params["Bbox"] is False:
        ax.legend()

    # PLOT XY LIMITS
    if params["scale"] is 'linear':
        ax.set_ylim(params["ylims"])

    if params["scale"] is 'log':
        if params["ylims"][0] is None: params["ylims"][0] = 10**(-1)
        if params["ylims"][0]==0     : params["ylims"][0] = 10**(-1)
        if params["ylims"][0]<0      : raise Exception("Y lower limit is not valid for log scale")
        ax.set_ylim(params["ylims"])

    eps = 0.03
    l = params["xlims"][0]-(params["xlims"][1]-params["xlims"][0])*eps
    u = params["xlims"][1]+(params["xlims"][1]-params["xlims"][0])*eps
    ax.set_xlim([l, u])

    #FACECOLOR
    ax.set_facecolor("ghostwhite")

#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------


def histo2D(xdata, ydata, **kwargs):

    #AÑADIR WEIGTHS


    """
    Function to plot 2D histograms

    Arguments:
    xdata, ydata

    Kwargs:
    xlabel:str Label in the x axis.
    ylabel:str Label in the y axis
    bins  : histogram binning, it can be in any
    allowed form by numpy.histogram function.
    xlims :two value list x limits on xdata
    ylimis:two value list y limits on ydata
    cmap  :str or cmap type. Any matplotlib allowed cmap
    cbarlims: two value list minimum and maximum
    values for the cbar
    cmapscale: str. scale of the colormap,
    it can be 'linear' or 'log'.

    """

    #Default histogram parameters
    params = {"xlabel": 'X',
              "ylabel": 'Y',
              "bins":   10,
              "weights": None,
              "xlims": [None, None],
              "ylims": [None, None],
              "cmap" : 'Greys',
              "cmaplims": [None, None],
              "cmapscale": 'linear',
              "profile" : False}

    #KWARGS
    for k, v in kwargs.items():
        if k in params: params[k] = v
        else: raise Exception(f"{k} is not an allowed kwarg")

    #CREATE THE FIGURE AND AXES
    fig = plt.figure(figsize=[10, 5])
    ax  = fig.add_subplot(111)

    #xdata limits
    #lower
    if params["xlims"][0] is None:
        xmin = np.min(xdata)
        params["xlims"][0] = xmin
    else:
        sel = xdata>=params["xlims"][0]
        xdata = xdata[sel]
        ydata = ydata[sel]
        if params["weights"] is not None:
            params["weights"] = params["weights"][sel]
    #upper
    if params["xlims"][1] is None:
        xmax = np.max(xdata)
        params["xlims"][1] = xmax
    else:
        sel = xdata<params["xlims"][1]
        xdata = xdata[sel]
        ydata = ydata[sel]
        if params["weights"] is not None:
            params["weights"] = params["weights"][sel]

    #ydata limits
    #lower
    if params["ylims"][0] is None:
        ymin = np.min(ydata)
        params["ylims"][0] = ymin
    else:
        sel = ydata>=params["ylims"][0]
        xdata = xdata[sel]
        ydata = ydata[sel]
        if params["weights"] is not None:
            params["weights"] = params["weights"][sel]
    #upper
    if params["ylims"][1] is None:
        ymax = np.max(ydata)
        params["ylims"][1] = ymax
    else:
        sel = ydata<params["ylims"][1]
        xdata = xdata[sel]
        ydata = ydata[sel]
        if params["weights"] is not None:
            params["weights"] = params["weights"][sel]

    #2D HISTOGRAM
    H, xedg, yedg = np.histogram2d(xdata, ydata,
                                   bins  = params["bins"],
                                   range =[params["xlims"], params["ylims"]],
                                   weights = params["weights"])
    X, Y = np.meshgrid(xedg, yedg)

    #cmap scale
    if   params["cmapscale"] is 'linear': norm=colors.Normalize()
    elif params["cmapscale"] is 'log'   : norm=colors.LogNorm()
    else: raise Exception("cmapscale not allowed")

    pcm  = ax.pcolormesh(X, Y, H.T,
                        cmap=params["cmap"],
                        vmin = params["cmaplims"][0],
                        vmax = params["cmaplims"][1],
                        norm = norm)
    fig.colorbar(pcm, ax=ax)

    #XY LABELS
    ax.set_xlabel(params["xlabel"])
    ax.set_ylabel(params["ylabel"])

    #XY PLOT LIMITS
    eps = 0.03
    l = params["xlims"][0]-(params["xlims"][1]-params["xlims"][0])*eps
    u = params["xlims"][1]+(params["xlims"][1]-params["xlims"][0])*eps
    ax.set_xlim([l, u])

    l = params["ylims"][0]-(params["ylims"][1]-params["ylims"][0])*eps
    u = params["ylims"][1]+(params["ylims"][1]-params["ylims"][0])*eps
    ax.set_ylim([l, u])

    #FACECOLOR
    ax.set_facecolor("ghostwhite")


    #PROFILE
    if params["profile"]:
        X = (xedg[1:] + xedg[:-1])/2.
        Y = []
        for i in range(0, len(xedg)-1):
            sel = (xedg[i] <= xdata) & (xdata < xedg[i+1])

            if len(ydata[sel])>0: Y.append(ydata[sel].mean())
            else: Y.append(np.nan)

        ax.scatter(X, Y, s=10, color = "r")
