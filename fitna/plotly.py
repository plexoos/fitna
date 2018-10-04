import numpy as np
import plotly
import scipy


def make_traces_from_arrays(data_points):

    traces = []

    for point_set in data_points:
        trace = plotly.graph_objs.Scatter(
            x=point_set[0],
            y=point_set[1],
            mode='markers',
            hoverinfo='none'
        )

        traces.append(trace)

    return traces


def make_traces_from_dict(data_points, dataset_names=[]):

    traces = []

    for name, point_set in data_points.items():
        if name not in dataset_names:
            continue

        trace = plotly.graph_objs.Scatter(
            x=point_set[0],
            y=point_set[1],
            mode='markers',
            hoverinfo='none'
        )

        traces.append(trace)

    return traces


def make_trace_from_cov(cov, mean_x=0, mean_y=0):

    w, v = scipy.linalg.eigh(cov)
    alpha = np.arctan2(v[1,0], v[0,0])
    trace = make_trace_ellipse(mean_x, mean_y, w[0], w[1], alpha)

    return trace


def make_traces_from_NormalDists(estimates):

    return [make_trace_from_cov(e.cov, e.mean[0], e.mean[1]) for e in estimates]


def make_trace_ellipse_axes(cov, mean_x=0, mean_y=0):

    w, v = scipy.linalg.eigh(cov)

    trace = plotly.graph_objs.Scatter(
        x=[ w[0]*v[0,0] + mean_x, mean_x, w[1]*v[1,0] + mean_x ],
        y=[ w[0]*v[0,1] + mean_y, mean_y, w[1]*v[1,1] + mean_y ],
        mode='lines',
        line=dict(width = 5),
        hoverinfo='none'
    )

    return trace


def make_trace_ellipse(xc=0, yc=0, a=1, b=1, alpha=0):

    t = np.linspace(0, 2*np.pi, 50)
    x = xc + a * np.cos(t) * np.cos(alpha) - b * np.sin(t) * np.sin(alpha)
    y = yc + a * np.cos(t) * np.sin(alpha) + b * np.sin(t) * np.cos(alpha)

    trace = plotly.graph_objs.Scatter(
        x=x,
        y=y,
        mode='lines',
        hoverinfo='none'
    )

    return trace
