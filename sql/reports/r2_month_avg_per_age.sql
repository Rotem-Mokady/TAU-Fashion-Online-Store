SELECT q.age_category,
	   avg(total_transactions) as month_avg_total_transactions,
       avg(total_price) as month_avg_total_price

FROM

	(
	SELECT CASE WHEN TIMESTAMPDIFF(year,  u.birth_date, current_time()) < 30 THEN 'UNDER 30'
				WHEN TIMESTAMPDIFF(year,  u.birth_date, current_time()) < 40 THEN 'UNDER 40'
				ELSE '40 AND MORE' END as age_category,
		  month(t.purchase_time) as month_idx,
		  count(DISTINCT t.id) as total_transactions,
		  sum(c.price) as total_price

	FROM taufashion_10.users u

	JOIN taufashion_10.transactions t
	ON u.email = t.user_mail

	JOIN taufashion_10.transaction_to_items tti
	ON tti.transaction_id = t.id

	JOIN taufashion_10.cloths c
	ON tti.cloth_id = c.id

	GROUP BY CASE WHEN TIMESTAMPDIFF(year,  u.birth_date, current_time()) < 30 THEN 'UNDER 30'
				WHEN TIMESTAMPDIFF(year,  u.birth_date, current_time()) < 40 THEN 'UNDER 40'
				ELSE '40 AND MORE' END,
			 month(t.purchase_time)
	) q

GROUP BY q.age_category
