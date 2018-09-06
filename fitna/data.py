import scipy


class NormalDist:

    def __init__(self, mean, cov, norm=1, size=100):
        self.norm = norm
        self.mean = mean
        self.cov  = cov
        self.size = size


    def __repr__(self):
        return "\nNormalDist{" + \
               " norm: " + str(self.norm) + "," + \
               " mean: " + str(self.mean.tolist()) + "," + \
               " cov:  " + str(self.cov.tolist()) + "," + \
               " size: " + str(self.size) + \
               " }\n"


class NormalMixture:

    def __init__(self, normal_dists):
        '''
        Takes a list of NormalDists
        '''

        # Additional checks on the input must be done here
        self.components = normal_dists


    def rvs(self):
        ''' Generates random points for the mixture '''

        points = []

        for component in self.components:
            sample = component.norm * scipy.stats.multivariate_normal.rvs(component.mean, component.cov, component.size).T
            points.append(sample)

        return points
