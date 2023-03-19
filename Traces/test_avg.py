VM_TRACE = True
DO_STAGE_ONE = True
DO_STAGE_TWO = True
DO_STAGE_THREE = True
TIMESTAMP_RANGE = (2 * 3600*24, 8 * 3600*24)


IN_FILE = "Data/container_usage.csv" if VM_TRACE else "Data/machine_usage.csv"
STAGE_ONE_FILE = f"Temp/{'vm' if VM_TRACE else 'server'}_stage_1.dat"
STAGE_TWO_FILE = f"Temp/{'vm' if VM_TRACE else 'server'}_stage_2.dat"
STAGE_THREE_FILE = f"Temp/{'vm' if VM_TRACE else 'server'}_stage_3.dat"
OUT_FILE = f"Results/{'vm' if VM_TRACE else 'server'}_avg_tpt_util.pdf"


import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os
import numpy as np

# {m_id: {time_stamp: net_io}}
trace_map = {}
if DO_STAGE_ONE:
    with open(IN_FILE, 'r') as infile:
        for line in infile:
            if VM_TRACE:
                m_id, server_id, time_stamp, _, _, _, _, _, net_in, net_out, _ = line.strip().split(",")
                if not m_id:
                    m_id = server_id
            else:
                m_id, time_stamp, _, _, _, _, net_in, net_out, _ = line.strip().split(",")
            time_stamp = float(time_stamp)
            if time_stamp < TIMESTAMP_RANGE[0] or time_stamp > TIMESTAMP_RANGE[1]:
                continue
            if net_in and net_out:
                net_traffic = float(net_in) + float(net_out)
                if net_traffic < 0:
                    continue
                if m_id not in trace_map:
                    trace_map[m_id] = {}
                trace_map[m_id][time_stamp] = net_traffic

    with open(STAGE_ONE_FILE, 'w') as f:
        for m_id, trace in trace_map.items():
            print(f"{m_id}\t{','.join(map(str, trace.keys()))}\t{','.join(map(str, trace.values()))}",file=f)
    print('stage 1 done.')
elif DO_STAGE_TWO:
    with open(STAGE_ONE_FILE, 'r') as f:
        for line in f.readlines():
            m_id, keys, values = line.strip().split("\t")
            trace_map[m_id] = dict(zip(map(float, keys.strip().split(',')), map(float, values.strip().split(','))))


# {m_id: {time_stamp: percentaged_tpt}}
tpt_map = {}
if DO_STAGE_TWO:
    for m_id, trace in trace_map.items():
        ts = list(trace.keys())
        pkgs = list(trace.values())
        if len(pkgs) < 2:
            continue
        tpts = []
        max_tpt = 0
        for i in range(len(pkgs)-1):
            tpt = abs(pkgs[i + 1] - pkgs[i]) / (ts[i + 1] - ts[i])
            tpts.append(tpt)
            max_tpt = max(max_tpt, tpt)
        tpt_map[m_id] = dict(zip(ts[:-1], map(lambda x : x / max_tpt * 100 if max_tpt else 0, tpts)))

    with open(STAGE_TWO_FILE, 'w') as f:
        for m_id, trace in tpt_map.items():
            print(f"{m_id}\t{','.join(map(str, trace.keys()))}\t{','.join(map(str, trace.values()))}",file=f)
    print('stage 2 done.')
elif DO_STAGE_THREE:
    with open(STAGE_TWO_FILE, 'r') as f:
        for line in f.readlines():
            m_id, keys, values = line.strip().split("\t")
            tpt_map[m_id] = dict(zip(map(float, keys.strip().split(',')), map(float, values.strip().split(','))))

# {time_stamp : avg_tpt}
avg_trace = {}
if DO_STAGE_THREE:
    cnt = {}
    for m_id, temp in tpt_map.items():
        for t, tpt in temp.items():
            if t not in avg_trace:
                avg_trace[t], cnt[t] = 0, 0
            avg_trace[t] += tpt
            cnt[t] += 1
    for t in avg_trace.keys():
        avg_trace[t] /= cnt[t]

    with open(STAGE_THREE_FILE, 'w') as f:
        print(f"{','.join(map(str, avg_trace.keys()))}\t{','.join(map(str, avg_trace.values()))}",file=f)
    print('stage 3 done.')
else:
    with open(STAGE_THREE_FILE, 'r') as f:
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

off = TIMESTAMP_RANGE[0]  # min(x_data)
x_data = list(map(lambda x : x - off, x_data))

plt.plot(x_data, y_data, linewidth=0.5)

YLabel = plt.ylabel("IOPS Util (%)", multialignment='center', fontsize=12)
YLabel.set_position((0.0,0.5))
YLabel.set_linespacing(0.5)

#Want the labels to be days, and the increments are on a 10s basis (hence 360 not 3600)
Xticks = np.arange(0,x_data[-1],3600*24)
Graph.set_xticks(Xticks)
Graph.set_xticklabels(['0','1','2','3','4','5'],fontsize=11)
Graph.xaxis.set_ticks_position('none')
Graph.set_xlabel('Time (days)', fontsize=14)
# Graph.set_xlabel('Time (seconds)', fontsize=14)

YTicks = np.arange(0,6,1)
Graph.set_yticks(YTicks)
Graph.set_yticklabels(['0', '1', '2', '3', '4', '5'], fontsize=11)
Graph.yaxis.set_ticks_position('none')

Graph.set_axisbelow(True)
Graph.yaxis.grid(color='lightgrey', linestyle='solid')

Graph.grid(b=True, which='minor')

Graph.set_xlim(0, x_data[-1])
Graph.set_ylim((0, 6))

PDF.savefig(Figure, bbox_inches='tight')

PDF.close()
