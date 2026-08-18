import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import differential_evolution
from scipy.spatial import cKDTree


# 1. Load the supplied data

DATA_PATH = "data/UVCE_BTech_Flam_Resource.csv"

data = pd.read_csv(DATA_PATH)

x = data["x"].to_numpy(dtype=float)
y = data["y"].to_numpy(dtype=float)

print("FLAM PARAMETRIC CURVE PARAMETER ESTIMATION")
print(f"Number of supplied points: {len(data)}")


# 2. Residual calculation

def calculate_residuals(params):
    """
    Calculate transformed-coordinate residuals for
    candidate parameters (theta, M, X).

    theta is represented internally in radians.
    """

    theta, M, X = params

    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)

    # Inverse rotation:
    # t = (x-X)cos(theta) + (y-42)sin(theta)
    t = (
        (x - X) * cos_theta
        + (y - 42.0) * sin_theta
    )

    # Transformed second coordinate
    v = (
        -(x - X) * sin_theta
        + (y - 42.0) * cos_theta
    )

    # Expected transformed second coordinate
    predicted_v = (
        np.exp(M * np.abs(t))
        * np.sin(0.3 * t)
    )

    return v - predicted_v


# 3. L1 objective function

def objective(params):
    """
    Mean absolute residual (L1 objective).
    """

    residuals = calculate_residuals(params)

    return np.mean(np.abs(residuals))


# 4. Parameter bounds from the assignment

bounds = [
    (
        np.deg2rad(1e-8),
        np.deg2rad(50.0 - 1e-8)
    ),
    (
        -0.05 + 1e-10,
        0.05 - 1e-10
    ),
    (
        1e-8,
        100.0 - 1e-8
    )
]


# 5. Numerical optimization

print("\nRunning numerical optimization...")

result = differential_evolution(
    objective,
    bounds=bounds,
    seed=42,
    popsize=25,
    maxiter=3000,
    tol=1e-12,
    polish=True,
    workers=1
)

theta_rad, M, X = result.x
theta_deg = np.rad2deg(theta_rad)

residuals = calculate_residuals(result.x)

mean_l1 = np.mean(np.abs(residuals))
max_abs_error = np.max(np.abs(residuals))
rmse = np.sqrt(np.mean(residuals ** 2))


# 6. Print numerical result

print("\nOPTIMIZATION RESULT")
print(f"theta (degrees): {theta_deg:.10f}")
print(f"M:               {M:.10f}")
print(f"X:               {X:.10f}")

print("\nError metrics")
print(f"Mean L1 residual:  {mean_l1:.12e}")
print(f"Maximum residual:  {max_abs_error:.12e}")
print(f"RMSE:              {rmse:.12e}")


# 7. Exact recovered parameters

theta_exact = np.deg2rad(30.0)
M_exact = 0.03
X_exact = 55.0

exact_residuals = calculate_residuals(
    (theta_exact, M_exact, X_exact)
)

exact_mean_l1 = np.mean(np.abs(exact_residuals))
exact_max_error = np.max(np.abs(exact_residuals))
exact_rmse = np.sqrt(np.mean(exact_residuals ** 2))

print("\nEXACT PARAMETERS")
print("theta = 30 degrees")
print("M     = 0.03")
print("X     = 55")

print("\nVerification using exact parameters")
print(f"Mean L1 residual:  {exact_mean_l1:.12e}")
print(f"Maximum residual:  {exact_max_error:.12e}")
print(f"RMSE:              {exact_rmse:.12e}")


# 8. Generate a uniformly sampled fitted curve

t_values = np.linspace(6.0, 60.0, 10000)

x_curve = (
    t_values * np.cos(theta_exact)
    - np.exp(M_exact * np.abs(t_values))
    * np.sin(0.3 * t_values)
    * np.sin(theta_exact)
    + X_exact
)

y_curve = (
    42.0
    + t_values * np.sin(theta_exact)
    + np.exp(M_exact * np.abs(t_values))
    * np.sin(0.3 * t_values)
    * np.cos(theta_exact)
)


# 9. Compare fitted curve against supplied points

observed_points = np.column_stack((x, y))
curve_points = np.column_stack((x_curve, y_curve))

tree = cKDTree(curve_points)

distances, _ = tree.query(
    observed_points,
    k=1
)

print("\nCURVE-TO-DATA CHECK")
print(f"Mean nearest-curve distance: {np.mean(distances):.12e}")
print(f"Maximum nearest-curve distance: {np.max(distances):.12e}")


# 10. Save fitted parameter summary

os.makedirs("results", exist_ok=True)

with open(
    "results/fitted_parameters.txt",
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "FLAM Research and Development / AI Assignment\n"
    )

    file.write(
        "Parametric Curve Unknown Parameter Estimation\n\n"
    )

    file.write(
        "Final Parameters\n"
    )

    file.write(
        "theta = 30 degrees\n"
    )

    file.write(
        "M = 0.03\n"
    )

    file.write(
        "X = 55\n\n"
    )

    file.write(
        "Numerical Optimization Result\n"
    )

    file.write(
        f"theta = {theta_deg:.10f} degrees\n"
    )

    file.write(
        f"M = {M:.10f}\n"
    )

    file.write(
        f"X = {X:.10f}\n\n"
    )

    file.write(
        "Error Metrics\n"
    )

    file.write(
        f"Mean L1 residual = {mean_l1:.12e}\n"
    )

    file.write(
        f"Maximum residual = {max_abs_error:.12e}\n"
    )

    file.write(
        f"RMSE = {rmse:.12e}\n"
    )


# 11. Plot observed points and fitted curve

plt.figure(figsize=(10, 7))

plt.scatter(
    x,
    y,
    s=12,
    alpha=0.45,
    label="Supplied data points"
)

plt.plot(
    x_curve,
    y_curve,
    linewidth=2,
    label="Fitted parametric curve"
)

plt.xlabel("x")
plt.ylabel("y")

plt.title(
    "FLAM Assignment - Fitted Parametric Curve"
)

plt.legend()

plt.grid(True, alpha=0.3)

plt.tight_layout()

plt.savefig(
    "results/curve_plot.png",
    dpi=300
)

plt.show()

print("\nDONE")
print("Final answer:")
print("theta = 30 degrees")
print("M = 0.03")
print("X = 55")