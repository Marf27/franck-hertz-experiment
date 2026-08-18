# ⚛️ Franck–Hertz Experiment

Experimental analysis of the **Franck–Hertz experiment** using voltage-current measurements of a mercury-filled Franck–Hertz tube.

The project investigates the characteristic current minima produced by inelastic electron-atom collisions and uses the experimental data to estimate the **excitation energy of mercury atoms** and the corresponding **photon wavelength**.

## Overview

The Franck–Hertz experiment provides direct experimental evidence for the quantization of atomic energy levels. Electrons are accelerated through a gas of mercury atoms and undergo inelastic collisions when their kinetic energy reaches the excitation energy of the atoms.

This project analyzes experimental measurements acquired at different:

* Tube temperatures
* Braking voltages
* Circuit resistances
* Voltage sweep directions

The analysis includes both standard current-voltage measurements and hysteresis measurements.

## Analysis

The Python script performs the following steps:

1. Loads experimental voltage-current measurements from text files.
2. Converts the original measurement format into numerical NumPy arrays.
3. Plots experimental **I–V curves** for different temperatures, braking voltages, and resistances.
4. Analyzes **hysteresis** by comparing increasing and decreasing voltage sweeps.
5. Investigates the dependence of the critical voltage on the tube temperature.
6. Performs a weighted linear fit of `log(V)` as a function of temperature.
7. Calculates the coefficient of determination (R^2).
8. Smooths experimental current signals using a Gaussian filter.
9. Automatically detects consecutive current minima using `scipy.signal.find_peaks`.
10. Determines the mean voltage separation between consecutive minima.
11. Estimates the **excitation energy of mercury atoms**.
12. Calculates the corresponding **photon wavelength** using

[
E = \frac{hc}{\lambda}.
]

## Results

The analysis of the selected experimental measurements gives approximately:

[
\Delta_V = (5.06 \pm 2.94),\mathrm{V}
]

for the mean voltage separation between consecutive current minima.

For singly charged electrons, the corresponding excitation energy is numerically equal to the voltage difference:

[
E_\mathrm{exc} = (5.06 \pm 2.94),\mathrm{eV}.
]

The associated photon wavelength is therefore approximately

[
\lambda = (251.7 \pm 20.9),\mathrm{nm}.
]

The temperature-dependent analysis also includes a weighted linear fit of

[
\log(V_\mathrm{critical})
]

as a function of temperature.

The fit quality is evaluated using the coefficient of determination (R^2).

> **Note:** The experimental uncertainty is relatively large, primarily due to the scatter in the detected voltage spacing between consecutive minima. The reported values should therefore be interpreted as experimental estimates rather than high-precision measurements.

## Requirements

The project requires Python 3 and the following scientific Python libraries:

* NumPy
* SciPy
* Matplotlib

Install the dependencies with:

## Usage

Clone the repository:

```bash
git clone https://github.com/<your-username>/franck-hertz-experiment.git
cd franck-hertz-experiment
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Then run the analysis script:

```bash
python src/franck_hertz.py
```

The script loads the experimental measurements, performs the analysis, and generates the corresponding plots.

## Methods

### I–V Curves

The experimental current is plotted as a function of the applied accelerating voltage for different experimental conditions.

These curves reveal the characteristic oscillatory structure associated with repeated inelastic collisions between electrons and mercury atoms.

### Hysteresis Analysis

Measurements were performed while both increasing and decreasing the applied voltage.

The two voltage sweeps are plotted together to investigate possible hysteresis effects in the experimental system.

### Temperature Dependence

The critical voltage is analyzed as a function of the Franck–Hertz tube temperature.

The transformation

[
y = \log(V_\mathrm{critical})
]

is used to obtain a linear relationship with temperature:

[
\log(V_\mathrm{critical}) = aT+b.
]

The fit is performed using the experimental uncertainty in the critical voltage as weights.

### Minimum Detection

The excitation energy is estimated from the spacing between consecutive current minima.

Because the experimental data contain noise, the current signal is first smoothed using a Gaussian filter:

```python
smoothed_current = gaussian_filter1d(
    current,
    sigma=smoothing_sigma
)
```

Local minima are then detected by applying `find_peaks` to the negative current:

```python
minimum_indices, _ = find_peaks(
    -smoothed_current,
    distance=minimum_distance,
    prominence=0.02
)
```

The voltage differences between consecutive minima are then averaged across the selected measurements.

### Excitation Energy

For electrons with charge magnitude (e), an accelerating voltage difference (\Delta V) corresponds numerically to an energy difference of (\Delta V) eV.

Therefore,

[
E_\mathrm{exc} \approx \Delta V\ \mathrm{eV}.
]

### Photon Wavelength

The wavelength associated with the excitation energy is calculated from

[
\lambda = \frac{hc}{E}.
]

Using (hc \approx 1240\ \mathrm{eV,nm}),

[
\lambda[\mathrm{nm}] \approx
\frac{1240}{E[\mathrm{eV}]}.
]

Uncertainty propagation is performed using

[
\sigma_\lambda =
\frac{hc}{E^2}\sigma_E.
]

## Technologies

* **Python**
* **NumPy** — numerical calculations and data handling
* **SciPy** — signal processing, peak detection, and curve fitting
* **Matplotlib** — experimental data visualization

## Scientific Context

The Franck–Hertz experiment was first performed by **James Franck and Gustav Hertz** in 1914 and provided experimental evidence that atoms absorb energy in discrete quantities.

The experiment played an important role in establishing the quantized nature of atomic energy levels and was awarded the **1925 Nobel Prize in Physics** to Franck and Hertz.

## Reproducibility

The analysis is designed to be reproducible from the original experimental measurements.

All numerical parameters used for signal processing, fitting, and uncertainty estimation are explicitly defined in the source code.

For complete reproducibility, the original experimental data should be included in the `data/` directory.

## Author

**Mathias Rendón Fernández**

Physics student — Universidad Autónoma de Madrid
