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
    order by 1 asc;"""

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
select reis.neighborhood, avg(tda.latitude), avg(tda.longitude), reis.description
          from tn_davidson_addresses tda  
          join (  
          select padctn_id, neighborhood, n.description,
          ROW_NUMBER() OVER (partition by padctn_id order by sale_date desc)  
          rn from real_estate_info_scrape reis_in
          join neighborhoods n on reis_in.neighborhood = n.id
          where
          coalesce(trim(neighborhood),'') <> ''  
          and property_use in ('Single Family')
          and year_week > (yearweek(now()))-5
          ) reis on tda.padctn_id = reis.padctn_id 
          where reis.rn = 1
group by reis.neighborhood, reis.description;
          """