FILE = "Data/mu_m_2549.csv"  # machine_usage.csv
NET_IN = False
"""
machine_usage.csv format:
+------------------------------------------------------------------------------------------+
| Field            | Type       | Label | Comment                                          |
+------------------------------------------------------------------------------------------+
| machine_id       | string     |       | uid of machine                                   |
| time_stamp       | double     |       | time stamp, in second                            |
| cpu_util_percent | bigint     |       | [0, 100]                                         |
| mem_util_percent | bigint     |       | [0, 100]                                         |
| mem_gps          | double     |       |  normalized memory bandwidth, [0, 100]           |
| mkpi             | bigint     |       |  cache miss per thousand instruction             |
| net_in           | double     |       |  normarlized in coming network traffic, [0, 100] |
| net_out          | double     |       |  normarlized out going network traffic, [0, 100] |
| disk_io_percent  | double     |       |  [0, 100], abnormal values are of -1 or 101      |
+------------------------------------------------------------------------------------------+
"""
import numpy as np
infile = open(FILE, 'r')

pkg_nums = {}
for line in infile:
    #We want to average the utilization over the course of the given second
    machine_id, time_stamp, cpu_util_percent, mem_util_percent, mem_gps, mkpi, net_in, net_out, disk_io_percent = line.strip().split(",")
    time_stamp = float(time_stamp)
    net_traffic = net_in if NET_IN else net_out
    if net_traffic:
        net_traffic = float(net_traffic)
        if net_traffic < 0 or net_traffic > 100: 
            continue
        pkg_nums[time_stamp] = net_traffic

pkg_nums = sorted(pkg_nums.items())
out_list = []
for i in range(len(pkg_nums) - 1):
    x, y = pkg_nums[i], pkg_nums[i + 1]
    t1, n1 = x
    t2, n2 = y
    print(t1, (n2-n1) / (t2-t1))
    out_list.append((n2-n1) / (t2-t1))

out_list = (np.array(out_list) / max(out_list) * 100).tolist()

outfile = open("ali_machine_usage.dat", 'w')
print(",".join(map(str, out_list)),file=outfile)
outfile.close()
infile.close()
