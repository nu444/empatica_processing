import sys
import matplotlib.pyplot as plt
from empatica_processing import *

# use command line paramter as source file, fallback to demo file
if len(sys.argv) >= 2:
    source = sys.argv[1]
else:
    source = './1731504447_A0370B/HR.csv'

# Filter requirements.
T = 5.0         # Sample Period
fs = 1.0       # sample rate, Hz
cutoff = 0.06      # desired cutoff frequency of the filter, Hz
nyq = 0.5 * fs  # Nyquist Frequency
order = 2       # sin wave can be approx represented as quadratic
n = int(T * fs) # total number of samples

fig, axs = plt.subplots(2)

# Processing settings
marked_percentile = 30
marked_is_maximum = True


with open(source) as csvfile:
    reader = csv.reader(csvfile, delimiter = ',')
    hr = [row[0] for row in reader]
    hr = extract_measurement_numericals(hr, 2, 5)
    filtered = butter_lowpass_filter(hr, cutoff, fs, order)
    stronglyFiltered = butter_lowpass_filter(hr, cutoff / 3.0, fs, order)
    axs[0].plot(filtered)
    axs[0].plot(stronglyFiltered)
    axs[0].set_title("Heart Rate")
    plt.figtext(0.01, 0.01, "Sample Rate "+ str(fs)+ "Hz | Blue boxes: "+ ("top" if  marked_is_maximum else "bottom") + " " + str(marked_percentile) + "th Percentile")
    axs[0].plot(hr)
    plot_extreme_intervals(hr, axs[0], percentile(hr, marked_percentile), True)

    # derivative on second plot
    derivative = rate_of_change(hr)
    filteredDer1 = butter_lowpass_filter(derivative, cutoff, fs, order)
    filteredDer2 = butter_lowpass_filter(derivative, cutoff / 3.0, fs, order)
    axs[1].plot(derivative)
    axs[1].plot(filteredDer1)
    axs[1].plot(filteredDer2)
    axs[1].set_title("Derivative")
    mark_faulty_values(derivative, axs[1], 10, 5)
    plt.show()