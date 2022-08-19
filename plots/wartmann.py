####################################################
#                                                  #
#                     Imports                      #
#                                                  #
####################################################

import pandas as pd
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource
from plots.minkowski import configure_plot


####################################################
#                                                  #
#                  Helper Methods                  #
#                                                  #
####################################################

# reads data from files
def get_data(cohort_size, parameter):
    filename = "wartmann-" + cohort_size + parameter + ".csv"
    # skip first two rows
    df = pd.read_csv(filename, skiprows=[i for i in range(1, 3)])
    # only read every 3rd row
    df = df.iloc[::3, :]

    return df, ColumnDataSource(df)


# generates figure object
def get_figure():
    return figure(
        title="",
        x_axis_label="parameter value(s)",
        y_axis_label="recognition rate (%)",
        x_range=(1, 8),
        y_range=(0, 100),
        width=800,
        height=800
    )


# defines arguments used for line creation
def get_line_args(protocol):
    y = protocol + "_recog_rate (%)"
    alpha_args = dict(x='alpha', y=y, legend_label="increasing alpha only, beta = 1",
                      color=(31, 119, 180), line_width=3)
    beta_args = dict(x='beta', y=y, legend_label="increasing beta only, alpha = 1",
                     color=(255, 127, 14), line_width=3)
    both_args = dict(x='alpha', y=y, legend_label="increasing both simultaneously",
                     color=(44, 160, 44), line_width=3)

    return alpha_args, beta_args, both_args


# defines arguments used for quad creation
def get_quad_args(left, right, df, protocol, start, end):
    column = protocol + "_recog_rate (%)"
    return dict(left=left, right=right, top=max(df[column].iloc[start:end]), bottom=min(df[column].iloc[start:end]),
                color="black")


# used to generate plot
def generate_plot(cohort_size, protocol):
    _, source_alpha = get_data(cohort_size, "-alpha")
    _, source_beta = get_data(cohort_size, "-beta")
    _, source_both = get_data(cohort_size, "-both")
    df_quads, source_quads = get_data(cohort_size, "")

    plot = get_figure()

    alpha_args, beta_args, both_args = get_line_args(protocol)

    plot.line(source=source_alpha, **alpha_args)
    plot.line(source=source_beta, **beta_args)
    plot.line(source=source_both, **both_args)

    plot.quad(legend_label="1.25 ≤ beta ≤ 3.0", **get_quad_args(1.24, 1.26, df_quads, protocol, 0, 7))
    plot.quad(**get_quad_args(1.49, 1.51, df_quads, protocol, 7, 14))
    plot.quad(**get_quad_args(1.74, 1.76, df_quads, protocol, 14, 21))
    plot.quad(**get_quad_args(1.99, 2.01, df_quads, protocol, 21, 28))
    plot.quad(**get_quad_args(2.24, 2.26, df_quads, protocol, 28, 35))
    plot.quad(**get_quad_args(2.49, 2.51, df_quads, protocol, 35, 42))
    plot.quad(**get_quad_args(2.74, 2.76, df_quads, protocol, 42, 49))
    plot.quad(**get_quad_args(2.99, 3.01, df_quads, protocol, 49, 56))

    configure_plot(plot, protocol)

    show(plot)


####################################################
#                                                  #
#                   Execution                      #
#                                                  #
####################################################

generate_plot("small", "close")
generate_plot("small", "medium")
generate_plot("small", "far")
generate_plot("large", "close")
generate_plot("large", "medium")
generate_plot("large", "far")
