import copy
import numpy as np
import scipy.stats
import fitna


def do_em(data, initial_estimates=None, tol=1e-6, max_iter=50):

    components = []

    if initial_estimates is None:
        data_cov = np.cov(data.T)
        data_mean = np.mean(data.T, axis=1)

        max_eigen = np.amax(data_cov.diagonal())
        # Extract and construct a diagonal array from data_cov
        data_cov = np.diag(np.diag(data_cov))
        np.fill_diagonal(data_cov, max_eigen)

        estimate = fitna.data.NormalDist(norm=1, mean=data_mean, cov=data_cov)
        components.append(estimate)
    else:
        # Copy initial estimates to a local list
        # The local list may change size in the future
        components = copy.deepcopy(initial_estimates)

    all_estimates = []
    # Add initial estimates
    all_estimates.append(copy.deepcopy(components))

    all_memb_probs = []

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
        memb_probs_indep = np.zeros((n_components, n_points))

        for ic, component in enumerate(components):
            for ip in range(n_points):
                memb_probs[ic, ip] = component.norm * scipy.stats.multivariate_normal(component.mean, component.cov).pdf(data[ip])
            component_max_prob = np.amax(memb_probs[ic,:])
            memb_probs_indep[ic, :] = memb_probs[ic, :] / component_max_prob

        memb_probs = memb_probs / memb_probs.sum(0)


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

        # For each cluster calculate new (weighted) covariances given the probabilities
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
        all_memb_probs.append(memb_probs_indep)

        if ll_old != 0 and ll_frac_delta < tol:
            print('break: Tolerance reached')
            break

        ll_old = ll_new

    # Add a dummy entry
    all_memb_probs.append(all_memb_probs[-1])

    return ll_new, all_estimates, all_memb_probs
