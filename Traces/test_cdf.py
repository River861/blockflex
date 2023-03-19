VM_TRACE = False
DO_STAGE_FOUR = True

IN_FILE = f"Temp/{'vm' if VM_TRACE else 'server'}_stage_2.dat"
STAGE_FOUR_FILE = f"Temp/{'vm' if VM_TRACE else 'server'}_stage_4.dat"
OUT_FILE = f"Results/{'vm' if VM_TRACE else 'server'}_cdf_tpt_util.pdf"

import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os
import numpy as np

x_data = [i for i in range(101)]
cdf = []

if DO_STAGE_FOUR:
    # {machine_id: {time_stamp: percentaged_tpt}}
    tpt_map = {}
    with open(IN_FILE, 'r') as f:
        for line in f.readlines():
            machine_id, keys, values = line.strip().split("\t")
            tpt_map[machine_id] = dict(zip(map(float, keys.strip().split(',')), map(float, values.strip().split(','))))

    # tpt lists
    tpts = []
    for machine_id, trace in tpt_map.items():
        tpts += list(trace.values())

    tpts.sort()
    tpts.reverse()

    # max/min/avg_cdf: min(tpts)
    cdf = [tpts[int(len(tpts) * i / 100)] for i in range(100)] + [tpts[-1]]

    with open(STAGE_FOUR_FILE, 'w') as f:
        print(','.join(map(str, cdf)),file=f)
    print('stage 4 done.')

else:
    with open(STAGE_FOUR_FILE, 'r') as f:
        data = f.readlines()
        cdf = data[0].strip()
        cdf = list(map(float, cdf.strip().split(',')))


# ----------------------------------------------------------------------------

# plot
# plt.rcParams.update({'font.family': 'serif'})

Figure = plt.figure(figsize=(2.8,0.9))
Graph = Figure.add_subplot(111)
PDF = PdfPages(OUT_FILE)

x_data = np.array(x_data) / 100
cdf = np.array(cdf) / 100

plt.plot(x_data, cdf, '--', label='cdf', color='blue',linewidth=1)

labels = ['0', '', '20','', '40', '', '60', '', '80', '', '100']

YLabel = plt.ylabel("IOPS Util (%)", multialignment='center', fontsize=7)
YLabel.set_position((0.0,0.5))
YLabel.set_linespacing(0.5)

#Want the labels to be days, and the increments are on a 10s basis (hence 360 not 3600)
Xticks = np.arange(0, 1.1, 0.1)
Graph.set_xticks(Xticks)
Graph.set_xticklabels(labels,fontsize=7)
Graph.xaxis.set_ticks_position('none')
Graph.set_xlabel(f'Percentage of {"VMs" if VM_TRACE else "Servers"} X Timestamps (%)', fontsize=7)

YTicks = Xticks
Graph.set_yticks(YTicks)
Graph.set_yticklabels(labels,fontsize=7)
Graph.yaxis.set_ticks_position('none')

Graph.set_axisbelow(True)
Graph.yaxis.grid(color='lightgrey', linestyle='solid')

lg = Graph.legend(loc='upper right', prop={'size':7}, ncol=1, borderaxespad=0.2)
lg.draw_frame(False)

Graph.grid(b=True, which='both')

Graph.set_xlim((0,0.3))
Graph.set_ylim((0,1))
plt.margins(0)

PDF.savefig(Figure, bbox_inches='tight')
PDF.close()



# max_cdf, avg_cdf, min_cdf = [], [], []

# if DO_STAGE_FOUR:
#     # {machine_id: {time_stamp: percentaged_tpt}}
#     tpt_map = {}
#     with open(IN_FILE, 'r') as f:
#         for line in f:
#             machine_id, keys, values = line.strip().split("\t")
#             tpt_map[machine_id] = dict(zip(map(float, keys.strip().split(',')), map(float, values.strip().split(','))))

#     # tpt lists
#     max_tpts, avg_tpts, min_tpts = [], [], []
#     for machine_id, trace in tpt_map.items():
#         tpts = trace.values()
#         max_tpts.append(max(tpts))
#         avg_tpts.append(sum(tpts) / len(tpts))
#         min_tpts.append(min(tpts))

#     max_tpts.sort()
#     max_tpts.reverse()
#     avg_tpts.sort()
#     avg_tpts.reverse()
#     min_tpts.sort()
#     min_tpts.reverse()

#     # max/min/avg_cdf: min(tpts)
#     max_cdf = [max_tpts[int(len(max_tpts) * i / 100)] for i in range(100)] + [max_tpts[-1]]
#     avg_cdf = [avg_tpts[int(len(avg_tpts) * i / 100)] for i in range(100)] + [avg_tpts[-1]]
#     min_cdf = [min_tpts[int(len(min_tpts) * i / 100)] for i in range(100)] + [min_tpts[-1]]

#     with open(STAGE_FOUR_FILE, 'w') as f:
#         print(f"{','.join(map(str, max_cdf))}\t{','.join(map(str, avg_cdf))}\t{','.join(map(str, min_cdf))}",file=f)
#     print('stage 4 done.')

# else:
#     with open(STAGE_FOUR_FILE, 'r') as f:
#         data = f.readlines()
#         max_cdf, avg_cdf, min_cdf = data[0].strip().split("\t")
#         max_cdf = list(map(float, max_cdf.strip().split(',')))
#         avg_cdf = list(map(float, avg_cdf.strip().split(',')))
#         min_cdf = list(map(float, min_cdf.strip().split(',')))

# # ----------------------------------------------------------------------------

# # plot
# plt.rcParams.update({'font.family': 'serif'})

# Figure = plt.figure(figsize=(2.8,0.9))
# Graph = Figure.add_subplot(111)
# PDF = PdfPages(OUT_FILE)

# x_data = np.array(x_data) / 100
# max_cdf = np.array(max_cdf) / 100
# avg_cdf = np.array(avg_cdf) / 100
# min_cdf = np.array(min_cdf) / 100

# plt.plot(x_data, max_cdf, '-', label="Maximum",color='red',linewidth=2)
# plt.plot(x_data, avg_cdf, '--', label="Average",color='blue',linewidth=1)
# plt.plot(x_data, min_cdf, ':' ,label="Minimum",color='green',linewidth=2)

# labels = ['0', '', '20','', '40', '', '60', '', '80', '', '100']

# YLabel = plt.ylabel("IOPS Util (%)", multialignment='center', fontsize=7)
# YLabel.set_position((0.0,0.5))
# YLabel.set_linespacing(0.5)

# #Want the labels to be days, and the increments are on a 10s basis (hence 360 not 3600)
# Xticks = np.arange(0, 1.1, 0.1)
# Graph.set_xticks(Xticks)
# Graph.set_xticklabels(labels,fontsize=7)
# Graph.xaxis.set_ticks_position('none')
# Graph.set_xlabel('Percentage of Servers (%)', fontsize=7)

# YTicks = Xticks
# Graph.set_yticks(YTicks)
# Graph.set_yticklabels(labels,fontsize=7)
# Graph.yaxis.set_ticks_position('none')

# Graph.set_axisbelow(True)
# Graph.yaxis.grid(color='lightgrey', linestyle='solid')

# lg = Graph.legend(loc='upper right', prop={'size':7}, ncol=1, borderaxespad=0.2)
# lg.draw_frame(False)

# Graph.grid(b=True, which='both')

# Graph.set_xlim((0,1))
# Graph.set_ylim((0,1))
# plt.margins(0)

# PDF.savefig(Figure, bbox_inches='tight')
# PDF.close()