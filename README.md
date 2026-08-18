<<<<<<< HEAD
# Research and Development / AI Assignment

## Parametric Curve Unknown Parameter Estimation

## 1. Problem Statement

The objective of this assignment is to determine the unknown parameters θ, M, and X of a given parametric curve using the supplied set of (x, y) points.

The given curve is:

[
x=t\cos(\theta)-e^{M|t|}\sin(0.3t)\sin(\theta)+X
]

[
y=42+t\sin(\theta)+e^{M|t|}\sin(0.3t)\cos(\theta)
]

The supplied resource contains 1,500 points that lie on the required curve.

The parameter constraints provided in the assignment are:

[
0^\circ < \theta < 50^\circ
]

[
-0.05 < M < 0.05
]

[
0 < X < 100
]

and

[
6 < t < 60.
]

---

## 2. Input Data

The input data is provided in:

text
data/UVCE_BTech_Flam_Resource.csv


The CSV contains two columns:

text
x
y


and contains 1,500 observed points.

The order of the points in the CSV is not assumed to correspond to increasing values of the parameter t.

---

## 3. Mathematical Transformation

The original equations can be simplified by defining:

[
A=e^{M|t|}\sin(0.3t).
]

The equations then become:

[
x-X=t\cos(\theta)-A\sin(\theta)
]

[
y-42=t\sin(\theta)+A\cos(\theta).
]

This can be interpreted as a rotation of the vector:

[
\begin{bmatrix}
t\
A
\end{bmatrix}
]

by the angle (\theta).

Therefore, applying the inverse rotation gives:

[
t=(x-X)\cos(\theta)+(y-42)\sin(\theta)
]

and

[
A=-(x-X)\sin(\theta)+(y-42)\cos(\theta).
]

Since

[
A=e^{M|t|}\sin(0.3t),
]

the transformed coordinates must satisfy:

[
-(x-X)\sin(\theta)+(y-42)\cos(\theta)
=====================================

e^{M|t|}\sin(0.3t).
]

This transformation removes the need to independently optimize the value of t for every observed point.

---

## 4. Residual Function

For each observed point (x_i, y_i), calculate:

[
t_i=(x_i-X)\cos(\theta)+(y_i-42)\sin(\theta)
]

and

[
v_i=-(x_i-X)\sin(\theta)+(y_i-42)\cos(\theta).
]

The predicted value of the transformed coordinate is:

[
\hat v_i=e^{M|t_i|}\sin(0.3t_i).
]

Therefore, the residual is:

[
r_i=v_i-\hat v_i.
]

For the correct values of θ, M, and X, the residuals should be close to zero.

---

## 5. Optimization Objective

The assignment evaluates the L1 distance between the expected and predicted curve.

Therefore, the optimization objective used in this solution is the mean absolute residual:

[
L(\theta,M,X)
=============

\frac{1}{N}
\sum_{i=1}^{N}|r_i|.
]

The search is restricted to the parameter ranges specified in the assignment.

A global numerical optimization method is used to search the three-dimensional parameter space.

---

## 6. Numerical Optimization

The implementation uses Python with NumPy, Pandas, SciPy, and Matplotlib.

The optimizer searches the following ranges:

text
0° < θ < 50°
-0.05 < M < 0.05
0 < X < 100


The fitted numerical values are approximately:

text
θ = 29.999973°
M = 0.029999997
X = 54.999998


These values correspond to the exact parameters:

[
\boxed{\theta=30^\circ}
]

[
\boxed{M=0.03}
]

[
\boxed{X=55}
]

---

## 7. Final Parametric Curve

Substituting the recovered parameters into the original equations gives:

[
x=t\cos(30^\circ)-e^{0.03|t|}\sin(0.3t)\sin(30^\circ)+55
]

[
y=42+t\sin(30^\circ)+e^{0.03|t|}\sin(0.3t)\cos(30^\circ)
]

for:

[
6<t<60.
]

Using:

[
\cos(30^\circ)=\frac{\sqrt3}{2}
]

and

[
\sin(30^\circ)=\frac12,
]

the equations can also be written as:

[
x=
55+\frac{\sqrt3}{2}t
-\frac12e^{0.03|t|}\sin(0.3t)
]

[
y=
42+\frac12t
+\frac{\sqrt3}{2}e^{0.03|t|}\sin(0.3t).
]

---

## 8. Verification

The recovered parameters were tested against all 1,500 supplied points.

Using:

text
θ = 30°
M = 0.03
X = 55


the transformed-coordinate residual is extremely small.

The numerical optimization produced approximately:

text
Mean absolute residual ≈ 2.56 × 10^-6
Maximum absolute residual ≈ 1.75 × 10^-5


This confirms that the recovered parameters closely reproduce the supplied curve.

---

## 9. How to Run the Solution

Install the required Python packages:

bash
pip install -r requirements.txt


Then execute:

bash
python solution.py


The program loads the CSV data, performs the parameter estimation, prints the fitted parameters and error metrics, and generates a curve comparison plot.

---

## 10. Interactive Desmos Visualization

The final fitted curve can also be viewed interactively in Desmos:

[Open the Interactive Desmos Graph](https://www.desmos.com/calculator/dnm1sdkavp)

The Desmos graph uses the recovered values:

text
θ = 30°
M = 0.03
X = 55


with the parameter range:

text
6 < t < 60


---

## 11. Final Answer

[
\boxed{\theta=30^\circ,\quad M=0.03,\quad X=55}
]

These are the unknown parameter values obtained from the supplied point data and the specified parameter constraints.
=======
# FLAM-Parametric-Curve-Assignment
Research and Development - Parametric Curve Unknown Parameter Estimation
>>>>>>> e673aa3d14272beeb09a8d9800d976369a25955b
