import numpy as np
import scipy.stats

import matplotlib.pyplot as plt
from matplotlib import transforms
from matplotlib.patches import Rectangle


# Colors used for plotting the posterior predictives
COLORS = {
    "true": "tab:orange",
    "predicted": "tab:blue",
    "calibrated": "tab:pink",
    "observations": "lightgrey",
}
# Transparency for the posterior predictives
FILL_ALPHA = 0.15


def plot_true_function(func, df, title=None):
    x = np.linspace(df.x.min(), df.x.max(), num=1000)
    distribution = func(x)
    lower, upper = distribution.interval(0.95)

    plt.fill_between(
        x, lower, upper, color=COLORS["true"], alpha=FILL_ALPHA, label="True 95% Interval",
    )
    plt.scatter(df.x, df.y, s=10, color=COLORS["observations"], label="Observations")
    plt.plot(x, distribution.mean(), color=COLORS["true"], label="True Mean")
    if title is not None:
        plt.title(title)
    plt.legend(bbox_to_anchor=(1.04, 1), borderaxespad=0)


def plot_posterior_predictive(x, post_pred, title=None, func=None, df=None):
    """Plot the posterior predictive along with the observations and the true function
    """
    if func is not None and df is not None:
        plot_true_function(func, df)

    x = x.ravel()
    lower, upper = np.percentile(post_pred, [2.5, 97.5], axis=0)
    plt.fill_between(
        x,
        lower,
        upper,
        color=COLORS["predicted"],
        alpha=FILL_ALPHA,
        label=f"95% Predictive Interval",
    )
    plt.plot(x, post_pred.mean(axis=0), color=COLORS["predicted"], label=f"Predicted Mean")
    plt.title(title)
    plt.legend(bbox_to_anchor=(1.04, 1), borderaxespad=0)


def plot_illustration(ppc_func, df, conditionals=True, title=None):
    """Visualize the miscalibrated posterior predictive to illustrate
    the calibration algorithm.
    """
    # Plot the observations and 95% predictive interval
    fig, ax = plt.subplots(1, 1)
    x = np.linspace(df.x.min(), df.x.max(), num=1000)
    distribution = ppc_func(x)
    lower, upper = distribution.interval(0.95)

    ax.fill_between(
        x,
        lower,
        upper,
        color=COLORS["predicted"],
        alpha=FILL_ALPHA,
        label="95% Predictive Interval",
    )
    ax.scatter(df.x, df.y, s=10, color=COLORS["observations"], label="Observations")
    ax.plot(x, distribution.mean(), color=COLORS["predicted"], label="Predicted Mean")
    ax.set(xlabel="X", ylabel="Y")
    if title is not None:
        ax.set_title(title)
    ax.legend(bbox_to_anchor=(1.04, 1), borderaxespad=0)
    ax.set_ylim([-12, 12])

    if not conditionals:
        return

    # Plot the conditional distribution of Y given X=x_0
    ax2 = fig.add_axes([0.2, 0.235, 0.075, 0.4])
    ax2.axison = False

    base = ax2.transData
    rot = transforms.Affine2D().rotate_deg(90)

    x_ = np.linspace(-3, 3, num=100)
    density = scipy.stats.norm(loc=0, scale=0.75)
    ax2.plot(x_, density.pdf(x_), transform=rot + base, color="tab:gray")

    # Plot the conditional distribution of Y given X=x_1
    ax3 = fig.add_axes([0.5, 0.405, 0.075, 0.2])
    ax3.axison = False

    base = ax3.transData
    rot = transforms.Affine2D().rotate_deg(90)

    x_ = np.linspace(-3, 3, num=100)
    density = scipy.stats.norm(loc=0, scale=0.55)
    ax3.plot(x_, density.pdf(x_), transform=rot + base, color="tab:gray")

    ax.annotate("$f(Y|x_0)$", [-3.23, 4])
    ax.annotate("$f(Y|x_1)$", [0.2, 3.5])


def plot_table(mark_y=False, show_quantiles=None):
    """Display a table, accompaining the step-by-step illustration of the algorithmm
    """
    if show_quantiles == "all":
        table_params = {"ncols": 5, "figsize": (10, 4)}
        columns = [
            "Observation",
            "PDF $f(Y|x_t)$",
            "CDF $H(x_t)$",
            "$H(x_t)(y_t)$",
            r"$\hat{P}(p)$",
        ]
    elif show_quantiles == "predicted":
        table_params = {"ncols": 4, "figsize": (8, 4)}
        columns = ["Observation", "PDF $f(Y|x_t)$", "CDF $H(x_t)$", "$H(x_t)(y_t)$"]
    else:
        table_params = {"ncols": 3, "figsize": (6, 4)}
        columns = ["Observation", "PDF $f(Y|x_t)$", "CDF $H(x_t)$"]

    fig, ax = plt.subplots(nrows=5, **table_params)

    for a in ax.flatten():
        a.set_xticklabels([])
        a.set_yticklabels([])
        a.set_xticks([])
        a.set_yticks([])
        a.margins(0.2)

    plt.subplots_adjust(wspace=0.0, hspace=0)

    for i, column in enumerate(columns):
        ax[0, i].set_title(column)

    rows = ["$(x_0, y_0)$", "$(x_1, y_1)$", r"$\ldots$", r"$\ldots$", "$(x_t, y_t)$"]
    for i, row in enumerate(rows):
        ax[i, 0].annotate(row, xy=[0.5, 0.5], size=15, ha="center", va="center")

    x_ = np.linspace(-3, 3, num=100)
    scales = [1, 0.5, 0.75, 1.25, 1.5]
    for i, std in enumerate(scales):
        ax[i, 1].plot(x_, scipy.stats.norm.pdf(x_, loc=0, scale=std))
        ax[i, 2].plot(x_, scipy.stats.norm.cdf(x_, loc=0, scale=std))

    # Illustrative predictive and empirical quantiles (obtained via isotonic regression)
    quantiles = [0.8, 0.8, 0.2, 0.4, 0.6]
    empirical = [0.638443, 0.638443, 0.3569105, 0.44220539, 0.56308756]

    if mark_y:
        for i, quantile in enumerate(quantiles):
            distribution = scipy.stats.norm(loc=0, scale=scales[i])
            value = distribution.ppf(quantile)
            ax[i, 1].plot([value] * 2, [0, distribution.pdf(value)], linestyle="--")
            ax[i, 2].plot([value] * 2, [0, distribution.cdf(value)], linestyle="--")

    if show_quantiles in ["predicted", "all"]:
        for i, quantile in enumerate(quantiles):
            ax[i, 3].annotate(quantile, xy=[0.5, 0.5], size=15, ha="center", va="center")

    if show_quantiles in ["all"]:
        for i, quantile in enumerate(empirical):
            ax[i, 4].annotate(f"{quantile:.2f}", xy=[0.5, 0.5], size=15, ha="center", va="center")

        ax4 = plt.gcf().add_axes([0.595, 0.59, 0.303, 0.28])
        ax4.axison = False
        ax4.add_patch(
            Rectangle(
                (0, 0.01),
                0.99,
                0.99,
                linewidth=1,
                linestyle="--",
                edgecolor="tab:red",
                facecolor="none",
            )
        )


def plot_ecdf(predicted_quantiles):
    plt.hist(predicted_quantiles, bins=50, cumulative=True, density=True, alpha=0.3)
    plt.title("CDF of Predicted Quantiles")
    plt.xlabel("Predicted Quantiles, $H(x_t)(y_t)$")
    plt.ylabel(r"Empirical Quantiles, $\hat{P}(p_t)$")


def calibration_plot(predicted_quantiles, model):
    """Visualize a calibration plot suggested by the authors
    """
    # Choose equally spaced quantiles
    expected_quantiles = np.linspace(0, 1, num=11).reshape(-1, 1)

    # Compute the probabilities of predicted quantiles at the discrete quantile levels
    T = predicted_quantiles.shape[0]
    observed_uncalibrated = (predicted_quantiles.reshape(1, -1) <= expected_quantiles).sum(
        axis=1
    ) / T

    # Use the model to output the actual probabilities of any quantile
    calibrated_quantiles = model.predict(predicted_quantiles)
    # Estimate the observed calibrated quantiles
    observed_calibrated = (calibrated_quantiles.reshape(1, -1) <= expected_quantiles).sum(
        axis=1
    ) / T

    # Plot the results
    plt.plot(
        expected_quantiles,
        observed_uncalibrated,
        marker="o",
        color=COLORS["predicted"],
        label="Uncalibrated",
    )
    plt.plot(
        expected_quantiles,
        observed_calibrated,
        marker="o",
        color=COLORS["calibrated"],
        label="Calibrated",
    )
    plt.plot([0, 1], [0, 1], color="tab:grey", linestyle="--", zorder=0)
    plt.title("Calibration Plot")
    plt.xlabel("Expected Quantiles")
    plt.ylabel("Observed Quantiles")
    plt.legend()


def plot_calibration(x, post_pred, qc, df, func):
    """Plot the posterior predictive before and after calibration
    """
    x = x.ravel()
    q = [0.025, 0.5, 0.975]
    quantiles = [q, qc.inverse_transform(q)]
    titles = ["Before Calibration", "After Calibration"]

    fig, ax = plt.subplots(1, 2, figsize=(8.5, 3.5), sharex=True, sharey=True)

    for i, axis in enumerate(ax):
        # Plot the true function
        distribution = func(x)
        lower, upper = distribution.interval(0.95)
        true_interval = axis.fill_between(
            x, lower, upper, color=COLORS["true"], alpha=FILL_ALPHA, label="True 95% Interval",
        )
        axis.scatter(df.x, df.y, s=3, color=COLORS["observations"], label="Observations")
        true_median = axis.plot(x, distribution.median(), color=COLORS["true"], label="True Median")
        axis.set_title(titles[i])

        lower, median, upper = np.quantile(post_pred, quantiles[i], axis=0)
        predicted_interval = axis.fill_between(
            x,
            lower,
            upper,
            color=COLORS["predicted"],
            alpha=FILL_ALPHA,
            label=f"95% Predictive Interval",
        )
        predicted_median = axis.plot(
            x, median, color=COLORS["predicted"], label=f"Predicted Median"
        )

    handles = [true_interval, true_median[0], predicted_interval, predicted_median[0]]
    labels = [h.get_label() for h in handles]
    fig.legend(handles, labels, loc="lower center", ncol=len(labels))
    fig.tight_layout(rect=(0, 0.1, 1, 1))


def check_convergence(res_main, res_holdout, func, debug_mode=True):
    if not debug_mode:
        # Do not plot posterior predictives if in production mode
        return

    data = {"main dataset": res_main, "hold-out dataset": res_holdout}
    for name, res in data.items():
        plt.figure()
        plot_posterior_predictive(
            res["X_test"], res["post_pred"], func=func, df=res["df"], title=name,
        )

        # Print the diagnostic tests
        diagnostics = get_metrics(res["mcmc"])
        message = ("Minimum ESS: {min_ess:,.2f}\n" "Max Gelman-Rubin: {max_rhat:.2f}").format(
            **diagnostics
        )
        plt.gcf().text(0.95, 0.15, message)
