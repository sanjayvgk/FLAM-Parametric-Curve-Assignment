# FLAM Parametric Curve Assignment

## Final answer

**theta = 30 degrees = pi/6 radians, M = 0.03, X = 55**

For \(6<t<60\), the submitted curve is

$$
\begin{aligned}
x(t)&=t\cos\left(\frac{\pi}{6}\right)-e^{0.03|t|}\sin(0.3t)\sin\left(\frac{\pi}{6}\right)+55,\\
y(t)&=42+t\sin\left(\frac{\pi}{6}\right)+e^{0.03|t|}\sin(0.3t)\cos\left(\frac{\pi}{6}\right).
\end{aligned}
$$

Copy-paste expression for [Desmos](https://www.desmos.com/calculator/rfj91yrxob):

```text
\left(t\cos\left(\frac{\pi}{6}\right)-e^{0.03\left|t\right|}\sin(0.3t)\sin\left(\frac{\pi}{6}\right)+55,\ 42+t\sin\left(\frac{\pi}{6}\right)+e^{0.03\left|t\right|}\sin(0.3t)\cos\left(\frac{\pi}{6}\right)\right)\left\{6<t<60\right\}
```

![Supplied observations and submitted curve](results/curve_plot.svg)

## Method

Writing \(A=e^{M|t|}\sin(0.3t)\), the translated observations are a rotation:

$$
\begin{bmatrix}x-X\\y-42\end{bmatrix}=
\begin{bmatrix}\cos\theta&-\sin\theta\\\sin\theta&\cos\theta\end{bmatrix}
\begin{bmatrix}t\\A\end{bmatrix}.
$$

The inverse rotation therefore gives

$$
\begin{aligned}
t_i&=(x_i-X)\cos\theta+(y_i-42)\sin\theta,\\
v_i&=-(x_i-X)\sin\theta+(y_i-42)\cos\theta.
\end{aligned}
$$

SciPy differential evolution (seed 42) minimizes the **fitting objective**
\(\operatorname{mean}(|v_i-e^{M|t_i|}\sin(0.3t_i)|)\), within the assignment bounds
\(0^\circ<\theta<50^\circ\), \(-0.05<M<0.05\), and \(0<X<100\).

This is not the assignment evaluator's metric. The evaluator uses uniformly sampled,
pointwise two-dimensional L1 distance:
\(\operatorname{mean}(|x_{pred}(t_j)-x_{expected}(t_j)|+|y_{pred}(t_j)-y_{expected}(t_j)|)\).
It depends on the sampling grid and on matching equal parameter values; it is not a
nearest-point distance and should not be compared numerically with the fitting objective.

## Numerical verification

| Check | Result |
|---|---:|
| Observations used | 1,500 |
| Fitted theta | 29.9999730015 degrees |
| Fitted M | 0.0299999971 |
| Fitted X | 54.9999983399 |
| Fitted mean transformed absolute residual | 2.558593110990e-6 |
| Fitted maximum transformed absolute residual | 1.745866859326e-5 |
| Uniform curve L1, fitted versus submitted | 1.946105917974e-5 |

The tiny fit residuals are consistent with decimal rounding in the supplied observations.
The numerical values are correspondingly close to a clear clean pattern, so the submission
rounds theta to 30 degrees, M to 0.03, and X to 55. The program independently requires the
uniform fitted-versus-rounded curve difference to remain below \(10^{-3}\).

## Install and run

Python 3.12 is used in CI.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
MPLBACKEND=Agg python solution.py
python -m unittest discover -s tests -v
```

Paths are resolved relative to `solution.py`, so the default command works from any current
directory. Options are `--data PATH`, `--output-dir DIR`, `--validation-samples N`, and
`--show` (interactive plotting; off by default). Run `python solution.py --help` for details.
The deterministic run writes `results/fitted_parameters.txt` and the text-based,
diff-reviewable `results/curve_plot.svg`.

## Manual Desmos verification

Open the assignment [Desmos calculator](https://www.desmos.com/calculator/rfj91yrxob), paste
the expression above, and visually confirm the domain-restricted curve. Checking while signed
out is recommended to ensure the shared calculator and expression are publicly accessible.

## Project structure

```text
data/UVCE_BTech_Flam_Resource.csv  supplied 1,500 observations
results/                           deterministic summary and plot
solution.py                        fitting, validation, CLI, and plotting
tests/test_solution.py             standard-library unit tests
.github/workflows/test.yml         Python 3.12 CI and smoke test
```

## References

- Assignment-provided [Desmos calculator](https://www.desmos.com/calculator/rfj91yrxob)
- [SciPy `differential_evolution` documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.differential_evolution.html)
