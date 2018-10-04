import random
import dash
import dash_core_components as dcc
import dash_html_components as html

import numpy as np
import fitna

np.random.seed(1234)

# Two dimensional normal distributions
normal_params = [
    fitna.data.NormalDist(norm=1, mean=np.array([4, 4]), cov=np.array([[1, -0.5], [-0.5, 1]]), size=100, name='dataset_1'),
    fitna.data.NormalDist(norm=1, mean=np.array([6, 6]), cov=np.array([[1,  0.5], [ 0.5, 1]]), size=100, name='dataset_2'),
    fitna.data.NormalDist(norm=1, mean=np.array([4, 4]), cov=np.array([[1, -0.5], [-0.5, 1]]), size=10, name='dataset_1_s'),
    fitna.data.NormalDist(norm=1, mean=np.array([6, 6]), cov=np.array([[1,  0.5], [ 0.5, 1]]), size=10, name='dataset_2_s')
]

normal_mixture = fitna.data.NormalMixture(normal_params)
data_points = normal_mixture.rvs()

g_all_estimates = []

# Initialize global variables to refer to list of normal_params with predefined datasets
dropdown_dataset_options = []

for (dataset_name, sample) in normal_mixture.datasets.items():
    dropdown_dataset_options.append({'label': dataset_name, 'value': dataset_name})

# Make traces with covariance matrix eigenvectors
initial_estimates = [
    fitna.data.NormalDist(norm=0.5, mean=np.array([5.1, 5.1]), cov=np.array([[1., 0.], [0., 1.]]) ),
    fitna.data.NormalDist(norm=0.5, mean=np.array([4.9, 4.9]), cov=np.array([[1., 0.], [0., 1.]]) )
]

fig_layout = {
    'height': 1000,
    'xaxis': {'autorange': True},
    'yaxis': {'scaleanchor': 'x', 'scaleratio': 1, 'autorange': True}
}


app = dash.Dash(__name__)

app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

app.layout = html.Div([
    dcc.Graph(
        id='graph-out',
        figure={'data': [], 'layout': fig_layout },
        animate=True
    ),

    html.Div(
        id='slider-div',
        style={'width': '90%', 'margin': 'auto'},
        children=[dcc.Slider(id='slider-steps', value=0)]
    ),

    html.Div(
        id='controls-div',
        style={'width': '50%', 'margin': '3em auto'},
        children=[
            dcc.Dropdown(
                id='dropdown-datasets',
                options=dropdown_dataset_options,
                value=[],
                multi=True ),
            html.Button('Run', id='button-do-em', n_clicks=0) ]
    )
])


# Now add optimization/fit steps
def run_optimization(dataset_names):
    # Filter datasets based on dataset_names
    selected_samples = [normal_mixture.datasets[name] for name in dataset_names]
    data_points_T = np.concatenate(selected_samples, 1).T
    dummy_ll_new, all_estimates = fitna.em.do_em(data_points_T, initial_estimates, 1e-6, 50)

    return all_estimates


def update_figure(dataset_names, optimization_step):
    data = fitna.plotly.make_traces_from_dict(normal_mixture.datasets, dataset_names)

    if optimization_step > 0:
        err_traces = fitna.plotly.make_traces_from_NormalDists(g_all_estimates[optimization_step-1])
        data.extend(err_traces)

    return {
        'data': data,
        'layout': fig_layout
    }


@app.callback(
    dash.dependencies.Output('graph-out', 'figure'),
    [dash.dependencies.Input('dropdown-datasets', 'value'),
     dash.dependencies.Input('slider-steps', 'value')])
def select_datasets(dataset_names, optimization_step):
    return update_figure(dataset_names, optimization_step)


@app.callback(
    dash.dependencies.Output('slider-div', 'children'),
    [dash.dependencies.Input('button-do-em', 'n_clicks')],
    [dash.dependencies.State('dropdown-datasets', 'value')])
def select_datasets(n_clicks, dataset_names):
    global g_all_estimates
    g_all_estimates = run_optimization(dataset_names) if len(dataset_names) else []
    slider = dcc.Slider(
                 id='slider-steps',
                 min=0,
                 max=len(g_all_estimates),
                 step=1,
                 value=0,
                 disabled=False,
                 marks={i: 'step {}'.format(i) for i in range(0, len(g_all_estimates) + 1)} )
    return [slider]


if __name__ == '__main__':
    app.run_server(debug=True)
