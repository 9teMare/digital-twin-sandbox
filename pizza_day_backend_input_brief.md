# Pizza Day Backend Data Input Brief

## 1. Case Positioning

Campaign: `SEA pizza day campaign 0521`

Campaign ID: `5020378`

Promotion encryption ID: `563c3077a2845768a5f5f33446bf942c`

Campaign time: `2026-05-21` to `2026-06-10`

Product story:

Pizza Day is the first pilot case for UserTwin. It is not only a campaign dashboard case. It should be used to prove that UserTwin can simulate the gap between:

`successful registration -> task-active user -> qualified trader -> high-value / VIP potential user`

Backend goal:

Use Pizza Day data as structured model input, then output user segments, task path predictions, reward waste risk, and campaign optimization recommendations.

## 2. Existing Data Sources

### A. Campaign KPI Summary

Use as campaign-level aggregate metrics.

| Metric | Value |
|---|---:|
| Participants | 4,640 |
| Signup | 234 |
| KYC | 0 |
| FTD | 176 |
| FTT | 229 |
| FTTS | 139 |
| FTTF | 28 |
| FTT TradFi | 62 |
| 100FTT | 110 |
| FTT / Signup | 97.86% |
| 100FTT / FTT | 48.03% |
| Deposit Users | 2,320 |
| Net Deposit Amt | 688,527 |
| Trading Users | 3,338 |
| TV | 3,814,318,649 |
| Fee After Rebate | 157,367 |
| Current VIPs | 194 |
| New VIPs during campaign | 83 |
| Upgrade VIPs During Campaign | 10 |
| FTT Users TV | 26,924,432 |
| FTT Users Fee After Rebate | 3,136 |

Note:
The registration export shows `4,739` successful registration users, while the KPI summary shows `Participants = 4,640`. This is likely caused by export time or reporting logic differences. Use `4,739` for registration-event analysis and keep `4,640` as official KPI-summary value.

### B. Registration Events

Use as registration-level user input.

Current parsed result:

| Metric | Value |
|---|---:|
| Registration attempt rows | 5,254 |
| Successful registration rows | 4,739 |
| Failed registration rows | 515 |
| Unique successful registration users | 4,739 |
| Task-active users after registration | 1,253 |
| Successful registration -> task-active conversion | 26.44% |

Failure reason distribution:

| Failure reason | Count |
|---|---:|
| Duplicate registration | 316 |
| Operation region mismatch | 109 |
| KYC level mismatch | 67 |
| Risk control limitation | 22 |
| Business info missing | 1 |

Regional registration performance:

| Region code | Successful registration | Task-active users | Conversion |
|---|---:|---:|---:|
| sec_vi | 1,507 | 707 | 46.91% |
| sec_id | 2,605 | 421 | 16.16% |
| sec_th | 334 | 76 | 22.75% |
| sec_ph | 173 | 25 | 14.45% |
| sec_my | 120 | 24 | 20.00% |

Key insight:

Indonesia has the largest registration volume, but Vietnam has the strongest task-active conversion. UserTwin should not optimize by registration volume only. It should simulate post-registration task activation quality.

### C. Task Completion Events

Use as task behavior input.

Current parsed result:

| Metric | Value |
|---|---:|
| Task completion records | 2,037 |
| Unique task-active users | 1,253 |
| Multi-task users | 260 |

Task type distribution:

| Task type | Completion records | Unique users |
|---|---:|---:|
| CFD trading task | 860 | 860 |
| Total trading volume task | 971 | 483 |
| Net deposit task | 112 | 112 |
| Net deposit + total trading volume task | 94 | 94 |

Trading volume threshold distribution:

| Task threshold | Unique users |
|---|---:|
| Total volume >= 52,200 USDT | 483 |
| Total volume >= 100,000 USDT | 297 |
| Total volume >= 522,000 USDT | 95 |
| Total volume >= 1,000,000 USDT | 64 |
| Total volume >= 5,220,000 USDT | 17 |
| Total volume >= 10,000,000 USDT | 15 |

### D. Reward Events

Use as reward efficiency and risk-control input.

Current identifiable signals:

| Reward status / signal | Count |
|---|---:|
| Expired | 1,127 |
| Risk-control rejected | 255 |
| Waiting for risk-control result | 47 |
| Completed, waiting to push to coupon center | 2 |

Reward types observed:

- BTC cash coupon
- USDT cash coupon
- BGB cash coupon
- Lottery source
- Puzzle source

Key insight:

Reward data can support a `Reward Waste Risk` module. UserTwin should predict which users are likely to receive but not use rewards, or trigger risk-control rejection.

## 3. Backend Tables To Build

### Table 1: `campaign_summary`

One row per campaign.

Required fields:

| Field | Type | Example |
|---|---|---|
| campaign_id | string | `5020378` |
| campaign_name | string | `SEA pizza day campaign 0521` |
| promotion_encryption_id | string | `563c3077a2845768a5f5f33446bf942c` |
| start_date | date | `2026-05-21` |
| end_date | date | `2026-06-10` |
| region_scope | string | `SEA` |
| campaign_type | string | `trading_activation` |
| product_tags | array | `["CFD", "deposit", "volume_task", "reward"]` |

Recommended KPI fields:

`participants`, `signup`, `ftd`, `ftt`, `ftts`, `fttf`, `ftt_tradfi`, `hundred_ftt`, `deposit_users`, `net_deposit_amt`, `trading_users`, `tv`, `fee_after_rebate`, `current_vips`, `new_vips`, `upgrade_vips`, `ftt_users_tv`, `ftt_users_fee_after_rebate`

### Table 2: `registration_events`

One row per registration attempt.

Required fields:

| Field | Type | Notes |
|---|---|---|
| uid_hash | string | Hash raw UID before model usage |
| campaign_id | string | `5020378` |
| promotion_encryption_id | string | Join key |
| channel_code | string | Channel code at signup |
| vip_code | string | VIP code at signup |
| bd_name | string | BD or operation group |
| operation_region_code | string | `sec_vi`, `sec_id`, etc. |
| registration_method | string | manual / auto |
| registration_outcome | string | success / failed |
| join_time | datetime | Registration timestamp |
| failure_reason | string | Duplicate / KYC mismatch / region mismatch / risk control |
| accumulated_points | number | Optional |
| points_used | number | Optional |
| point_balance | number | Optional |

Optional derived fields from URL:

| Field | Description |
|---|---|
| language | `vi_VN`, `in_ID`, `en_US`, etc. |
| app_version | App version at signup |
| app_theme | dark / standard |
| domain_type | bitget.com / bitgetapp.com / other domain |

Privacy note:

Do not feed raw UID or full signup URL into the model. Use `uid_hash` and extracted URL features instead.

### Table 3: `task_completion_events`

One row per completed task.

Required fields:

| Field | Type | Notes |
|---|---|---|
| uid_hash | string | Join with registration table |
| campaign_id | string | `5020378` |
| promotion_encryption_id | string | Join key |
| component_type | string | Example: puzzle component |
| task_completion_time | datetime | Completion timestamp |
| reward_amount | number | Task reward amount |
| task_name | string | CFD / total volume / deposit |
| task_rule | string | Raw rule text |
| task_category | string | Derived: `cfd`, `volume`, `deposit`, `combo` |
| threshold_usdt | number | Extracted from task rule |

Task category rules:

| Raw task name | Derived category |
|---|---|
| CFD 交易任务 | `cfd` |
| 总交易量任务 | `volume` |
| 净充值任务 | `deposit` |
| 净充值任务，总交易量任务 | `combo` |

Threshold extraction:

Parse `交易额≥52,200 USDT` into `threshold_usdt = 52200`.

### Table 4: `reward_events`

One row per reward event.

Required fields:

| Field | Type | Notes |
|---|---|---|
| uid_hash | string | Join with user |
| campaign_id | string | `5020378` |
| reward_source | string | lottery / puzzle |
| reward_time | datetime | Reward timestamp |
| reward_amount | number | Numeric amount |
| reward_asset | string | BTC / USDT / BGB |
| reward_name | string | Cash coupon |
| reward_type | string | Coupon / voucher |
| reward_status | string | expired / risk_rejected / pending / completed |
| distribution_type | string | Auto |

Derived reward features per user:

| Feature | Meaning |
|---|---|
| reward_count | Number of rewards received |
| expired_reward_count | Expired reward count |
| risk_rejected_reward_count | Risk rejected count |
| pending_risk_reward_count | Pending risk-control count |
| reward_assets | BTC / USDT / BGB mix |
| reward_waste_risk | High if rewards expire or do not lead to task completion |

### Table 5: `user_campaign_features`

One row per user per campaign.

Build this by joining registration, task completion, and reward events.

Required fields:

| Field | Type |
|---|---|
| uid_hash | string |
| campaign_id | string |
| operation_region_code | string |
| bd_name | string |
| channel_code | string |
| registration_outcome | string |
| registration_failure_reason | string |
| is_task_active | boolean |
| completed_cfd_task | boolean |
| completed_deposit_task | boolean |
| completed_volume_task | boolean |
| completed_combo_task | boolean |
| max_volume_threshold_usdt | number |
| completed_task_count | number |
| completed_task_type_count | number |
| reward_count | number |
| expired_reward_count | number |
| risk_rejected_reward_count | number |
| derived_segment | string |

## 4. User Segmentation Rules

Use exclusive priority-based segmentation.

Priority order:

1. S1 Power / Whale Candidates
2. S2 High-Value Volume Traders
3. S3 CFD-Fit Specialists
4. S4 Deposit-Only Warm Leads
5. S5 Multi-Path Engaged Users
6. S6 Baseline Qualified Traders
7. R1 Registered Only / No Task
8. R2 Registration Failed

### Segment definitions

| Segment | Count | Rule | Action |
|---|---:|---|---|
| S1 Power / Whale Candidates | 64 | `max_volume_threshold_usdt >= 1,000,000` | Push VIP, leaderboard, high-value exclusive benefits |
| S2 High-Value Volume Traders | 233 | `100,000 <= max_volume_threshold_usdt < 1,000,000` | Push tiered volume rewards |
| S3 CFD-Fit Specialists | 647 | Completed CFD task, but no clear volume/deposit upgrade | Push CFD path with risk education |
| S4 Deposit-Only Warm Leads | 72 | Completed deposit task but weak trading behavior | Push first-trade guidance |
| S5 Multi-Path Engaged Users | 122 | Completed multiple task types but not high-volume | Push personalized task bundle |
| S6 Baseline Qualified Traders | 115 | `max_volume_threshold_usdt = 52,200` | Push 100FTT / next-level volume task |
| R1 Registered Only / No Task | 3,486 | Successful registration but no task completion | Diagnose activation drop-off |
| R2 Registration Failed | 515 | Failed registration | Diagnose registration friction |

Note:
`R1 = 4,739 successful registrations - 1,253 task-active users = 3,486`.

Registration failure subsegments:

| Subsegment | Count | Rule |
|---|---:|---|
| Duplicate Signup Users | 316 | failure_reason = duplicate registration |
| Region-Mismatch Users | 109 | failure_reason = operation region mismatch |
| KYC-Mismatch Users | 67 | failure_reason = KYC level mismatch |
| Risk-Control Limited Users | 22 | failure_reason = risk control limitation |

## 5. Frontend / Model Output Format

Backend should return these blocks to frontend.

### A. Campaign Overview

```json
{
  "campaign_id": "5020378",
  "campaign_name": "SEA pizza day campaign 0521",
  "region_scope": "SEA",
  "start_date": "2026-05-21",
  "end_date": "2026-06-10",
  "core_metrics": {
    "successful_registrations": 4739,
    "task_active_users": 1253,
    "registration_to_task_active_rate": 0.2644,
    "ftt": 229,
    "hundred_ftt": 110,
    "hundred_ftt_over_ftt": 0.4803,
    "tv": 3814318649,
    "fee_after_rebate": 157367,
    "new_vips": 83,
    "upgrade_vips": 10
  }
}
```

### B. Regional Performance

```json
[
  {
    "region_code": "sec_vi",
    "successful_registrations": 1507,
    "task_active_users": 707,
    "task_active_rate": 0.4691
  },
  {
    "region_code": "sec_id",
    "successful_registrations": 2605,
    "task_active_users": 421,
    "task_active_rate": 0.1616
  }
]
```

### C. User Segment Summary

```json
[
  {
    "segment_id": "S1",
    "segment_name": "Power / Whale Candidates",
    "user_count": 64,
    "rule": "max_volume_threshold_usdt >= 1000000",
    "recommended_action": "Push VIP benefits, leaderboard, and high-value trading missions."
  },
  {
    "segment_id": "S3",
    "segment_name": "CFD-Fit Specialists",
    "user_count": 647,
    "rule": "completed_cfd_task = true and no high-volume upgrade",
    "recommended_action": "Route into CFD tasks with risk education and suitability checks."
  }
]
```

### D. Registration Friction

```json
[
  {
    "friction_type": "duplicate_registration",
    "count": 316,
    "recommendation": "Detect duplicate signup and reduce reward abuse before launch."
  },
  {
    "friction_type": "kyc_mismatch",
    "count": 67,
    "recommendation": "Show KYC requirement before registration."
  }
]
```

### E. Reward Efficiency

```json
{
  "expired_rewards": 1127,
  "risk_rejected_rewards": 255,
  "pending_risk_control_rewards": 47,
  "completed_pending_coupon_push": 2,
  "recommendation": "Predict reward waste and risk-control friction before campaign launch."
}
```

## 6. Model Input Prompt Context

The backend can pass the model a compact campaign context like this:

```text
Campaign: SEA Pizza Day 0521
Goal: increase qualified trading activation, trading volume, and VIP potential.
Key metric: Qualified Activation = 100FTT / FTT = 48.03%.
Registration: 4,739 successful users, 1,253 task-active users, 26.44% registration-to-task-active rate.
Region insight: Vietnam has 46.91% task-active rate, Indonesia has 16.16%.
Task paths: CFD task, deposit task, volume task, combo task.
Risk/reward signals: 1,127 expired rewards, 255 risk-control rejected rewards.
Output required: user segments, likely task path, reward waste risk, region optimization, campaign routing recommendation.
```

## 7. UserTwin Storytelling To Keep In Mind

Do not position this as a normal campaign dashboard.

Position it as:

`Trading platform user simulation infrastructure.`

Core message:

Pizza Day attracted many users, but only part of them became task-active and even fewer became qualified/high-value traders. UserTwin helps the platform simulate this before launch: which region converts, which users get stuck, which users fit CFD or volume tasks, and which rewards are likely to be wasted.

