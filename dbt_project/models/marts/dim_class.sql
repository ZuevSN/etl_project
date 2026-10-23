-- dbt_project_models.marts.dim_class.sql
-- Grain: one row = one unique passenger class
-- Scope: all classes present in stg_titanic
SELECT DISTINCT pclass,
case
	when pclass = 1 then '1st Class'
	when pclass = 2 then '2nd Class'
	when pclass = 3 then '3rd Class'
else
	'unknown'
end description_class
FROM {{ ref('stg_titanic') }} WHERE pclass is not null