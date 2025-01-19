SELECT q.faculty,
	   avg(total_transactions) as month_avg_total_transactions,
       avg(total_price) as month_avg_total_price

FROM

	(
	SELECT u.faculty,
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

	GROUP BY u.faculty,
			 month(t.purchase_time)
	) q

GROUP BY q.faculty
