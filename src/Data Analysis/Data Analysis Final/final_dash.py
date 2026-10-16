import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
 
CSV_PATH = r"201902-fordgobike-tripdata.csv"
# Design tokens — one palette, one type scale, reused everywhere below.
# ----------------------------------------------------------------------------
COLORS = {
    "bg": "#EEF1F5",             # app background
    "surface": "#FFFFFF",        # card background
    "border": "#E3E8EE",
    "ink": "#182430",            # primary text
    "muted": "#68748259" if False else "#67727E",   # secondary text
    "navy": "#0F3057",           # brand / primary accent
    "navy_dark": "#0A2140",
    "teal": "#1C8C8C",           # secondary accent
    "coral": "#F0654B",          # highlight accent
    "sand": "#F0A83E",           # tertiary accent
    "grid": "#EEF1F5",
    "heat_lo": "#EAF1F8",
    "heat_hi": "#0F3057",
}
CATEGORICAL = [COLORS["navy"], COLORS["teal"], COLORS["coral"], COLORS["sand"], "#7E9CB5", "#9B6BB0"]
FONT = "Inter, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif"
CARD_SHADOW = "0 1px 2px rgba(15,48,87,0.05), 0 10px 24px -16px rgba(15,48,87,0.28)"
 
PLOTLY_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        font=dict(family=FONT, color=COLORS["ink"], size=12.5),
        paper_bgcolor=COLORS["surface"],
        plot_bgcolor=COLORS["surface"],
        colorway=CATEGORICAL,
        title=dict(font=dict(size=14.5, color=COLORS["ink"]), x=0.0, xanchor="left", pad=dict(b=10)),
        margin=dict(l=44, r=20, t=46, b=36),
        xaxis=dict(gridcolor=COLORS["grid"], zeroline=False, showline=False),
        yaxis=dict(gridcolor=COLORS["grid"], zeroline=False, showline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1, font=dict(size=11)),
        hoverlabel=dict(bgcolor=COLORS["surface"], font_family=FONT, bordercolor=COLORS["border"]),
    )
)
 
WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WEEKDAY_SHORT = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTH_ORDER = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
 
 
# ----------------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------------
def generate_dummy(n=4000, seed=7):
    rng = np.random.default_rng(seed)
    hours = pd.date_range("2019-02-01", "2019-02-28 23:00", freq="h")
    weights = np.array([1.0 + 1.8 * (h in (7, 8, 9, 17, 18, 19)) for h in hours.hour])
    weights = weights / weights.sum()
    start = rng.choice(hours, size=n, p=weights)
    dur = rng.exponential(scale=480, size=n).astype(int) + 60  # seconds
    stations = {
        "Market St @ 7th": (37.7766, -122.4172),
        "Howard St @ 2nd St": (37.7871, -122.3969),
        "Embarcadero @ Sansome": (37.8043, -122.4033),
        "Mission St @ 3rd": (37.7845, -122.4029),
        "Van Ness Ave @ Market": (37.7749, -122.4194),
        "Steuart St @ Market": (37.7940, -122.3948),
    }
    names = list(stations.keys())
    start_idx = rng.integers(0, len(names), size=n)
    end_idx = rng.integers(0, len(names), size=n)
    df = pd.DataFrame({
        "trip_id": range(1, n + 1),
        "start_time": start,
        "duration_sec": dur,
        "start_station_name": [names[i] for i in start_idx],
        "end_station_name": [names[i] for i in end_idx],
        "start_station_latitude": [stations[names[i]][0] + rng.normal(0, 0.0015) for i in start_idx],
        "start_station_longitude": [stations[names[i]][1] + rng.normal(0, 0.0015) for i in start_idx],
        "user_type": rng.choice(["Subscriber", "Customer"], size=n, p=[0.75, 0.25]),
        "member_gender": rng.choice(["Male", "Female", "Other"], size=n, p=[0.55, 0.4, 0.05]),
        "age": rng.integers(18, 70, size=n),
    })
    df["day_of_week"] = df["start_time"].dt.day_name()
    df["month"] = df["start_time"].dt.strftime("%b")
    df["age_group"] = pd.cut(df["age"], bins=[0, 29, 50, 200], labels=["Young", "Adult", "Senior"])
    return df
 
 
def load_data():
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH, parse_dates=["start_time"])
        print(f"[info] loaded {len(df):,} rows from {CSV_PATH}")
    else:
        print(f"[warning] {CSV_PATH} not found — generating a dummy dataset so the dashboard still runs.")
        df = generate_dummy()
 
    df["start_time"] = pd.to_datetime(df["start_time"])
    df["trip_duration_min"] = df["duration_sec"] / 60.0
    if "day_of_week" not in df.columns:
        df["day_of_week"] = df["start_time"].dt.day_name()
    if "month" not in df.columns:
        df["month"] = df["start_time"].dt.strftime("%b")
    if "hour" not in df.columns:
        df["hour"] = df["start_time"].dt.hour
    if "age_group" not in df.columns and "age" in df.columns:
        df["age_group"] = pd.cut(df["age"], bins=[0, 29, 50, 200], labels=["Young", "Adult", "Senior"])
    return df
 
 
df = load_data()
 
user_types = sorted(df["user_type"].dropna().unique())
genders = sorted(df["member_gender"].dropna().unique())
age_groups = [a for a in ["Young", "Adult", "Senior"] if a in df["age_group"].dropna().astype(str).unique().tolist()] \
    or sorted(df["age_group"].dropna().astype(str).unique())
has_end_station = "end_station_name" in df.columns
 
DUR_MIN = float(np.floor(df["trip_duration_min"].min()))
DUR_MAX = float(np.ceil(df["trip_duration_min"].max()))
duration_marks = {
    int(DUR_MIN): f"{int(DUR_MIN)}m",
    int(DUR_MAX): f"{int(DUR_MAX)}m",
}
_mid = int((DUR_MIN + DUR_MAX) / 2)
if DUR_MAX - DUR_MIN > 20:
    duration_marks[_mid] = f"{_mid}m"
 
station_view_options = [{"label": "Top start stations", "value": "start"}]
if has_end_station:
    station_view_options += [
        {"label": "Top end stations", "value": "end"},
        {"label": "Top routes", "value": "routes"},
    ]
 
app = Dash(__name__)
app.title = "Ford GoBike Dashboard"
 
_INDEX_CSS = """
* { box-sizing: border-box; }
html, body { margin: 0; background: __BG__; font-family: __FONT__; }
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-thumb { background: __BORDER__; border-radius: 4px; }
.Select-control, .dash-dropdown .Select-control {
  border-radius: 8px !important; border-color: __BORDER__ !important; font-size: 13px !important;
}
.DateInput_input { font-family: __FONT__ !important; font-size: 13px !important; }
.DateRangePickerInput { border-radius: 8px !important; overflow: hidden; }
.rc-slider-track { background-color: __NAVY__ !important; }
.rc-slider-handle { border-color: __NAVY__ !important; }
.rc-slider-handle:hover, .rc-slider-handle:active { border-color: __NAVY__ !important; }
.rc-slider-dot-active { border-color: __NAVY__ !important; }
input[type="radio"] { accent-color: __NAVY__; }
input[type="checkbox"] { accent-color: __NAVY__; }
""".replace("__BG__", COLORS["bg"]).replace("__BORDER__", COLORS["border"]) \
    .replace("__FONT__", FONT).replace("__NAVY__", COLORS["navy"])
 
app.index_string = """<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>""" + _INDEX_CSS + """</style>
    </head>
    <body>
        {%app_entry%}
        <footer>{%config%}{%scripts%}{%renderer%}</footer>
    </body>
</html>"""
 
 
# ----------------------------------------------------------------------------
# Reusable layout pieces
# ----------------------------------------------------------------------------
def section_header(title, subtitle, dot_color):
    return html.Div([
        html.Div([
            html.Span(style={
                "display": "inline-block", "width": "8px", "height": "8px", "borderRadius": "50%",
                "background": dot_color, "marginRight": "9px",
            }),
            html.Span(title, style={"fontSize": "16.5px", "fontWeight": "700", "color": COLORS["ink"]}),
        ], style={"display": "flex", "alignItems": "center"}),
        html.P(subtitle, style={
            "fontSize": "12.5px", "color": COLORS["muted"], "margin": "5px 0 0 17px",
        }),
    ], style={"marginBottom": "14px"})
 
 
def card(children, style=None):
    base = {
        "background": COLORS["surface"], "borderRadius": "14px",
        "border": f"1px solid {COLORS['border']}", "boxShadow": CARD_SHADOW, "padding": "18px 20px",
    }
    base.update(style or {})
    return html.Div(children, style=base)
 
 
def kpi_card(label, value, sub, accent, icon):
    return html.Div([
        html.Div([
            html.Div(icon, style={
                "fontSize": "18px", "width": "38px", "height": "38px", "borderRadius": "10px",
                "background": f"{accent}17", "display": "flex", "alignItems": "center",
                "justifyContent": "center",
            }),
        ]),
        html.Div(value, style={
            "fontSize": "25px", "fontWeight": "800", "color": COLORS["ink"], "lineHeight": "1.15",
            "marginTop": "14px",
        }),
        html.Div(label, style={"fontSize": "12.5px", "color": COLORS["muted"], "marginTop": "2px"}),
        html.Div(sub, style={"fontSize": "11px", "color": accent, "marginTop": "8px", "fontWeight": "600"}),
    ], style={
        "background": COLORS["surface"], "borderRadius": "14px", "border": f"1px solid {COLORS['border']}",
        "boxShadow": CARD_SHADOW, "padding": "18px 20px", "flex": "1", "minWidth": "180px",
        "borderTop": f"3px solid {accent}",
    })
 
 
def filter_label(text, top="18px"):
    return html.Label(text, style={
        "fontSize": "11.5px", "fontWeight": "600", "color": COLORS["muted"],
        "display": "block", "marginBottom": "7px", "marginTop": top,
    })
 
 
dropdown_style = {"fontSize": "13px"}
 
# ----------------------------------------------------------------------------
# Layout — top navbar
# ----------------------------------------------------------------------------
navbar = html.Div([
    html.Div([
        html.Span("🚲", style={"fontSize": "20px", "marginRight": "10px"}),
        html.Div([
            html.Div("Ford GoBike", style={"fontSize": "16px", "fontWeight": "800", "color": "#FFFFFF", "lineHeight": "1.1"}),
            html.Div("Trip Analytics Dashboard", style={"fontSize": "11.5px", "color": "#AFC3D8"}),
        ]),
    ], style={"display": "flex", "alignItems": "center"}),
    html.Div(
        f"Data: {df['start_time'].min().strftime('%b %d, %Y')} – {df['start_time'].max().strftime('%b %d, %Y')}",
        style={
            "fontSize": "12px", "color": "#DCE7F2", "background": "rgba(255,255,255,0.08)",
            "padding": "7px 14px", "borderRadius": "999px", "border": "1px solid rgba(255,255,255,0.14)",
        },
    ),
], style={
    "display": "flex", "justifyContent": "space-between", "alignItems": "center",
    "background": f"linear-gradient(135deg, {COLORS['navy']}, {COLORS['navy_dark']})",
    "padding": "16px 28px", "position": "sticky", "top": "0", "zIndex": "10",
})
 
# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
sidebar = html.Div([
    html.Div("Filters", style={"fontSize": "13px", "fontWeight": "700", "color": COLORS["ink"], "letterSpacing": "0.2px"}),
    html.Div("Every chart updates instantly.", style={"fontSize": "11.5px", "color": COLORS["muted"], "marginTop": "2px"}),
 
    filter_label("Date range"),
    dcc.DatePickerRange(
        id="date_range",
        min_date_allowed=df["start_time"].min().date(),
        max_date_allowed=df["start_time"].max().date(),
        start_date=df["start_time"].min().date(),
        end_date=df["start_time"].max().date(),
        display_format="MMM D, YYYY",
    ),
 
    filter_label("User type"),
    dcc.Dropdown(id="user_type", options=[{"label": u, "value": u} for u in user_types],
                 value=[], multi=True, placeholder="All user types", style=dropdown_style),
 
    filter_label("Gender"),
    dcc.Dropdown(id="gender", options=[{"label": g, "value": g} for g in genders],
                 value=[], multi=True, placeholder="All genders", style=dropdown_style),
 
    filter_label("Age group"),
    dcc.Checklist(
        id="age_group",
        options=[{"label": " " + a, "value": a} for a in age_groups],
        value=age_groups,
        style={"fontSize": "13px", "color": COLORS["ink"]},
        labelStyle={"display": "block", "marginBottom": "6px"},
    ),
 
    filter_label("Trip duration (minutes)"),
    html.Div(
        dcc.RangeSlider(
            id="duration_range", min=DUR_MIN, max=DUR_MAX, value=[DUR_MIN, DUR_MAX],
            marks=duration_marks, tooltip={"placement": "bottom", "always_visible": False},
            allowCross=False,
        ),
        style={"padding": "0 4px"},
    ),
 
    html.Div("💡 Tip: combine the age, gender and duration filters to spot niche riding patterns.", style={
        "fontSize": "11.5px", "color": COLORS["muted"], "marginTop": "26px",
        "padding": "10px 12px", "background": COLORS["bg"], "borderRadius": "10px",
        "border": f"1px solid {COLORS['border']}", "lineHeight": "1.5",
    }),
], style={
    "width": "270px", "minWidth": "270px", "padding": "22px 20px", "background": COLORS["surface"],
    "borderRight": f"1px solid {COLORS['border']}", "height": "calc(100vh - 64px)", "overflowY": "auto",
    "position": "sticky", "top": "64px",
})
 
# ----------------------------------------------------------------------------
# Main content
# ----------------------------------------------------------------------------
main = html.Div([
 
    # 1. Overview KPIs
    html.Div(id="kpi_row", style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "30px"}),
 
    # 2. Time Analysis
    html.Div([
        section_header("Time Analysis", "When trips happen — by day of week, month, and time of day.", COLORS["teal"]),
        html.Div([
            card(dcc.Graph(id="trips_by_weekday", config={"displayModeBar": False}), style={"flex": "1", "minWidth": "320px"}),
            card(dcc.Graph(id="trips_by_month", config={"displayModeBar": False}), style={"flex": "1", "minWidth": "320px"}),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "16px"}),
        card(dcc.Graph(id="hour_heatmap", config={"displayModeBar": False})),
    ], style={"marginBottom": "30px"}),
 
    # 3. User Analysis
    html.Div([
        section_header("User Analysis", "Who is riding — trip duration, age, gender, and subscriber mix.", COLORS["coral"]),
        html.Div([
            card(dcc.Graph(id="duration_distribution", config={"displayModeBar": False}), style={"flex": "1", "minWidth": "320px"}),
            card(dcc.Graph(id="age_distribution", config={"displayModeBar": False}), style={"flex": "1", "minWidth": "320px"}),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "16px"}),
        html.Div([
            card(dcc.Graph(id="gender_split", config={"displayModeBar": False}), style={"flex": "1", "minWidth": "260px"}),
            card(dcc.Graph(id="user_type_split", config={"displayModeBar": False}), style={"flex": "1", "minWidth": "260px"}),
            card(dcc.Graph(id="duration_by_age", config={"displayModeBar": False}), style={"flex": "1", "minWidth": "260px"}),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}),
    ], style={"marginBottom": "30px"}),
 
    # 4. Station & Trip Analysis
    html.Div([
        section_header("Station & Trip Analysis", "Where trips start and end, and the busiest routes.", COLORS["sand"]),
        html.Div([
            card(dcc.Graph(id="station_map", config={"displayModeBar": False}), style={"flex": "1.4", "minWidth": "360px"}),
            card([
                dcc.RadioItems(
                    id="station_view",
                    options=station_view_options, value="start",
                    inline=True,
                    style={"fontSize": "12.5px", "color": COLORS["ink"], "marginBottom": "8px"},
                    labelStyle={"marginRight": "14px"},
                ),
                dcc.Graph(id="station_bar", config={"displayModeBar": False}),
            ], style={"flex": "1", "minWidth": "300px"}),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}),
    ], style={"marginBottom": "10px"}),
 
    html.Div(id="footer", style={"height": "16px"}),
], style={"flex": "1", "padding": "26px 30px", "minWidth": "0"})
 
app.layout = html.Div([
    navbar,
    html.Div([sidebar, main], style={"display": "flex"}),
], style={"fontFamily": FONT, "background": COLORS["bg"], "minHeight": "100vh"})
 
 
# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def empty_figure(message):
    fig = go.Figure()
    fig.update_layout(template=PLOTLY_TEMPLATE, height=280)
    fig.add_annotation(text=message, showarrow=False, font=dict(size=13, color=COLORS["muted"]))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig
 
 
def donut(labels, values, colors, title):
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.6, marker=dict(colors=colors),
        textinfo="percent", sort=False,
    ))
    fig.update_layout(template=PLOTLY_TEMPLATE, title=title, height=300)
    return fig
 
 
# ----------------------------------------------------------------------------
# Main callback
# ----------------------------------------------------------------------------
@app.callback(
    Output("kpi_row", "children"),
    Output("trips_by_weekday", "figure"),
    Output("trips_by_month", "figure"),
    Output("hour_heatmap", "figure"),
    Output("duration_distribution", "figure"),
    Output("age_distribution", "figure"),
    Output("gender_split", "figure"),
    Output("user_type_split", "figure"),
    Output("duration_by_age", "figure"),
    Output("station_map", "figure"),
    Output("station_bar", "figure"),
    [
        Input("date_range", "start_date"),
        Input("date_range", "end_date"),
        Input("user_type", "value"),
        Input("gender", "value"),
        Input("age_group", "value"),
        Input("duration_range", "value"),
        Input("station_view", "value"),
    ],
)
def update(start_date, end_date, user_type, gender, age_group, duration_range, station_view):
    dff = df.copy()
    if start_date:
        dff = dff[dff["start_time"] >= pd.to_datetime(start_date)]
    if end_date:
        dff = dff[dff["start_time"] <= pd.to_datetime(end_date) + pd.Timedelta(days=1)]
    if user_type:
        dff = dff[dff["user_type"].isin(user_type)]
    if gender:
        dff = dff[dff["member_gender"].isin(gender)]
    if age_group:
        dff = dff[dff["age_group"].astype(str).isin([str(a) for a in age_group])]
    if duration_range:
        lo, hi = duration_range
        dff = dff[(dff["trip_duration_min"] >= lo) & (dff["trip_duration_min"] <= hi)]
 
    # ---- KPIs ----
    total_trips = len(dff)
    total_all = len(df)
    avg_dur = dff["trip_duration_min"].mean() if total_trips else 0
    active_users = dff["user_id"].nunique() if "user_id" in dff.columns else (dff["trip_id"].nunique() if "trip_id" in dff.columns else dff["bike_id"].nunique())
    popular_station = dff["start_station_name"].mode().iloc[0] if not dff.empty else "N/A"
    share = (total_trips / total_all * 100) if total_all else 0
 
    kpis = [
        kpi_card("Total trips", f"{total_trips:,}", f"{share:.0f}% of all {total_all:,} trips", COLORS["navy"], "🚲"),
        kpi_card("Avg. duration", f"{avg_dur:.1f} min", "across selected trips", COLORS["teal"], "⏱"),
        kpi_card("Active riders", f"{active_users:,}", "unique riders in view", COLORS["coral"], "👤"),
        kpi_card("Top station", popular_station, "most frequent trip start", COLORS["sand"], "📍"),
    ]
 
    if dff.empty:
        empty = empty_figure("No trips match the current filters — try widening them.")
        return kpis, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty
 
    # ---- Trips by weekday (required) ----
    trips_wd = dff["day_of_week"].value_counts().reindex(WEEKDAY_ORDER).fillna(0)
    fig_weekday = go.Figure(go.Scatter(
        x=WEEKDAY_SHORT, y=trips_wd.values, mode="lines+markers",
        line=dict(color=COLORS["navy"], width=2.5), marker=dict(size=7, color=COLORS["navy"]),
        fill="tozeroy", fillcolor="rgba(15, 48, 87, 0.08)",
    ))
    fig_weekday.update_layout(template=PLOTLY_TEMPLATE, title="Trips per day of week", height=300)
 
    # ---- Trips by month ----
    trips_month = dff["month"].value_counts().reindex(MONTH_ORDER).dropna()
    fig_month = go.Figure(go.Bar(x=trips_month.index, y=trips_month.values,
                                  marker=dict(color=COLORS["teal"])))
    fig_month.update_layout(template=PLOTLY_TEMPLATE, title="Trips by month", height=300)
 
    # ---- Hour-of-day x weekday heatmap ----
    pivot = (dff.groupby(["day_of_week", "hour"]).size()
             .unstack(fill_value=0).reindex(WEEKDAY_ORDER))
    pivot = pivot.reindex(columns=range(24), fill_value=0)
    fig_heat = go.Figure(go.Heatmap(
        z=pivot.values, x=[f"{h:02d}:00" for h in pivot.columns], y=WEEKDAY_SHORT,
        colorscale=[[0, COLORS["heat_lo"]], [1, COLORS["heat_hi"]]],
        colorbar=dict(title="Trips", thickness=12, len=0.9),
        hovertemplate="%{y}, %{x}<br>%{z} trips<extra></extra>",
    ))
    fig_heat.update_layout(template=PLOTLY_TEMPLATE, title="Trip volume by hour of day and weekday",
                            height=280, xaxis=dict(showgrid=False), yaxis=dict(showgrid=False, autorange="reversed"))
 
    # ---- Trip duration distribution (required) ----
    dur_capped = dff["trip_duration_min"].clip(upper=dff["trip_duration_min"].quantile(0.98))
    fig_dur = px.histogram(x=dur_capped, nbins=30, template=PLOTLY_TEMPLATE,
                            color_discrete_sequence=[COLORS["navy"]])
    fig_dur.update_layout(title="Trip duration distribution (98th pct. capped)", bargap=0.06,
                           showlegend=False, height=300)
    fig_dur.update_xaxes(title="Duration (minutes)")
    fig_dur.update_yaxes(title="Trips")
 
    # ---- Age distribution ----
    fig_age = px.histogram(dff, x="age", nbins=15, template=PLOTLY_TEMPLATE,
                            color_discrete_sequence=[COLORS["coral"]])
    fig_age.update_layout(title="Age distribution", bargap=0.08, showlegend=False, height=300)
    fig_age.update_yaxes(title="Trips")
    fig_age.update_xaxes(title="Age")
 
    # ---- Gender split ----
    gender_counts = dff["member_gender"].value_counts().reset_index()
    gender_counts.columns = ["gender", "trips"]
    fig_gender = donut(gender_counts["gender"], gender_counts["trips"], CATEGORICAL, "Gender split")
 
    # ---- User type split (required) ----
    type_counts = dff["user_type"].value_counts().reset_index()
    type_counts.columns = ["user_type", "trips"]
    fig_type = donut(type_counts["user_type"], type_counts["trips"],
                      [COLORS["navy"], COLORS["sand"], COLORS["teal"]], "Subscriber vs. Customer")
 
    # ---- Avg duration by age group ----
    if "age_group" in dff.columns and dff["age_group"].notna().any():
        by_age = dff.groupby(dff["age_group"].astype(str))["trip_duration_min"].mean()
        order = [a for a in ["Young", "Adult", "Senior"] if a in by_age.index] or list(by_age.index)
        by_age = by_age.reindex(order)
        fig_dur_age = go.Figure(go.Bar(x=by_age.index, y=by_age.values, marker=dict(color=CATEGORICAL[:len(by_age)])))
        fig_dur_age.update_layout(template=PLOTLY_TEMPLATE, title="Avg. duration by age group", height=300)
        fig_dur_age.update_yaxes(title="Minutes")
    else:
        fig_dur_age = empty_figure("No age group data")
 
    # ---- Station map ----
    if {"start_station_latitude", "start_station_longitude"}.issubset(dff.columns):
        station_agg = (dff.groupby("start_station_name")
                        .agg(trips=("trip_id", "count") if "trip_id" in dff.columns else ("start_station_name", "count"),
                             lat=("start_station_latitude", "mean"),
                             lon=("start_station_longitude", "mean"))
                        .reset_index())
        if hasattr(px, "scatter_map"):
            fig_map = px.scatter_map(
                station_agg, lat="lat", lon="lon", size="trips", hover_name="start_station_name",
                zoom=12, color_discrete_sequence=[COLORS["navy"]], size_max=34,
            )
            fig_map.update_layout(map_style="open-street-map")
        else:
            fig_map = px.scatter_mapbox(
                station_agg, lat="lat", lon="lon", size="trips", hover_name="start_station_name",
                zoom=12, color_discrete_sequence=[COLORS["navy"]], size_max=34,
            )
            fig_map.update_layout(mapbox_style="open-street-map")
        fig_map.update_layout(
            template=PLOTLY_TEMPLATE, title="Trip starts by station (bubble size = trips)",
            margin=dict(l=0, r=0, t=48, b=0), height=430,
        )
    else:
        fig_map = empty_figure("No station coordinates in this dataset")
 
    # ---- Station bar (start / end / routes, driven by the toggle) ----
    if station_view == "end" and has_end_station:
        top = dff["end_station_name"].value_counts().nlargest(8).reset_index()
        top.columns = ["station", "trips"]
        fig_station_bar = go.Figure(go.Bar(x=top["trips"], y=top["station"], orientation="h",
                                            marker=dict(color=COLORS["coral"])))
        fig_station_bar.update_layout(template=PLOTLY_TEMPLATE, title="Top end stations", height=430,
                                       yaxis=dict(autorange="reversed"))
    elif station_view == "routes" and has_end_station:
        routes = (dff.groupby(["start_station_name", "end_station_name"]).size()
                  .nlargest(8).reset_index(name="trips"))
        routes["route"] = routes["start_station_name"] + " → " + routes["end_station_name"]
        fig_station_bar = go.Figure(go.Bar(x=routes["trips"], y=routes["route"], orientation="h",
                                            marker=dict(color=COLORS["sand"])))
        fig_station_bar.update_layout(template=PLOTLY_TEMPLATE, title="Top routes", height=430,
                                       yaxis=dict(autorange="reversed"))
    else:
        top = dff["start_station_name"].value_counts().nlargest(8).reset_index()
        top.columns = ["station", "trips"]
        fig_station_bar = go.Figure(go.Bar(x=top["trips"], y=top["station"], orientation="h",
                                            marker=dict(color=COLORS["navy"])))
        fig_station_bar.update_layout(template=PLOTLY_TEMPLATE, title="Top start stations", height=430,
                                       yaxis=dict(autorange="reversed"))
 
    return (kpis, fig_weekday, fig_month, fig_heat, fig_dur, fig_age, fig_gender, fig_type,
            fig_dur_age, fig_map, fig_station_bar)
 
 
if __name__ == "__main__":
    app.run(debug=True)