import json
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
# Generate random samples for the provided distributions
normal_mixture.rvs()

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
        children=[dcc.Slider(id='slider-steps', value=0, disabled=True)]
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
            html.Button('Run', id='button-run-em', n_clicks=0) ]
    ),

    html.Div(id='div-cached-optimization-steps', style={'display': 'none'})
])


# Now add optimization/fit steps
def run_optimization(dataset_names):
    # Filter datasets based on dataset_names
    selected_samples = [normal_mixture.datasets[name] for name in dataset_names]
    data_points_T = np.concatenate(selected_samples, 1).T
    dummy_ll_new, all_estimates, all_memb_probs = fitna.em.do_em(data_points_T, initial_estimates, 1e-6, 50)

    return all_estimates, all_memb_probs



@app.callback(
    dash.dependencies.Output('graph-out', 'figure'),
    [dash.dependencies.Input('slider-steps', 'value'),
     dash.dependencies.Input('dropdown-datasets', 'value')],
    [dash.dependencies.State('div-cached-optimization-steps', 'children')])
def select_slider_step(optimization_step, dataset_names, cached_steps):

    if cached_steps == None:
        return { 'data': [], 'layout': fig_layout }

    cached_step = next((step for step in cached_steps if step['props']['id'] == 'step_{}'.format(optimization_step)), {})
    #print(cached_step)
    cached_step_memb_prob = next((step for step in cached_steps if step['props']['id'] == 'step_{}_memb_probs'.format(optimization_step)), {})

    data = fitna.plotly.make_traces_combo(normal_mixture.datasets, dataset_names, json.loads(cached_step_memb_prob['props']['children']) if cached_step_memb_prob else [])

    if cached_step:
        data.extend(json.loads(cached_step['props']['children']))

    return {
        'data': data,
        'layout': fig_layout
    }



@app.callback(
    dash.dependencies.Output('slider-div', 'children'),
    [dash.dependencies.Input('div-cached-optimization-steps', 'children')])
def update_slider(div_children):
    if not div_children:
        return [dcc.Slider(id='slider-steps', value=0, disabled=True)]
    else:
        slider = dcc.Slider(
                     id='slider-steps',
                     min=0,
                     max=len(div_children)/2 - 1,
                     step=1,
                     value=0,
                     disabled=False,
                     marks={i: 'step {}'.format(i) for i in range(0, int(len(div_children)/2))} )
        return [slider]



@app.callback(
    dash.dependencies.Output('div-cached-optimization-steps', 'children'),
    [dash.dependencies.Input('button-run-em', 'n_clicks')],
    [dash.dependencies.State('dropdown-datasets', 'value')])
def request_run_optimization(n_clicks, dataset_names):

    all_estimates, all_memb_probs = run_optimization(dataset_names) if len(dataset_names) else ([], [])

    div_cached_optimization_steps = []

    for index, estimate in enumerate(all_estimates):

        traces = fitna.plotly.make_traces_from_NormalDists(estimate)
        traces_as_json = list(map(lambda tr: tr.to_plotly_json(), traces))

        div = html.Div(id='step_{}'.format(index), children=json.dumps(traces_as_json))
        div_cached_optimization_steps.append(div)

        div = html.Div(id='step_{}_memb_probs'.format(index), children=json.dumps(all_memb_probs[index].tolist()))
        div_cached_optimization_steps.append(div)

    return div_cached_optimization_steps



if __name__ == '__main__':
    app.run_server(debug=True)
