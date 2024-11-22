with raw_data as
(
	select u.*, t.id as order_id, t.amount, t.purchase_time, c.*

	from taufashion_10.users u

	join taufashion_10.transactions t
	on u.email = t.user_mail

	join taufashion_10.cloths c
	on t.cloth_id = c.id
) ,

most_popular_color as (

	select distinct
	   q.gender,
	   first_value(q.color) over (order by q.counter desc) as most_popular_color

	from
		(
		select
			r.gender,
			substring_index(r.name, ' ', 1) as color,
			sum(r.amount) as counter

		from raw_data r

		group by r.gender,
			   substring_index(r.name, ' ', 1)
		) q
)

select r.purchase_time
from raw_data





