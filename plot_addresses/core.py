import random
import re

import folium
import pandas as pd
import creds
from helpers import get_connection

TEMPLATE_DIRECTORY = '../analytics_project/dashboard/templates/dashboard'
STATIC_DIRECTORY = '../analytics_project/dashboard/static/dashboard/html'

NASHVILLE_LATITUDE = 36.164577
NASHVILLE_LONGITUDE = -86.776949

color_list_glob = ['r', 'g', 'b', 'y', 'c', 'm', 'k']
df = pd.main()


def get_coord_set(connection):
    sql = """select tda.longitude, tda.latitude, reis.neighborhood
          from tn_davidson_addresses tda  
          join (  
          select padctn_id, neighborhood,  
          ROW_NUMBER() OVER (partition by padctn_id order by sale_date desc)  
          rn from real_estate_info_scrape reis_in
          join neighborhoods n on reis_in.neighborhood = n.id
          where
          coalesce(trim(neighborhood),'') <> ''  
          and property_use in ('Single Family')
          ) reis on tda.padctn_id = reis.padctn_id 
          where reis.rn = 1 
          ;"""
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    print(cursor.rowcount)
    cursor.close()
    return rows


def get_sale_rows(connection, neighborhood):
    sql = """select STR_TO_DATE(CONCAT(yearweek(now()),' Sunday'), '%X%V %W') as 'Week of', (select count(*)
    from real_estate_info_scrape where neighborhood = {0}
    and year_week = yearweek(now())) sale_count
    union
    select STR_TO_DATE(CONCAT(yearweek(now())-1,' Sunday'), '%X%V %W') as 'Week of', (select count(*)
    from real_estate_info_scrape where neighborhood = {0}
    and year_week = (yearweek(now()))-1) sale_count
    union
    select STR_TO_DATE(CONCAT(yearweek(now())-2,' Sunday'), '%X%V %W') as 'Week of', (select count(*)
    from real_estate_info_scrape where neighborhood = {0}
    and year_week = (yearweek(now()))-2) sale_count
    union
    select STR_TO_DATE(CONCAT(yearweek(now())-3,' Sunday'), '%X%V %W') as 'Week of', (select count(*)
    from real_estate_info_scrape where neighborhood = {0}
    and year_week = (yearweek(now()))-3) sale_count
    union
    select STR_TO_DATE(CONCAT(yearweek(now())-4,' Sunday'), '%X%V %W') as 'Week of', (select count(*)
    from real_estate_info_scrape where neighborhood = {0}
    and year_week = (yearweek(now()))-4) sale_count """.format(neighborhood)
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


def get_avg_lat_long(xy_coord):
    sum_x = 0.0
    sum_y = 0.0
    for y, x in xy_coord:
        sum_x = sum_x + float(x)
        sum_y = sum_y + float(y)
    avg_x = sum_x / len(xy_coord)
    avg_y = sum_y / len(xy_coord)
    return avg_y, avg_x


def main():
    cnx = get_connection(creds.aws_user, creds.aws_pass,
                         creds.aws_host,
                         creds.aws_database)
    if cnx:
        print("got connection")
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

        coord_dict = {}
        for coord in coord_list:
            # var_longitude.append(coord[0])
            # var_latitude.append(coord[1])
            xy_list = [coord[1], coord[0]]
            if coord[2] in coord_dict:
                coord_dict[coord[2]].append(xy_list)
            else:
                coord_dict[coord[2]] = [xy_list]
            # plt.scatter(coord[0],coord[1],s=1)
        # plt.scatter(var_longitude, var_latitude, s=0.05)
        for neighborhood, xy_coord in coord_dict.items():
            # x, y = zip(*xy_coord)
            # print(neighborhood)
            # print(color_list_glob[int(neighborhood) % len(color_list_glob)])
            # plt.scatter(x, y, s=.01, c=color_list_glob[int(neighborhood) % len(color_list_glob)])


            avg_latitude, avg_longitude = get_avg_lat_long(xy_coord)

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

        interactive_map.save(TEMPLATE_DIRECTORY + '/' + "base-map.html")
        interactive_map.save(STATIC_DIRECTORY + '/' + "base-map.html")

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
