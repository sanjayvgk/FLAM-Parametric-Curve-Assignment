"""Fit and validate the FLAM parametric curve."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
from scipy.optimize import OptimizeResult, differential_evolution

ROOT = Path(__file__).resolve().parent
DEFAULT_DATA_PATH = ROOT / "data" / "UVCE_BTech_Flam_Resource.csv"
DEFAULT_OUTPUT_DIR = ROOT / "results"
BOUNDS = (
    (np.deg2rad(1e-8), np.deg2rad(50.0 - 1e-8)),
    (-0.05 + 1e-10, 0.05 - 1e-10),
    (1e-8, 100.0 - 1e-8),
)


def load_data(path: str | Path = DEFAULT_DATA_PATH) -> tuple[np.ndarray, np.ndarray]:
    """Load a non-empty, finite CSV whose columns are exactly ``x`` and ``y``."""
    path = Path(path).expanduser()
    frame = pd.read_csv(path)
    if list(frame.columns) != ["x", "y"]:
        raise ValueError("CSV must contain exactly the columns 'x,y' in that order")
    if frame.empty:
        raise ValueError("CSV contains no observations")
    try:
        numeric = frame.apply(pd.to_numeric, errors="raise")
    except (TypeError, ValueError) as exc:
        raise ValueError("CSV x and y values must be numeric") from exc
    values = numeric.to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("CSV x and y values must all be finite")
    return values[:, 0], values[:, 1]


def inverse_transform(
    x: np.ndarray, y: np.ndarray, theta: float, x_offset: float
) -> tuple[np.ndarray, np.ndarray]:
    """Undo the curve's rotation, returning inferred ``t`` and transverse ``v``."""
    dx, dy = np.asarray(x) - x_offset, np.asarray(y) - 42.0
    cosine, sine = np.cos(theta), np.sin(theta)
    return dx * cosine + dy * sine, -dx * sine + dy * cosine


def residuals(
    params: Iterable[float], x: np.ndarray, y: np.ndarray
) -> np.ndarray:
    """Return transformed-coordinate residuals for ``(theta, M, X)``."""
    theta, growth, x_offset = params
    t, v = inverse_transform(x, y, theta, x_offset)
    return v - np.exp(growth * np.abs(t)) * np.sin(0.3 * t)


def fitting_objective(
    params: Iterable[float], x: np.ndarray, y: np.ndarray
) -> float:
    """Return the mean absolute transformed-coordinate residual."""
    return float(np.mean(np.abs(residuals(params, x, y))))


def optimize_parameters(x: np.ndarray, y: np.ndarray) -> OptimizeResult:
    """Run the deterministic, bounded global optimization."""
    result = differential_evolution(
        fitting_objective,
        bounds=BOUNDS,
        args=(x, y),
        seed=42,
        popsize=25,
        maxiter=3000,
        tol=1e-12,
        polish=True,
        workers=1,
    )
    if not result.success:
        raise RuntimeError(f"Parameter optimization failed: {result.message}")
    return result


def derive_submission_parameters(params: Iterable[float]) -> tuple[float, float, float]:
    """Round the recovered pattern to clean assignment submission values."""
    theta, growth, x_offset = params
    return np.deg2rad(round(float(np.rad2deg(theta)))), round(float(growth), 2), round(float(x_offset))


def generate_curve(
    t: np.ndarray, params: Iterable[float]
) -> tuple[np.ndarray, np.ndarray]:
    """Evaluate the original two-dimensional parametric curve."""
    theta, growth, x_offset = params
    oscillation = np.exp(growth * np.abs(t)) * np.sin(0.3 * t)
    return (
        t * np.cos(theta) - oscillation * np.sin(theta) + x_offset,
        42.0 + t * np.sin(theta) + oscillation * np.cos(theta),
    )


def residual_metrics(values: np.ndarray) -> dict[str, float]:
    """Summarize transformed-coordinate residuals."""
    values = np.asarray(values)
    return {
        "mean_absolute": float(np.mean(np.abs(values))),
        "maximum_absolute": float(np.max(np.abs(values))),
        "rmse": float(np.sqrt(np.mean(values**2))),
    }


def uniform_curve_l1(
    first: Iterable[float], second: Iterable[float], sample_count: int = 10_000
) -> float:
    """Compare curves pointwise on a common uniform grid using 2-D L1 distance."""
    if sample_count < 2:
        raise ValueError("validation sample count must be at least 2")
    t = np.linspace(6.0, 60.0, sample_count)
    x_first, y_first = generate_curve(t, first)
    x_second, y_second = generate_curve(t, second)
    return float(np.mean(np.abs(x_first - x_second) + np.abs(y_first - y_second)))


def write_summary(
    path: Path,
    fitted: Iterable[float],
    submitted: Iterable[float],
    fitted_metrics: dict[str, float],
    submitted_metrics: dict[str, float],
    curve_l1: float,
    observation_count: int,
    t_range: tuple[float, float],
) -> None:
    """Write a deterministic plain-text audit summary."""
    theta, growth, x_offset = fitted
    theta_clean, growth_clean, x_clean = submitted
    text = f"""FLAM Research and Development / AI Assignment
Parametric Curve Unknown Parameter Estimation

Observations used: {observation_count}
Inferred t range: {t_range[0]:.10f} to {t_range[1]:.10f}

Final Parameters
theta = {np.rad2deg(theta_clean):.0f} degrees = pi/6 radians
M = {growth_clean:.2f}
X = {x_clean:.0f}

Numerical Optimization Result
theta = {np.rad2deg(theta):.10f} degrees
M = {growth:.10f}
X = {x_offset:.10f}

Fitted Transformed-Coordinate Residual Metrics
Mean absolute residual = {fitted_metrics['mean_absolute']:.12e}
Maximum absolute residual = {fitted_metrics['maximum_absolute']:.12e}
RMSE = {fitted_metrics['rmse']:.12e}

Submitted-Value Transformed-Coordinate Residual Metrics
Mean absolute residual = {submitted_metrics['mean_absolute']:.12e}
Maximum absolute residual = {submitted_metrics['maximum_absolute']:.12e}
RMSE = {submitted_metrics['rmse']:.12e}

Uniform pointwise curve L1 difference (fitted versus submitted) = {curve_l1:.12e}
"""
    path.write_text(text, encoding="utf-8")


def plot_curve(
    path: Path, x: np.ndarray, y: np.ndarray, submitted: Iterable[float], show: bool = False
) -> None:
    """Save observations and the submitted curve with contrasting styling."""
    t = np.linspace(6.0, 60.0, 10_000)
    curve_x, curve_y = generate_curve(t, submitted)
    fig, axis = plt.subplots(figsize=(10, 6))
    axis.scatter(x, y, s=12, alpha=0.55, color="#0072B2", label="Supplied observations")
    axis.plot(curve_x, curve_y, color="#D55E00", linewidth=2.2, label="Submitted curve")
    axis.set(title="FLAM Parametric Curve Fit", xlabel="x", ylabel="y")
    axis.grid(alpha=0.25)
    axis.legend()
    fig.tight_layout()
    # SVG keeps the generated plot reviewable in text-only diff systems.  A fixed
    # hash salt and omitted date make repeated output byte-for-byte deterministic.
    mpl.rcParams["svg.hashsalt"] = "flam-parametric-curve"
    fig.savefig(path, format="svg", metadata={"Date": None})
    svg = path.read_text(encoding="utf-8")
    path.write_text("\n".join(line.rstrip() for line in svg.splitlines()) + "\n", encoding="utf-8")
    if show:
        plt.show()
    plt.close(fig)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH, help="input x,y CSV")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="artifact directory")
    parser.add_argument("--validation-samples", type=int, default=10_000, help="uniform metric samples")
    parser.add_argument("--show", action="store_true", help="display the plot interactively")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    x, y = load_data(args.data)
    result = optimize_parameters(x, y)
    fitted = tuple(float(value) for value in result.x)
    submitted = derive_submission_parameters(fitted)
    fitted_metrics = residual_metrics(residuals(fitted, x, y))
    submitted_metrics = residual_metrics(residuals(submitted, x, y))
    curve_l1 = uniform_curve_l1(fitted, submitted, args.validation_samples)
    if curve_l1 >= 1e-3:
        raise RuntimeError(f"Rounded submission curve differs excessively: L1={curve_l1:.6e}")
    t, _ = inverse_transform(x, y, submitted[0], submitted[2])
    if not np.all((t > 6.0) & (t < 60.0)):
        raise RuntimeError("At least one inferred t lies outside the required open interval (6, 60)")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_summary(args.output_dir / "fitted_parameters.txt", fitted, submitted, fitted_metrics,
                  submitted_metrics, curve_l1, len(x), (float(t.min()), float(t.max())))
    plot_curve(args.output_dir / "curve_plot.svg", x, y, submitted, args.show)
    print(f"Observations used: {len(x)}")
    print(f"theta = {np.rad2deg(fitted[0]):.10f} degrees; M = {fitted[1]:.10f}; X = {fitted[2]:.10f}")
    print(f"Mean transformed absolute residual: {fitted_metrics['mean_absolute']:.12e}")
    print(f"Uniform curve L1 difference: {curve_l1:.12e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
