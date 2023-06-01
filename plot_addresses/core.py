import random
import re
import sys

import folium
from folium.elements import *
from sys import platform
# import creds
# not really platform specific, but i have a local version on mac and prod in linux so this is an easy way to
# change credentials for a local dev environment
if platform == "linux" or platform == "linux2":
    import creds.py
    LIMIT = sys.maxsize
elif platform == "darwin":
    import local_creds as creds
    LIMIT = 1
elif platform == "win32":
    import local_creds as creds

import json

# from current project in case I make this a package
try:
    from .helpers import get_connection
except:
    from helpers import get_connection
try:
    from . import queries
except:
    import queries

TEMPLATE_DIRECTORY = '../analytics_project/dashboard/templates/dashboard/'
STATIC_DIRECTORY = '../analytics_project/dashboard/static/dashboard/html/'
STATIC_DIRECTORY_2 = '../analytics_project/static/dashboard/html/'
JSON_DIRECTORY = '../analytics_project/dashboard/static/dashboard/json/'

NASHVILLE_LATITUDE = 36.164577
NASHVILLE_LONGITUDE = -86.776949


def get_popup_html(connection, neighborhood):
    get_sale_rows_sql = queries.get_sales_rows.format(neighborhood)
    rows = get_result_set(connection, get_sale_rows_sql)
    html_out = """<table style="width:100%">
  <tr>
    <th>Week of</th>
    <th>Sales</th>
  </tr>"""
    for row in rows:
        html_out = html_out + """<tr>
            <td>{0}</td>
            <td>{1}</td>
          </tr>""".format(row[0], row[1])
    html_out = html_out + "</table>"
    return html_out


def get_result_set(connection, sql):
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    return rows


def main():
    cnx = get_connection(creds.aws_user, creds.aws_pass,
                          creds.aws_host,
                          creds.aws_database)

    if cnx:
        print("got connection")
        total_rows = get_result_set(cnx, queries.get_total_sales)
        context = {}
        for row in total_rows:
            context[str(row[0])] = row[1]

        f = open(JSON_DIRECTORY + "total_sales.json", "w")
        f.write(json.dumps(context))
        f.close()

        neighborhood_list = get_result_set(cnx, queries.get_coord_set.format(LIMIT))

        interactive_map = folium.Map(
            location=(NASHVILLE_LATITUDE, NASHVILLE_LONGITUDE),
            zoom_start=12,
            control_scale=True,
            scroll_wheel_zoom=True
        )
        for neighborhood_row in neighborhood_list:
            neighborhood = neighborhood_row[0]
            neighborhood_name = neighborhood_row[3].replace('_', ' ')
            neighborhood_clean = re.sub('[^A-Za-z0-9 /]+', '', neighborhood_name)

            neighborhood_group = folium.FeatureGroup(name=neighborhood_clean).add_to(interactive_map)

            popup_html = get_popup_html(cnx, neighborhood)
            popup_folium = folium.Popup(html=popup_html, min_width=300, max_width=300)

            avg_latitude = neighborhood_row[1]
            avg_longitude = neighborhood_row[2]

            print(neighborhood, [avg_latitude, avg_longitude])

            tooltip_color, icon_color = get_colors_from_set(folium.map.Icon.color_options)

            neighborhood_point = folium.Marker(
                location=[avg_latitude, avg_longitude],
                tooltip=folium.map.Tooltip(text=neighborhood_clean),
                popup=popup_folium,
                icon=folium.Icon(color=tooltip_color
                                 , icon_color=icon_color
                                 , icon="glyphicon-map-marker"
                                 ),

            )
            neighborhood_group.add_child(neighborhood_point)

            lat_long_sql = queries.get_lat_long.format(neighborhood)
            house_list = get_result_set(cnx, lat_long_sql)

            for house_row in house_list:
                latitude = house_row[0]
                longitude = house_row[1]
                location = house_row[2]
                circle = folium.CircleMarker(
                    [latitude, longitude],
                    radius=4,
                    fill=True,
                    popup=location,
                    color=tooltip_color,

                )
                neighborhood_group.add_child(circle)

        folium.LayerControl().add_to(interactive_map)

        interactive_map.save(TEMPLATE_DIRECTORY + "base-map.html")
        interactive_map.save(STATIC_DIRECTORY + "base-map.html")
        interactive_map.save(STATIC_DIRECTORY_2 + "base-map.html")
    else:
        print("could not connect to mysql")


def get_colors_from_set(in_set):
    tooltip_color = "white"
    icon_color = "white"
    in_int = random.randrange(1000)
    stop_at = in_int % len(folium.map.Icon.color_options)
    for idx, x in enumerate(in_set):
        if idx == stop_at:
            tooltip_color = x
    if tooltip_color == "white":
        tooltip_color = "black"
    return tooltip_color, icon_color

if __name__ == "__main__":
    main()
