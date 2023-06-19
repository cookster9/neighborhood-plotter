get_total_sales = """select DATE_FORMAT(STR_TO_DATE(CONCAT(yearweek(now()),' Sunday'), '%X%V %W'),'%m/%d') as 'Week_of', count(*)
    from real_estate_info_scrape where year_week = yearweek(now()) and property_use = 'SINGLE FAMILY'
    union
    select DATE_FORMAT(STR_TO_DATE(CONCAT(yearweek(now())-1,' Sunday'), '%X%V %W'),'%m/%d') as 'Week_of', count(*)
    from real_estate_info_scrape where year_week = (yearweek(now()))-1 and property_use = 'SINGLE FAMILY'
    union
    select DATE_FORMAT(STR_TO_DATE(CONCAT(yearweek(now())-2,' Sunday'), '%X%V %W'),'%m/%d') as 'Week_of', count(*)
    from real_estate_info_scrape where year_week = (yearweek(now()))-2 and property_use = 'SINGLE FAMILY'
    union
    select DATE_FORMAT(STR_TO_DATE(CONCAT(yearweek(now())-3,' Sunday'), '%X%V %W'),'%m/%d') as 'Week_of', count(*)
    from real_estate_info_scrape where year_week = (yearweek(now()))-3 and property_use = 'SINGLE FAMILY'
    union
    select DATE_FORMAT(STR_TO_DATE(CONCAT(yearweek(now())-4,' Sunday'), '%X%V %W'),'%m/%d') as 'Week_of', count(*)
    from real_estate_info_scrape where year_week = (yearweek(now()))-4 and property_use = 'SINGLE FAMILY'
    order by 1 asc
    ;"""

get_sales_rows = """select STR_TO_DATE(CONCAT(yearweek(now()),' Sunday'), '%X%V %W') as 'Week of', (select count(*)
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
    and year_week = (yearweek(now()))-4) sale_count """

get_coord_set = """
select reis.neighborhood, n.latitude, n.longitude, n.description
, tda.latitude, tda.longitude, reis.location, reis.padctn_id
, reis.sale_date, reis.sale_price, reis.id
from real_estate_info_scrape reis
inner join neighborhoods n on reis.neighborhood = n.id
inner join tn_davidson_addresses tda on reis.padctn_id = tda.padctn_id
where sale_date > DATE_ADD(now(), INTERVAL -6 WEEK)
and property_use = 'SINGLE FAMILY';
"""

get_lat_long = """select latitude, longitude, location, reis.padctn_id
from real_estate_info_scrape reis
inner join tn_davidson_addresses tda on reis.padctn_id = tda.padctn_id
where reis.neighborhood = {0}
order by sale_date desc
limit 5;
"""

get_neighborhoods = """select distinct n.id, n.description
from neighborhoods n
inner join real_estate_info_scrape reis on n.id = reis.neighborhood
where property_use in ('Single Family')
          and year_week > (yearweek(now()))-5
          limit {0};
          """