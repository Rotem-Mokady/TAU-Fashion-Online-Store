SELECT CASE WHEN q.campaign = 1 THEN 'With Campain' ELSE 'With No Campain' END as campain_flag,
	   avg(total_orders) as avg_total_orders

FROM
	(
	SELECT c.campaign,
		   c.id,
		   coalesce(sum(tti.amount), 0) as total_orders

	FROM taufashion_10.cloths c

	LEFT JOIN taufashion_10.transaction_to_items tti
	ON c.id = tti.cloth_id

	GROUP BY c.campaign,
			 c.id
	) q

GROUP BY q.campaign