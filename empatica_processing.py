import csv
import numpy as np
from scipy.signal import butter, filtfilt
from matplotlib.patches import Rectangle

def butter_lowpass_filter(data, cutoff, fs, order):
    normal_cutoff = cutoff / fs * 0.5
    # Get the filter coefficients
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data)
    return y

def draw_interval(start, end, data, ax, draw_color):
    height = (max(data) - min(data))
    height_padded = height * 1.1
    bottom = min(data) - ((height_padded - height) / 2)
    label_offset = height/30
    ax.add_patch(Rectangle((start, bottom), end - start, height_padded, color=draw_color, alpha=.2))
    ax.plot(start, bottom + height_padded, marker = 7, color=draw_color)
    ax.plot(end, bottom, marker = 6, color=draw_color)
    ax.text(start, bottom + height_padded + label_offset, start)
    ax.text(end, bottom, end)

def rate_of_change(data):
    out = []
    for i in range(1, len(data)):
        out.append(abs(data[i]-data[i-1]))
    return out

def mark_faulty_values(data, ax, rejection_factor, lookahead):
    start = -1
    der = rate_of_change(data)
    der_median = np.median(der)
    thresh = der_median * rejection_factor
    with open('faulty.csv', 'w', newline='') as csv_output:
        fieldnames = ['start', 'end']
        writer = csv.DictWriter(csv_output, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(0, len(der)):
            does_satisfy = (der[i] > thresh) if start == -1 else (der[i] > (thresh / 2.0))
            if does_satisfy:
                if start == -1:
                    start = i
            elif start != -1:
                next_interval_found = False
                for l in range(i+1, i + lookahead):
                    if der[min(l, len(der)-1)] > thresh:
                        next_interval_found = True
                        i = l + 1
                if not next_interval_found:
                    draw_interval(start-1, i, data, ax, 'red')
                    writer.writerow({'start': start, 'end': i})
                    start = -1

def plot_extreme_intervals(data, ax, thresh, is_maximum):
    ax.axhline(y = thresh, color = 'b', alpha=.2, linestyle = '--', lw=1)
    start = -1

    with open('intervals.csv', 'w', newline='') as csv_output:
        fieldnames = ['start', 'end']
        writer = csv.DictWriter(csv_output, fieldnames=fieldnames)
        writer.writeheader()

        for i, val in enumerate(data, start=0):
            does_satisfy = val > thresh  if is_maximum else val < thresh
            if does_satisfy:
                if start == -1:
                    start = i
            elif start != -1:
                draw_interval(start, i, data, ax, 'blue')
                writer.writerow({'start': start, 'end': i})
                start = -1

def percentile(data, percent):
    sorted_data = data.copy()
    sorted_data.sort()
    return sorted_data[int(len(sorted_data) * (100-percent) / 100)]

def extract_measurement_numericals(data, thresh_deviance, thresh_interval):
    without_header = data[1:len(data)]
    data = [float(val) for val in without_header]

    # drop faulty values on startup
    begin = 0
    done = False
    index = 1
    satisfied_range = 0
    while not done:
        div = abs(data[index] - data[index-1])
        if div < thresh_deviance:
            satisfied_range += 1
            if satisfied_range > thresh_interval:
                begin = index
                done = True
        else:
            satisfied_range = 0
        index += 1
        if index >= len(data):
            begin = len(data)-1
            done = True

    return data[begin:len(data)]