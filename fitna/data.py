import scipy


class NormalDist:

    def __init__(self, mean, cov, norm=1, size=100, name=None):
        self.norm = norm
        self.mean = mean
        self.cov  = cov
        self.size = size
        self.name = name if name is not None else 'normal_mean_{}_cov_{}'.format(mean, cov)


    def __repr__(self):
        return "\nNormalDist{" + \
               " norm: " + str(self.norm) + "," + \
               " mean: " + str(self.mean.tolist()) + "," + \
               " cov:  " + str(self.cov.tolist()) + "," + \
               " size: " + str(self.size) + \
               " }\n"


    def rvs(self):
        ''' Generates random sample for the mixture '''
        return self.norm * scipy.stats.multivariate_normal.rvs(self.mean, self.cov, self.size).T


class NormalMixture:

    def __init__(self, normal_dists):
        '''
        Takes a list of NormalDists
        '''

        # Additional checks on the input must be done here
        # Should check uniqueness of a distribution by its name?
        self.components = normal_dists

        # Random samples drawn from components and indexed by component.name
        self.datasets = {}


    def rvs(self):
        ''' Generates random samples for the mixture '''

        for component in self.components:
            sample = component.norm * scipy.stats.multivariate_normal.rvs(component.mean, component.cov, component.size).T
            self.datasets.update({component.name: sample})

        return list(self.datasets.values())
