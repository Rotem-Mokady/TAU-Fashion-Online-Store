SELECT t.id,
	   t.user_mail,
       t.purchase_time,
       group_concat(tti.cloth_id, '') as all_products_in_transaction

FROM taufashion_10.transactions t

JOIN taufashion_10.transaction_to_items tti
ON t.id = tti.transaction_id

GROUP BY t.id,
	     t.user_mail,
         t.purchase_time