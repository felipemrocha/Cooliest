import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from flask import Flask, Response, jsonify, render_template, request

from src.model.calculate_wall_temp import calculate_wall_temp

plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/solve", methods=["GET", "POST"])
def my_form_post():
    if request.method == "POST":
        w = float(request.form["w"])
        h = float(request.form["h"])
        l = float(request.form["l"])
        T_in = float(request.form["T_in"])
        V_dot = float(request.form["V_dot"])
        q_chip = float(request.form["q_chip"])
        fluid_name = request.form["fluid_name"]

        T_wall_K = round(
            calculate_wall_temp(w, h, l, T_in, V_dot, q_chip, fluid_name), 2
        )
        T_wall_C = T_wall_K - 273.15
        result = [T_wall_K, T_wall_C]

        x = [1, 2, 3, 4]
        y1 = [w, h, l, T_in]
        y2 = [V_dot, q_chip, T_wall_K, T_wall_C]

        plt.figure()
        plt.plot(x, y1)
        plt.plot(x, y2)
        plt.title("Test Plot")
        plt.xlabel("Numbers")
        plt.ylabel("Random Variables")
        plt.legend(["data", "more data"])
        plt.savefig("static/my_plot.png")

        return render_template(
            "home.html", get_plot=True, plot_url="static/my_plot.png", result=result
        )
    else:
        return render_template("home.html")


def main():
    app.run(debug=True, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
