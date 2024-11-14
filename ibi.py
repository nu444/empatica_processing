import sys
import matplotlib.pyplot as plt
from empatica_processing import *

# use command line paramter as source file, fallback to demo file
if len(sys.argv) >= 2:
    source = sys.argv[1]
else:
    source = './1731504447_A0370B/IBI.csv'

# Filter requirements.
T = 5.0         # Sample Period
fs = 30.0       # sample rate, Hz
cutoff = 10      # desired cutoff frequency of the filter, Hz ,      slightly higher than actual 1.2 Hz
nyq = 0.5 * fs  # Nyquist Frequency
order = 2       # sin wave can be approx represented as quadratic
n = int(T * fs) # total number of samples

fig, axs = plt.subplots(2)

with open('./1731585548_A0370B/IBI.csv') as csvfile:
    reader = csv.reader(csvfile, delimiter = ',')
    hrv = [row[1] for row in reader]
    hrv = extract_measurement_numericals(hrv, 2, 5)
    filtered = butter_lowpass_filter(hrv, cutoff, fs, order)
    stronglyFiltered = butter_lowpass_filter(hrv, cutoff / 3.0, fs, order)
    axs[0].plot(filtered)
    axs[0].plot(stronglyFiltered)
    axs[0].set_title("Interbeat Intervals")
    axs[0].plot(hrv)

    # derivative
    derivative = rate_of_change(hrv)
    filteredDer1 = butter_lowpass_filter(derivative, cutoff, fs, order)
    filteredDer2 = butter_lowpass_filter(derivative, cutoff / 3, fs, order)
    axs[1].plot(derivative)
    axs[1].plot(filteredDer1)
    axs[1].plot(filteredDer2)
    axs[1].set_title("Derivative")
    plt.show()