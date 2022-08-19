####################################################
#                                                  #
#                     Imports                      #
#                                                  #
####################################################

import pandas as pd
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource


####################################################
#                                                  #
#                  Helper Methods                  #
#                                                  #
####################################################

# reads data from files
def get_data(cohort_size, preprocessing_method):
    filename = "minkowski-" + cohort_size + "-" + preprocessing_method + ".csv"
    # skip first two rows
    df = pd.read_csv(filename, skiprows=[i for i in range(1, 3)])
    # only read every 3rd row
    df = df.iloc[::3, :]

    return ColumnDataSource(df)


# generates figure object
def get_figure():
    return figure(
        title="",
        x_axis_label="p-value",
        y_axis_label="recognition rate (%)",
        x_range=(0, 5),
        y_range=(0, 100),
        width=800,
        height=800
    )


# defines arguments used for line creation
def get_line_args(protocol):
    y = protocol + "_recog_rate (%)"
    standardize_args = dict(x='parameter_value', y=y, legend_label="standardize",
                            color=(31, 119, 180), line_width=3)
    subtract_mean_args = dict(x='parameter_value', y=y, legend_label="subtract_mean",
                              color=(255, 127, 14), line_width=3)
    omitted_args = dict(x='parameter_value', y=y, legend_label="omitted", color=(44, 160, 44), line_width=3)

    return standardize_args, subtract_mean_args, omitted_args


# defines plot styles
def configure_plot(plot, protocol):
    plot.legend.location = "bottom_right"
    plot.legend.label_text_font_size = "25px"
    plot.axis.axis_label_text_font_size = "25px"
    plot.axis.axis_line_width = 2
    plot.axis.major_label_text_font_size = "25px"
    plot.axis.major_tick_line_width = 2
    plot.axis.minor_tick_line_width = 2

    if protocol == "far":
        plot.legend.location = "top_left"


# used to generate plot
def generate_plot(cohort_size, protocol):
    source_standardize = get_data(cohort_size, "standardize")
    source_subtract_mean = get_data(cohort_size, "subtract-mean")
    source_omitted = get_data(cohort_size, "omitted")

    plot = get_figure()

    standardize_args, subtract_mean_args, omitted_args = get_line_args(protocol)

    plot.line(source=source_standardize, **standardize_args)
    plot.line(source=source_subtract_mean, **subtract_mean_args)
    plot.line(source=source_omitted, **omitted_args)

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
