-- dbt_project_models.marts.dim_port.sql
-- Grain: one row = one unique embarkation port
-- Scope: all ports present in stg_titanic
select 
distinct embarked,
case
	when embarked = 'C' then 'Cherbourg'
	when embarked = 'Q' then 'Queenstown'
	when embarked = 'S' then 'Southampton'
else
	'unknown'
end as description_embarked
from {{ ref('stg_titanic') }} WHERE embarked is not null