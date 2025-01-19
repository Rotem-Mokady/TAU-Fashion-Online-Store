SELECT s.id,
	   s.name,
       s.orders,
       CASE WHEN s.asc_ranking <= 3 THEN '3 Top Unpopular' ELSE '3 Top popular' END as description

FROM 
	(
		SELECT q.*,
			   rank () over (order by q.orders asc) as asc_ranking,
			   rank () over (order by q.orders desc) as desc_ranking

		FROM 
		(
		SELECT c.id,
			   c.name,
			   count(DISTINCT tti.transaction_id) as orders

		FROM taufashion_10.cloths c 

		LEFT JOIN taufashion_10.transaction_to_items tti
		ON c.id = tti.cloth_id 

		GROUP BY c.id,
				 c.name
		) q      
	)  s

WHERE s.asc_ranking <= 3 OR s.desc_ranking <= 3
       