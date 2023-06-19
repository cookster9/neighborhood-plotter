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
    import creds
    LIMIT = sys.maxsize
elif platform == "darwin":
    import local_creds as creds
    LIMIT = 1000
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

import js

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
        html = """<!DOCTYPE html>
            <html>
                <head>
                """
        leaflet_css = """<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
     integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
     crossorigin=""/>
     """
        leaflet_js = """<!-- Make sure you put this AFTER Leaflet's CSS -->
 <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
     integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
     crossorigin="">
     </script>
     """
        html = html + leaflet_css + leaflet_js
        css = """
        <style>#map { height: 500px; }</style>
        """
        html = html + css

        html = html + """</head>
        """



        html = html + """<div id="map"></div>
        """
        script_html = """
        <script>
            var map = L.map('map').setView([{0}, {1}], 12);
        """.format(NASHVILLE_LATITUDE, NASHVILLE_LONGITUDE)
        script_html = script_html + """L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);
"""
        script_html = script_html + js.all_icons


        print("got connection")
        # total_rows = get_result_set(cnx, queries.get_total_sales)
        # context = {}
        # for row in total_rows:
        #     context[str(row[0])] = row[1]
        #
        # f = open(JSON_DIRECTORY + "total_sales.json", "w")
        # f.write(json.dumps(context))
        # f.close()

        neighborhood_list = get_result_set(cnx, queries.get_coord_set)
        print("got neighborhood list")

        group_dict = {}
        for neighborhood_row in neighborhood_list:
            neighborhood = neighborhood_row[0]
            neighborhood_name = neighborhood_row[3].replace('_', ' ')
            neighborhood_clean = re.sub('[^A-Za-z0-9 /]+', '', neighborhood_name)

            avg_latitude = neighborhood_row[1]
            avg_longitude = neighborhood_row[2]

            if str(neighborhood) in group_dict:
                blank = group_dict[str(neighborhood)]
            else:
                print(neighborhood, [avg_latitude, avg_longitude])
                mod_neighborhood = int(neighborhood) % 7
                neighborhood_marker_js = """
                            var marker{0} = L.marker([{1}, {2}], {{icon: icon{3}}}).addTo(map);
                            var array{0} = new Array();
                                                    """.format(neighborhood, avg_latitude, avg_longitude,
                                                               mod_neighborhood)
                hover_js = """
                marker{0}.on('mouseover', function()
                {{
                    marker{0}.setIcon(icon{1});
                    array{0}.map(a => a.setStyle({{fillColor: 'yellow', radius: 40}}));
                }});
                marker{0}.on('mouseout', function()
                {{
                    marker{0}.setIcon(icon{2});
                    array{0}.map(a => a.setStyle({{fillColor: 'blue', radius: 30}}));
                }});
                """.format(neighborhood, "Hover", mod_neighborhood)

                popup_html = "\"<p>{0}</p>\"".format(neighborhood_clean)
                popup_js = """
                    marker{0}.bindPopup({1});
                """.format(neighborhood, popup_html)
                tooltip_js = """
                marker{0}.bindTooltip(\"{1}\");""".format(neighborhood, neighborhood_clean)
                script_html = script_html + neighborhood_marker_js + hover_js + popup_js + tooltip_js
                group_dict[str(neighborhood)] = ""

            latitude = neighborhood_row[4]
            longitude = neighborhood_row[5]
            location = neighborhood_row[6]
            padctn_id = neighborhood_row[7]
            sale_date = neighborhood_row[8]
            sale_price = neighborhood_row[9]
            reis_id = neighborhood_row[10]

            house_marker_js = """var circle{0} = L.circle([{1}, {2}], {{
                color: 'blue',
                fillOpacity: 0.5,
                radius: 30, weight: 2
            }}).addTo(map);
            array{3}.push(circle{0});
            """.format(reis_id, latitude, longitude, neighborhood)

            house_popup_js = """circle{0}.bindPopup(\"{1}<br>{2}<br>{3}\");
            """.format(reis_id, str(location), str(sale_date), str(sale_price))

            script_html = script_html + house_marker_js + house_popup_js

        script_html = script_html + """</script>"""
        html = html + script_html
        html = html + """</html>"""

        # interactive_map.save(TEMPLATE_DIRECTORY + "base-map.html")
        # interactive_map.save(STATIC_DIRECTORY + "base-map.html")
        # interactive_map.save(STATIC_DIRECTORY_2 + "base-map.html")
        saveHtmlFile(html, TEMPLATE_DIRECTORY + "base-map.html")
        saveHtmlFile(html, STATIC_DIRECTORY + "base-map.html")
        saveHtmlFile(html, STATIC_DIRECTORY_2 + "base-map.html")
    else:
        print("could not connect to mysql")

def saveHtmlFile(text, path):
    with open(path, "w") as file:
        file.write(text)

if __name__ == "__main__":
    main()
