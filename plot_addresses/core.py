import random
import re

import folium
import creds
from helpers import get_connection
import json
import queries

TEMPLATE_DIRECTORY = '../analytics_project/dashboard/templates/dashboard/'
STATIC_DIRECTORY = '../analytics_project/dashboard/static/dashboard/html/'
JSON_DIRECTORY = '../analytics_project/dashboard/static/dashboard/json/'

NASHVILLE_LATITUDE = 36.164577
NASHVILLE_LONGITUDE = -86.776949

def get_coord_set(connection):
    sql = queries.get_coord_set
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    print(cursor.rowcount)
    cursor.close()
    return rows


def get_sale_rows(connection, neighborhood):
    sql = queries.get_sales_rows.format(neighborhood)
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    # print(cursor.rowcount)
    cursor.close()
    return rows


def get_total_sales(connection):
    sql = queries.get_total_sales
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    # print(cursor.rowcount)
    cursor.close()
    return rows


def get_popup_html(connection, neighborhood):
    rows = get_sale_rows(connection, neighborhood)
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


def get_neighborhood_description(connection, neighborhood):
    sql = 'select description from neighborhoods where id = {0}'.format(neighborhood)
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    # print(cursor.rowcount)
    cursor.close()
    neighborhood = rows[0][0].replace('_', ' ')
    neighborhood_clean = re.sub('[^A-Za-z0-9 /]+', '', neighborhood)
    return neighborhood_clean


def main():
    cnx = get_connection(creds.aws_user, creds.aws_pass,
                         creds.aws_host,
                         creds.aws_database)
    if cnx:
        print("got connection")
        total_rows = get_total_sales(cnx)
        context = {}
        for row in total_rows:
            context[str(row[0])] = row[1]

        f = open(JSON_DIRECTORY + "total_sales.json", "w")
        f.write(json.dumps(context))
        f.close()

        coord_list = get_coord_set(cnx)
        # subplot = plt.subplot()

        interactive_map = folium.Map(
            location=(NASHVILLE_LATITUDE, NASHVILLE_LONGITUDE),
            zoom_start=12,
            control_scale=True
        )
        folium.TileLayer('Stamen Terrain').add_to(interactive_map)
        folium.TileLayer('Stamen Toner').add_to(interactive_map)
        folium.TileLayer('Stamen Water Color').add_to(interactive_map)
        folium.TileLayer('cartodbpositron').add_to(interactive_map)
        folium.TileLayer('cartodbdark_matter').add_to(interactive_map)
        folium.LayerControl().add_to(interactive_map)

        for row in coord_list:
            # x, y = zip(*xy_coord)
            # print(neighborhood)
            # print(color_list_glob[int(neighborhood) % len(color_list_glob)])
            # plt.scatter(x, y, s=.01, c=color_list_glob[int(neighborhood) % len(color_list_glob)])

            neighborhood = row[0]
            avg_latitude = row[1]
            avg_longitude = row[2]

            popup_html = get_popup_html(cnx, neighborhood)
            popup_folium = folium.Popup(html=popup_html, min_width=300, max_width=300)
            # print(popup_html)
            # quit()
            print(neighborhood, [avg_latitude, avg_longitude])
            neighborhood_clean = get_neighborhood_description(cnx, neighborhood)

            tooltip_color, icon_color = get_colors_from_set(folium.map.Icon.color_options)
            address_point = folium.Marker(
                location=[avg_latitude, avg_longitude],
                tooltip=folium.map.Tooltip(text=neighborhood_clean),
                popup=popup_folium,
                icon=folium.Icon(color=tooltip_color
                                 , icon_color=icon_color
                                 , icon="glyphicon-map-marker"
                                 ),

            )
            address_point.add_to(interactive_map)
        # plt.axis('off')
        # plt.show()

        # addresses_layer = folium.features.GeoJson(
        #     addresses,
        #     name="Public transport stops"
        # )

        interactive_map.save(TEMPLATE_DIRECTORY + "base-map.html")
        interactive_map.save(STATIC_DIRECTORY + "base-map.html")

        # plt.savefig('../pythonProject/analytics_project/dashboard/static/dashboard/images/foo.png')
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
        icon_color = "black"
    return tooltip_color, icon_color


main()