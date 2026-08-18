"""
Franck–Hertz Experiment
=======================

Analysis of experimental Franck–Hertz measurements.

The script:
    1. Loads voltage-current measurements at different temperatures,
       braking voltages, and resistances.
    2. Plots the experimental I-V curves.
    3. Analyzes hysteresis measurements.
    4. Fits the temperature dependence of the critical voltage.
    5. Detects consecutive minima in the current curves.
    6. Estimates the excitation energy of mercury atoms.
    7. Calculates the corresponding photon wavelength.

Author:
    Mathias Rendón Fernández
"""

# %%

# =============================================================================
# Imports
# =============================================================================

import os
from io import StringIO

import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.optimize import curve_fit
from scipy.signal import find_peaks


# =============================================================================
# Configuration
# =============================================================================

DATA_FOLDER = "MRF"


# =============================================================================
# Data Loading
# =============================================================================

def load_measurement(temperature, braking_voltage, resistance):
    """
    Load a standard Franck–Hertz measurement.

    Parameters
    ----------
    temperature : float
        Temperature of the Franck–Hertz tube in °C.
    braking_voltage : float
        Braking voltage in V.
    resistance : float
        Resistance in Ω.

    Returns
    -------
    voltage : ndarray
        Applied voltage in V.
    current : ndarray
        Measured current in nA.
    """
    filename = (
        f"{temperature} C, {braking_voltage} V, {resistance} O.txt"
    )
    filepath = os.path.join(DATA_FOLDER, filename)

    with open(filepath, encoding="latin1") as file:
        lines = file.readlines()

    # Remove the two-line header.
    data_lines = lines[2:]

    # Replace decimal commas with decimal points.
    data_lines = [line.replace(",", ".") for line in data_lines]

    data = np.loadtxt(
        StringIO("".join(data_lines)),
        delimiter="\t"
    )

    voltage = data[:, 0]
    current = data[:, 1]

    return voltage, current


def load_hysteresis_measurement(
    temperature,
    braking_voltage,
    resistance,
    measurement_type
):
    """
    Load a hysteresis Franck–Hertz measurement.

    Parameters
    ----------
    temperature : float
        Temperature of the Franck–Hertz tube in °C.
    braking_voltage : float
        Braking voltage in V.
    resistance : float
        Resistance in Ω.
    measurement_type : str
        Either "Increasing" or "Decreasing".

    Returns
    -------
    voltage : ndarray
        Applied voltage in V.
    current : ndarray
        Measured current in nA.
    """
    filename = (
        f"H {measurement_type}, "
        f"{temperature} C, "
        f"{braking_voltage} V, "
        f"{resistance} O.txt"
    )

    filepath = os.path.join(DATA_FOLDER, filename)

    with open(filepath, encoding="latin1") as file:
        lines = file.readlines()

    # Remove the two-line header.
    data_lines = lines[2:]

    # Replace decimal commas with decimal points.
    data_lines = [line.replace(",", ".") for line in data_lines]

    data = np.loadtxt(
        StringIO("".join(data_lines)),
        delimiter="\t"
    )

    voltage = data[:, 0]
    current = data[:, 1]

    return voltage, current


# =============================================================================
# Standard Measurements
# =============================================================================

measurement_config = {
    0: {
        5: [195, 235, 245, 280],
        15: [195, 220, 240, 285]
    },
    1.5: {
        5: [195, 225, 240, 280],
        15: [185, 220, 240, 280]
    },
    3: {
        5: [200, 220, 245, 280],
        15: [185, 225, 245, 275]
    }
}


measurements = {}

for braking_voltage in measurement_config:
    measurements[braking_voltage] = {}

    for resistance in measurement_config[braking_voltage]:
        measurements[braking_voltage][resistance] = {}

        for temperature in measurement_config[braking_voltage][resistance]:

            voltage, current = load_measurement(
                temperature,
                braking_voltage,
                resistance
            )

            measurements[braking_voltage][resistance][temperature] = (
                voltage,
                current
            )


# =============================================================================
# Plot Standard I-V Curves
# =============================================================================

for braking_voltage in measurements:
    for resistance in measurements[braking_voltage]:

        plt.figure()

        for temperature in measurements[braking_voltage][resistance]:

            voltage, current = measurements[
                braking_voltage
            ][resistance][temperature]

            plt.plot(
                voltage,
                current,
                label=f"{temperature} °C"
            )

        plt.xlabel("Applied Voltage (V)")
        plt.ylabel("Current (nA)")
        plt.title(
            f"Franck–Hertz Experiment\n"
            f"Braking Voltage = {braking_voltage} V, "
            f"R = {resistance} Ω"
        )

        plt.legend()
        plt.grid()
        plt.show()


# =============================================================================
# Hysteresis Measurements
# =============================================================================

hysteresis_config = {
    0: {
        5: [215, 250],
        10: [210, 260]
    },
    1.5: {
        5: [210, 255],
        10: [205, 250]
    }
}


hysteresis_data = {}

for braking_voltage in hysteresis_config:
    hysteresis_data[braking_voltage] = {}

    for resistance in hysteresis_config[braking_voltage]:
        hysteresis_data[braking_voltage][resistance] = {}

        for temperature in hysteresis_config[braking_voltage][resistance]:

            voltage_increasing, current_increasing = (
                load_hysteresis_measurement(
                    temperature,
                    braking_voltage,
                    resistance,
                    "Increasing"
                )
            )

            voltage_decreasing, current_decreasing = (
                load_hysteresis_measurement(
                    temperature,
                    braking_voltage,
                    resistance,
                    "Decreasing"
                )
            )

            hysteresis_data[braking_voltage][resistance][temperature] = {
                "Increasing": (
                    voltage_increasing,
                    current_increasing
                ),
                "Decreasing": (
                    voltage_decreasing,
                    current_decreasing
                )
            }


# =============================================================================
# Hysteresis Plotting
# =============================================================================

def plot_hysteresis_curve(
    voltage_increasing,
    current_increasing,
    voltage_decreasing,
    current_decreasing,
    color,
    temperature_label
):
    """
    Plot increasing and decreasing voltage sweeps and indicate
    their respective directions with arrows.
    """

    # Plot the two branches of the hysteresis curve.
    plt.plot(
        voltage_increasing,
        current_increasing,
        color=color,
        label=temperature_label
    )

    plt.plot(
        voltage_decreasing,
        current_decreasing,
        color=color
    )

    # -------------------------------------------------------------------------
    # Increasing-voltage arrow
    # -------------------------------------------------------------------------

    index = len(voltage_increasing) // 2

    if voltage_increasing[0] < voltage_increasing[-1]:
        x1 = voltage_increasing[index]
        y1 = current_increasing[index]

        x2 = voltage_increasing[index + 10]
        y2 = current_increasing[index + 10]

    else:
        x1 = voltage_increasing[index + 10]
        y1 = current_increasing[index + 10]

        x2 = voltage_increasing[index]
        y2 = current_increasing[index]

    plt.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops={
            "arrowstyle": "->",
            "color": "black",
            "linewidth": 2,
            "mutation_scale": 20
        }
    )

    # -------------------------------------------------------------------------
    # Decreasing-voltage arrow
    # -------------------------------------------------------------------------

    index = len(voltage_decreasing) // 2

    if voltage_decreasing[0] > voltage_decreasing[-1]:
        x1 = voltage_decreasing[index]
        y1 = current_decreasing[index]

        x2 = voltage_decreasing[index + 10]
        y2 = current_decreasing[index + 10]

    else:
        x1 = voltage_decreasing[index + 10]
        y1 = current_decreasing[index + 10]

        x2 = voltage_decreasing[index]
        y2 = current_decreasing[index]

    plt.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops={
            "arrowstyle": "->",
            "color": "black",
            "linewidth": 2,
            "mutation_scale": 20
        }
    )


# Zoom configuration for selected hysteresis plots.
zoom_config = {
    (0, 5): {
        "xlim": (2, 16),
        "ylim": (0.1, 1.8)
    },
    (0, 10): {
        "xlim": (2, 17),
        "ylim": (0.1, 0.85)
    },
    (1.5, 5): {
        "xlim": (2, 17),
        "ylim": (0.01, 0.42)
    },
    (1.5, 10): {
        "xlim": (2, 18),
        "ylim": (0.01, 0.2)
    }
}


for braking_voltage in hysteresis_data:
    for resistance in hysteresis_data[braking_voltage]:

        temperatures = list(
            hysteresis_data[braking_voltage][resistance].keys()
        )

        colors = ["C0", "C1"]

        # ---------------------------------------------------------------------
        # Full hysteresis plot
        # ---------------------------------------------------------------------

        plt.figure()

        for index, temperature in enumerate(temperatures):

            voltage_increasing, current_increasing = (
                hysteresis_data[
                    braking_voltage
                ][resistance][temperature]["Increasing"]
            )

            voltage_decreasing, current_decreasing = (
                hysteresis_data[
                    braking_voltage
                ][resistance][temperature]["Decreasing"]
            )

            plot_hysteresis_curve(
                voltage_increasing,
                current_increasing,
                voltage_decreasing,
                current_decreasing,
                color=colors[index],
                temperature_label=f"{temperature} °C"
            )

        plt.xlabel("Applied Voltage (V)")
        plt.ylabel("Current (nA)")
        plt.title(
            f"Hysteresis\n"
            f"Braking Voltage = {braking_voltage} V, "
            f"R = {resistance} Ω"
        )

        plt.legend(title="Temperature")
        plt.grid()
        plt.show()

        # ---------------------------------------------------------------------
        # Zoomed hysteresis plot
        # ---------------------------------------------------------------------

        plt.figure()

        for index, temperature in enumerate(temperatures):

            voltage_increasing, current_increasing = (
                hysteresis_data[
                    braking_voltage
                ][resistance][temperature]["Increasing"]
            )

            voltage_decreasing, current_decreasing = (
                hysteresis_data[
                    braking_voltage
                ][resistance][temperature]["Decreasing"]
            )

            plot_hysteresis_curve(
                voltage_increasing,
                current_increasing,
                voltage_decreasing,
                current_decreasing,
                color=colors[index],
                temperature_label=f"{temperature} °C"
            )

        config = zoom_config.get(
            (braking_voltage, resistance)
        )

        if config is not None:
            plt.xlim(*config["xlim"])
            plt.ylim(*config["ylim"])

        plt.xlabel("Applied Voltage (V)")
        plt.ylabel("Current (nA)")
        plt.title(
            f"Hysteresis — Zoomed\n"
            f"Braking Voltage = {braking_voltage} V, "
            f"R = {resistance} Ω"
        )

        plt.legend(title="Temperature")
        plt.grid()
        plt.show()


# =============================================================================
# Critical Voltage vs. Temperature
# =============================================================================

temperature_data = np.array(
    [185, 195, 205, 215, 225, 235, 245, 250],
    dtype=float
)

critical_voltage = np.array(
    [12.5, 14.2, 15.5, 20.4, 23.5, 31.4, 36.2, 41.8],
    dtype=float
)

# Measurement uncertainties.
temperature_uncertainty = 5       # °C
voltage_uncertainty = 0.1         # V


# -----------------------------------------------------------------------------
# Plot critical voltage as a function of temperature
# -----------------------------------------------------------------------------

plt.figure(figsize=(7, 5))

plt.errorbar(
    temperature_data,
    critical_voltage,
    xerr=temperature_uncertainty,
    yerr=voltage_uncertainty,
    fmt="o",
    color="C0",
    capsize=4,
    label="Experimental data"
)

plt.xlabel("Temperature (°C)")
plt.ylabel("Critical Voltage (V)")
plt.title("Critical Voltage vs. Temperature")
plt.grid(True)
plt.legend()
plt.show()


# -----------------------------------------------------------------------------
# Linear fit of log(V) vs. temperature
# -----------------------------------------------------------------------------

log_voltage = np.log(critical_voltage)

# Error propagation:
# σ_log(V) = σ_V / V
log_voltage_uncertainty = voltage_uncertainty / critical_voltage


def linear_model(temperature, slope, intercept):
    """Linear model: y = slope * temperature + intercept."""
    return slope * temperature + intercept


fit_parameters, covariance = curve_fit(
    linear_model,
    temperature_data,
    log_voltage,
    sigma=log_voltage_uncertainty,
    absolute_sigma=True
)

slope, intercept = fit_parameters

slope_uncertainty, intercept_uncertainty = np.sqrt(
    np.diag(covariance)
)


# -----------------------------------------------------------------------------
# Plot log(V) vs. temperature with linear fit
# -----------------------------------------------------------------------------

temperature_fit = np.linspace(
    temperature_data.min() - 5,
    temperature_data.max() + 5,
    200
)

log_voltage_fit = linear_model(
    temperature_fit,
    slope,
    intercept
)


plt.figure(figsize=(7, 5))

plt.errorbar(
    temperature_data,
    log_voltage,
    xerr=temperature_uncertainty,
    yerr=log_voltage_uncertainty,
    fmt="o",
    color="C1",
    capsize=4,
    label="Experimental data"
)

plt.plot(
    temperature_fit,
    log_voltage_fit,
    "-",
    color="black",
    label=(
        f"Fit: log(V) = "
        f"({slope:.3f} ± {slope_uncertainty:.3f})T + "
        f"({intercept:.3f} ± {intercept_uncertainty:.3f})"
    )
)

plt.xlabel("Temperature (°C)")
plt.ylabel("log(Critical Voltage)")
plt.title("Linear Fit of log(V) vs. Temperature")
plt.grid()
plt.legend()
plt.show()


# -----------------------------------------------------------------------------
# Print fit parameters
# -----------------------------------------------------------------------------

print("=" * 50)
print("Linear fit: log(V) = a·T + b")
print(f"a = {slope:.4f} ± {slope_uncertainty:.4f}")
print(f"b = {intercept:.4f} ± {intercept_uncertainty:.4f}")


# -----------------------------------------------------------------------------
# Calculate R²
# -----------------------------------------------------------------------------

log_voltage_fitted = linear_model(
    temperature_data,
    slope,
    intercept
)

residual_sum_of_squares = np.sum(
    (log_voltage - log_voltage_fitted) ** 2
)

total_sum_of_squares = np.sum(
    (log_voltage - np.mean(log_voltage)) ** 2
)

r_squared = (
    1
    - residual_sum_of_squares / total_sum_of_squares
)

print(f"R² = {r_squared:.5f}")
print("=" * 50)


# =============================================================================
# Franck–Hertz Excitation Energy
# =============================================================================

# Measurements selected for the determination of the voltage spacing
# between consecutive current minima.
selected_measurements = [
    ("normal", 195, 0, 5),
    ("normal", 195, 0, 15),
    ("normal", 195, 1.5, 5),
    ("normal", 225, 1.5, 5),
    ("normal", 240, 1.5, 5),
    ("normal", 220, 1.5, 5),
    ("normal", 200, 3, 5),
    ("normal", 220, 3, 5),
]


# Parameters used for minimum detection.
smoothing_sigma = 2


# -----------------------------------------------------------------------------
# Detect current minima and calculate voltage differences
# -----------------------------------------------------------------------------

voltage_differences = []

for measurement in selected_measurements:

    measurement_type, temperature, braking_voltage, resistance = (
        measurement
    )

    try:

        if measurement_type == "normal":

            voltage, current = measurements[
                braking_voltage
            ][resistance][temperature]

        elif measurement_type == "hysteresis":

            voltage, current = hysteresis_data[
                braking_voltage
            ][resistance][temperature]["Increasing"]

        else:
            print(
                f"Unknown measurement type: {measurement_type}"
            )
            continue

    except KeyError:

        print(
            f"Measurement not found: {measurement}"
        )
        continue

    # Smooth the current signal to reduce experimental noise.
    smoothed_current = gaussian_filter1d(
        current,
        sigma=smoothing_sigma
    )

    # Find local minima by searching for peaks in -I.
    #
    # The minimum distance is chosen as approximately one tenth
    # of the total number of sampled points.
    minimum_distance = int(len(voltage) / 10)

    minimum_indices, _ = find_peaks(
        -smoothed_current,
        distance=minimum_distance,
        prominence=0.02
    )

    if len(minimum_indices) < 2:

        print(
            f"Not enough minima found for: {measurement}"
        )
        continue

    # Voltage values corresponding to the detected minima.
    minimum_voltages = voltage[minimum_indices]

    # Voltage spacing between consecutive minima.
    delta_voltage = np.diff(minimum_voltages)

    voltage_differences.extend(delta_voltage)


# -----------------------------------------------------------------------------
# Mean voltage spacing and standard deviation
# -----------------------------------------------------------------------------

voltage_differences = np.array(voltage_differences)

if len(voltage_differences) > 0:

    mean_delta_voltage = np.mean(
        voltage_differences
    )

    std_delta_voltage = np.std(
        voltage_differences
    )

    print("\n" + "=" * 50)
    print(
        "Mean voltage difference between consecutive minima:"
    )
    print(
        f"ΔV = "
        f"{mean_delta_voltage:.2f} ± "
        f"{std_delta_voltage:.2f} V"
    )
    print("=" * 50)

else:

    print(
        "No voltage differences were found for "
        "the selected measurements."
    )


# =============================================================================
# Excitation Energy and Wavelength
# =============================================================================

if len(voltage_differences) > 0:

    # For singly charged electrons, the excitation energy in eV
    # is numerically equal to the corresponding voltage difference in V.
    excitation_energy = mean_delta_voltage
    excitation_energy_uncertainty = std_delta_voltage

    # Planck's constant multiplied by the speed of light,
    # expressed in eV·nm.
    hc = 1240

    # Associated photon wavelength.
    wavelength = hc / excitation_energy

    # Error propagation:
    #
    # λ = hc / E
    #
    # σ_λ = (hc / E²) σ_E
    wavelength_uncertainty = (
        hc
        / excitation_energy**2
        * excitation_energy_uncertainty
    )

    print("\n" + "=" * 50)

    print("Electronic excitation energy:")
    print(
        f"E = "
        f"{excitation_energy:.2f} ± "
        f"{excitation_energy_uncertainty:.2f} eV"
    )

    print("\nAssociated photon wavelength:")
    print(
        f"λ = "
        f"{wavelength:.1f} ± "
        f"{wavelength_uncertainty:.1f} nm"
    )

    print("=" * 50)
# %%