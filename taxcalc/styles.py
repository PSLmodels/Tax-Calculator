from bokeh.plotting import figure

DATETIME_FORMAT = dict(
    microseconds=["%m/%d %X"],
    milliseconds=["%X"],
    seconds=["%X"],
    minsec=["%X"],
    minutes=["%H:%M"],
    hourmin=["%H:%M"],
    hours=["%H:%M"],
    days=["%m/%d"],
)

FONT = "Helvetica"
FONT_SIZE = "10pt"

NODATA_COLOR = "#eeeeee"
GRAY = "#CCCCCC"
DARK_GRAY = "#6B6B73"
BLUE = '#21bfd5'
RED = '#FF6666'
GREEN = '#32CD32'
PURPLE = '#C5007C'

AXIS_FORMATS = dict(
    minor_tick_in=None,
    minor_tick_out=None,
    major_tick_in=None,
    major_label_text_font=FONT,
    major_label_text_font_size="8pt",
    axis_label_text_font=FONT,
    axis_label_text_font_style="italic",
    axis_label_text_font_size="8pt",

    axis_line_color=DARK_GRAY,
    major_tick_line_color=DARK_GRAY,
    major_label_text_color=DARK_GRAY,

    major_tick_line_cap="round",
    axis_line_cap="round",
    axis_line_width=1,
    major_tick_line_width=1,
)
PLOT_FORMATS = dict(
    toolbar_location=None,
    outline_line_color="#FFFFFF",
    title_text_font=FONT,
    title_text_align='center',
    title_text_color=DARK_GRAY,
    title_text_font_size="9pt",
    title_text_baseline='bottom',
    min_border_left=0,
    min_border_right=10,
    min_border_top=5,
    min_border_bottom=0,
)
LINE_FORMATS = dict(
    line_cap='round',
    line_join='round',
    line_width=2
)

FONT_PROPS_SM = dict(
    text_font=FONT,
    text_font_size='8pt',
)

FONT_PROPS_MD = dict(
    text_font=FONT,
    text_font_size='10pt',
)

FONT_PROPS_LG = dict(
    text_font=FONT,
    text_font_size='12pt',
)

BLANK_AXIS = dict(
    minor_tick_in=None,
    minor_tick_out=None,
    major_tick_in=None,
    major_label_text_font=FONT,
    major_label_text_font_size="8pt",
    axis_label_text_font=FONT,
    axis_label_text_font_style="italic",
    axis_label_text_font_size="8pt",

    axis_line_color='white',
    major_tick_line_color='white',
    major_label_text_color='white',
    axis_label_text_color='white',

    major_tick_line_cap="round",
    axis_line_cap="round",
    axis_line_width=1,
    major_tick_line_width=1,
)
