
/*
  Transforms client-user telemetry to a UFR representation.
      HASHBYTES('SHA2_512', CAST("user name" AS varbinary(8000)) as client_user_id,
*/

{{ config(materialized='table') }}

with revenue_feature_data as (

    select

      "theprogram" as client_id,
      "org" as client_name,
      "user name" as client_user_name,
      SHA1(CAST("user name" AS varbinary(8000))) as client_user_id,
      "amount" as client_revenue,
      "transaction date" as client_revenue_timestamp,
      "isoop" as client_feature_value_oop,
      "transaction date" as client_feature_usage_timestamp_oop,
      'submission' as client_feature_value_submission,
      "submission date" as client_feature_usage_timestamp_submission,
      'approval' as client_feature_value_approval,
      "approval date" as client_feature_usage_timestamp_approval
      
    from centerhq.public."client-user-spend-data-max"

)

select *
from revenue_feature_data

/*
    Uncomment the line below to remove records with null `id` values
*/

-- where id is not null
