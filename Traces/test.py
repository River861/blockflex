IN_FILE = "Data/machine_usage.csv"
DO_STAGE_ONE = True
DO_STAGE_TWO = True
DO_STAGE_THREE = True
OUT_FILE = "Results/avg_tpt_util.pdf"

import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os
import numpy as np

# {machine_id: {time_stamp: net_io}}
trace_map = {}
if DO_STAGE_ONE:
    with open(IN_FILE, 'r') as infile:
        for line in infile:
            machine_id, time_stamp, cpu_util_percent, mem_util_percent, mem_gps, mkpi, net_in, net_out, disk_io_percent = line.strip().split(",")
            time_stamp = float(time_stamp)
            # if int(time_stamp) % 100 != 0:
            #     continue
            if net_in and net_out:
                net_traffic = float(net_in) + float(net_out)
                if net_traffic < 0 or net_traffic > 100: 
                    continue
                if machine_id not in trace_map:
                    trace_map[machine_id] = {}
                trace_map[machine_id][time_stamp] = net_traffic

    with open("stage_1.dat", 'w') as f:
        for machine_id, trace in trace_map.items():
            print(f"{machine_id}\t{','.join(map(str, trace.keys()))}\t{','.join(map(str, trace.values()))}",file=f)
    print('stage 1 done.')
else:
    with open("stage_1.dat", 'r') as f:
        for line in f:
            machine_id, keys, values = line.strip().split("\t")
            trace_map[machine_id] = dict(zip(map(float, keys.strip().split(',')), map(float, values.strip().split(','))))


# {machine_id: {time_stamp: normalized_tpt}}
tpt_map = {}
if DO_STAGE_TWO:
    for machine_id, trace in trace_map.items():
        ts = list(trace.keys())
        pkgs = list(trace.values())
        tpts = []
        max_tpt = 0
        for i in range(len(pkgs)-1):
            tpt = (pkgs[i + 1] - pkgs[i]) / (ts[i + 1] - ts[i])
            tpts.append(tpt)
            max_tpt = max(max_tpt, tpt)
        tpt_map[machine_id] = dict(zip(ts[:-1], map(lambda x : x / max_tpt * 100 if max_tpt else 0, tpts)))

    with open("stage_2.dat", 'w') as f:
        for machine_id, trace in tpt_map.items():
            print(f"{machine_id}\t{','.join(map(str, trace.keys()))}\t{','.join(map(str, trace.values()))}",file=f)
    print('stage 2 done.')
else:
    with open("stage_2.dat", 'r') as f:
        for line in f:
            machine_id, keys, values = line.strip().split("\t")
            tpt_map[machine_id] = dict(zip(map(float, keys.strip().split(',')), map(float, values.strip().split(','))))

# {time_stamp : avg_tpt}
avg_trace = {}
if DO_STAGE_THREE:
    cnt = {}
    for machine_id, temp in tpt_map.items():
        for t, tpt in temp.items():
            if t not in avg_trace:
                avg_trace[t], cnt[t] = 0, 0
            avg_trace[t] += tpt
            cnt[t] += 1
    for t in avg_trace.keys():
        avg_trace[t] /= cnt[t]

    with open("stage_3.dat", 'w') as f:
        print(f"{','.join(map(str, avg_trace.keys()))}\t{','.join(map(str, avg_trace.values()))}",file=f)
    print('stage 3 done.')
else:
    with open("stage_3.dat", 'r') as f:
        data = f.readlines()
        keys, values = data[0].strip().split("\t")
        avg_trace = dict(zip(map(float, keys.strip().split(',')), map(float, values.strip().split(','))))

# ----------------------------------------------------------------------------

# plot
avg_trace = sorted(avg_trace.items())
x_data, y_data = zip(*avg_trace)

Figure = plt.figure(figsize=(3,2))
Graph = Figure.add_subplot(111)
PDF = PdfPages(OUT_FILE)

plt.plot(x_data, y_data, linewidth=0.5)

YLabel = plt.ylabel("Tpt (%)", multialignment='center', fontsize=12)
YLabel.set_position((0.0,0.5))
YLabel.set_linespacing(0.5)

#Want the labels to be days, and the increments are on a 10s basis (hence 360 not 3600)
Xticks = np.arange(0,len(x_data),360*24)
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

Graph.set_xlim(0, len(x_data))
Graph.set_ylim((0, 100))

PDF.savefig(Figure, bbox_inches='tight')

PDF.close()
