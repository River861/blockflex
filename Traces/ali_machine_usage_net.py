#!/usr/bin/python3
NET_IN = False

import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import os


#Collect data
x_values = []
y_values = []
with open("ali_machine_usage.dat", 'r') as f:
    data = f.readlines()
    y_values = list(map(float, data[0].split(",")))
    x_values = np.arange(len(data[0].split(",")))

Figure = plt.figure(figsize=(3,2))
Graph = Figure.add_subplot(111)
PDF = PdfPages(f"Results/ali_machine_usage_{'net_in' if NET_IN else 'net_out'}.pdf")

plt.plot(x_values, y_values, '-c', label="avg")

YLabel = plt.ylabel("Tpt (%)", multialignment='center', fontsize=12)
YLabel.set_position((0.0,0.5))
YLabel.set_linespacing(0.5)

#Want the labels to be days, and the increments are on a 10s basis (hence 360 not 3600)
Xticks = np.arange(0,len(x_values),360*24)
# Graph.set_xticks(Xticks)
# Graph.set_xticklabels(['0','1','2','3','4','5','6','7'],fontsize=11)
Graph.xaxis.set_ticks_position('none')
# Graph.set_xlabel('Time (days)', fontsize=14)
Graph.set_xlabel('Time (seconds)', fontsize=14)

YTicks = np.arange(0,100,10)
Graph.set_yticks(YTicks)
Graph.set_yticklabels(['0', '10', '20', '30', '40', '50', '60', '70', '80', '90'], fontsize=11)
Graph.yaxis.set_ticks_position('none')

Graph.set_axisbelow(True)
Graph.yaxis.grid(color='lightgrey', linestyle='solid')

Graph.grid(b=True, which='minor')

Graph.set_xlim(0, len(x_values))
Graph.set_ylim((0, 100))

PDF.savefig(Figure, bbox_inches='tight')

PDF.close()
