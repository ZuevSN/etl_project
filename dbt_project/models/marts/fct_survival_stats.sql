-- dbt_project_models.marts.fct_survival_stats.sql
-- Grain: one row = one unique combination of (pclass, embarked)
-- Scope: all passengers, aggregated by class and port
with agg as (
    select
        pclass,
        embarked,
        COUNT(passenger_id) total_passengers, sum(survived) survived_count, AVG(fare) avg_fare
    from {{ ref('stg_titanic') }}
    group by pclass, embarked
)
select
    *,
    survived_count::numeric / nullif(total_passengers, 0) as survival_rate
from agg