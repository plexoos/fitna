import copy
import numpy as np
import scipy.stats


def do_em(data, initial_estimates, tol=1e-6, max_iter=10):
    # Copy initial estimates to a local list
    # The local list may change size in the future
    components = copy.deepcopy(initial_estimates)

    all_estimates = []

    n_points, n_dims = data.shape
    n_components = len(components)

    ll_old = 0
    ll_new = 0

    for iteration in range(1, max_iter+1):
        print(f'iteration # {iteration} of {max_iter}')

        # E-step
        # For each data point calculate membership/assignment probabilities
        # associated with each current cluster
        memb_probs = np.zeros((n_components, n_points))

        for ic, component in enumerate(components):
            for ip in range(n_points):
                memb_probs[ic, ip] = component.norm * scipy.stats.multivariate_normal(component.mean, component.cov).pdf(data[ip])

        # Normalize the weight of each data point to 1
        memb_probs /= memb_probs.sum(0)

        # M-step
        # For each cluster calculate new norms given the probabilities
        for ic, component in enumerate(components):
            component.norm = 0
            for ip in range(n_points):
                component.norm += memb_probs[ic, ip]
            component.norm /= n_points

        # For each cluster calculate new (weighted) means given the probabilities
        for ic, component in enumerate(components):
            component.mean[:] = 0
            for ip in range(n_points):
                component.mean += memb_probs[ic, ip] * data[ip]
            component.mean /= memb_probs[ic, :].sum()

        # For each cluster calculate new covars given the probabilities
        for ic, component in enumerate(components):
            component.cov[:] = 0
            for ip in range(n_points):
                ys = np.reshape(data[ip] - component.mean, (n_dims, 1))
                component.cov += memb_probs[ic, ip] * np.dot(ys, ys.T)
            component.cov /= memb_probs[ic, :].sum()

        # Calculate new log likelihood value for all data points
        ll_new = 0.0
        for ip in range(n_points):
            s = 0
            for component in components:
                s += component.norm * scipy.stats.multivariate_normal(component.mean, component.cov).pdf(data[ip])
            ll_new += np.log(s)

        ll_frac_delta = np.abs( (ll_new - ll_old)/ll_new )

        all_estimates.append(copy.deepcopy(components))

        if ll_old != 0 and ll_frac_delta < tol:
            print('tolerance reached')
            break

        ll_old = ll_new

    return ll_new, all_estimates
