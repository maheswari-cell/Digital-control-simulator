from flask import Flask, render_template_string, request
import numpy as np
import matplotlib.pyplot as plt
from control.matlab import tf, c2d
from control import step_response
import os

# Initialize Flask app
app = Flask(__name__)
PLOT_DIR = "static/plots"
os.makedirs(PLOT_DIR, exist_ok=True)

# HTML Template (Embedded)
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Digital Control System Simulator</title>
</head>
<body>
    <h1>Digital Control System Simulator (Bilinear Transformation)</h1>
    <form method="post">
        <label>Numerator Coefficients:</label><br>
        <input type="text" name="numerator" placeholder="e.g., 1 5"><br><br>
        <label>Denominator Coefficients:</label><br>
        <input type="text" name="denominator" placeholder="e.g., 1 2 1"><br><br>
        <label>Sampling Time (Ts):</label><br>
        <input type="text" name="sampling_time" placeholder="e.g., 0.1"><br><br>
        <input type="submit" value="Simulate">
    </form>

    {% if plot_url %}
        <h2>Step Response</h2>
        <img src="{{ plot_url }}" alt="Step Response Plot">
    {% endif %}
</body>
</html>
"""

# Main route
@app.route("/", methods=["GET", "POST"])
def index():
    plot_url = None
    if request.method == "POST":
        try:
            # Get input values
            num = list(map(float, request.form["numerator"].split()))
            den = list(map(float, request.form["denominator"].split()))
            Ts = float(request.form["sampling_time"])

            # Continuous-time system
            sys = tf(num, den)

            # Discrete-time system using bilinear transformation (Tustin)
            d_sys = c2d(sys, Ts, method='tustin')

            # Step response
            time, response = step_response(d_sys)

            # Plot and save
            plt.figure()
            plt.title("Step Response (Discrete System)")
            plt.plot(time, response)
            plt.xlabel("Time (s)")
            plt.ylabel("Output")
            plt.grid(True)

            plot_path = os.path.join(PLOT_DIR, "step_response.png")
            plt.savefig(plot_path)
            plt.close()

            plot_url = "/" + plot_path.replace("\\", "/")
        except Exception as e:
            plot_url = None
            print(f"Error: {e}")

    return render_template_string(html_template, plot_url=plot_url)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
