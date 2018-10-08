from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
from flask import make_response, request
from getDataFromDatabase import getHistData


def plot_temp():
    times, temps, hums = getHistData(5)
    #temps = [1, 2, 3, 4, 5, 6, 7, 8]
    ys = temps
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title("Temperature *C")
    axis.set_xlabel("Samples")
    axis.grid(True)
    xs = range(len(temps))
    axis.plot(xs, ys)
    canvas = FigureCanvas(fig)
    #canvas.print_figure("output.png")
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

def plot_hum():
    times, temps, hums = getHistData(5)
    ys = hums
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title("Humidity [%]")
    axis.set_xlabel("Samples")
    axis.grid(True)
    xs = range(len(hums))
    axis.plot(xs, ys)
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response	

if __name__ == "__main__":
    plot_temp()
