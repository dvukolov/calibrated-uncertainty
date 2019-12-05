# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.2.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# Install NumPyro by running:
# `$ pip install numpyro`

# +
from functools import partial

# Import regular numpy in additional to JAX's
import numpy
import scipy.stats

import matplotlib.pyplot as plt
# %matplotlib inline

# %run helpers.ipynb

# +
# Compute on a CPU using 2 cores
numpyro.set_platform('cpu')
numpyro.set_host_device_count(2)

# Make plots larger by default
plt.rc('figure', dpi=100)


# +
# Define the true function and generate observations
def func(x):
    std = np.abs(x) * 0.5
    std = np.where(std < 0.5, 0.5, std)
    return scipy.stats.norm(loc=0.1 * x**3, scale=std)

func.latex = r'$y_i = 0.1x_i^3 + \varepsilon_i$'

data_points = [
    { 'n_points': 50, 'xlim': [-4, 4] },
]
df = generate_data(func, points=data_points, seed=2)

# Plot the data
plot_true_function(func, df, title=f'True Function: {func.latex}')

# +
# Observations
X = df[['x']].values
Y = df[['y']].values

# Number of hidden layers
hidden = 2
# Width of hidden layers
width = 10
# Standard deviation of the prior
sigma = 1.5
# Standard deviation of the likelihood
noise = 0.5

# Instantiate the model
model = partial(feedforward, X=X, Y=Y, width=width, hidden=hidden, sigma=sigma, noise=noise)

# +
# %%time
# Sampler parameters
num_chains = 2
num_samples = 2000
num_warmup = 2000

# Run the No-U-Turn sampler. Note: sampling more than one chain in parallel doesn't show a progress bar.
mcmc = sample(model, num_samples, num_warmup, num_chains, seed=0, summary=True)

# +
# Generate posterior predictive
X_test = numpy.linspace(df.x.min(), df.x.max(), num=1000)[:, np.newaxis]
posterior_predictive = simulate_posterior_predictive(model, mcmc, X_test, seed=1)

# Plot the results: truth vs prediction
plot_posterior_predictive(X_test, posterior_predictive, func=func, df=df,
                          title=f'NUTS, Weight Uncertainty {sigma}, Noise {noise},\n'
                                f'{width} Nodes in {hidden} Hidden Layer')
# -


