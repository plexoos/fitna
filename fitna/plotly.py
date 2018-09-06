import plotly.graph_objs as go
import scipy


def make_traces(estimates):

    traces = []

    for estimate in estimates:
        w, v = scipy.linalg.eigh(estimate.cov)
        
        errors = [dict( type = 'line', x0 = 0, y0 = 0, x1 = w[0]*v[0][0], y1 = w[0]*v[0][1] ),
                  dict( type = 'line', x0 = 0, y0 = 0, x1 = w[1]*v[1][0], y1 = w[1]*v[1][1] )]
        
        mean_x = estimate.mean[0]
        mean_y = estimate.mean[1]
        
        err_trace = go.Scatter(
            x = [ w[0]*v[0][0] + mean_x, mean_x, w[1]*v[1][0] + mean_x ],
            y = [ w[0]*v[0][1] + mean_y, mean_y, w[1]*v[1][1] + mean_y ],
            mode = 'lines',
            line = dict(width = 5),
            hoverinfo = 'none'
        )

        traces.append(err_trace)

    return traces
