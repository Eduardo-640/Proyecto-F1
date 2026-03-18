# Database Schema

> Auto-documented from Django models — `apps/` namespace.

---

## Table of Contents

- [seasons — Season](#season)
- [teams — Team](#team)
- [teams — Sponsor](#sponsor)
- [teams — SponsorCondition](#sponsorcondition)
- [drivers — Driver](#driver)
- [drivers — DriverStanding](#driverstanding)
- [races — Circuit](#circuit)
- [races — Race](#race)
- [races — RaceResult](#raceresult)
- [races — CreditTransaction](#credittransaction)
- [developments — TeamDevelopment](#teamdevelopment)
- [developments — PurchasedUpgrade](#purchasedupgrade)
- [Relationships diagram](#relationships-diagram)

---

## Season

**App:** `seasons` | **Table:** `seasons_season`

| Column       | Type                | Constraints               | Notes                                                    |
| ------------ | ------------------- | ------------------------- | -------------------------------------------------------- |
| `id`         | integer             | PK, auto                  | —                                                        |
| `name`       | varchar(100)        | NOT NULL                  | Display name of the season                               |
| `year`       | smallint (unsigned) | NOT NULL                  | Calendar year                                            |
| `edition`    | smallint (unsigned) | NOT NULL                  | Edition number within the year                           |
| `active`     | boolean             | NOT NULL, default `false` | Only one season active at a time (enforced in app logic) |
| `start_date` | date                | NOT NULL                  | —                                                        |
| `end_date`   | date                | NOT NULL                  | —                                                        |
| `created_at` | datetime            | NOT NULL, auto            | —                                                        |

**Ordering:** `year`, `edition`

---

## Team

**App:** `teams` | **Table:** `teams_team`

| Column       | Type               | Constraints              | Notes           |
| ------------ | ------------------ | ------------------------ | --------------- |
| `id`         | integer            | PK, auto                 | —               |
| `name`       | varchar(100)       | NOT NULL, UNIQUE         | —               |
| `credits`    | integer (unsigned) | NOT NULL, default `500`  | Budget currency |
| `active`     | boolean            | NOT NULL, default `true` | —               |
| `created_at` | datetime           | NOT NULL, auto           | —               |

**Ordering:** `-credits` (richest first)

---

## Sponsor

**App:** `teams` | **Table:** `teams_sponsor`

| Column        | Type               | Constraints               | Notes                                                 |
| ------------- | ------------------ | ------------------------- | ----------------------------------------------------- |
| `id`          | integer            | PK, auto                  | —                                                     |
| `team_id`     | FK → `Team`        | NULL, SET NULL            | A sponsor belongs to at most one team                 |
| `name`        | varchar(100)       | NOT NULL, UNIQUE          | —                                                     |
| `description` | text               | blank                     | —                                                     |
| `is_main`     | boolean            | NOT NULL, default `false` | At most **one** main sponsor per team (DB constraint) |
| `base_bonus`  | integer (unsigned) | NOT NULL, default `0`     | Credits provided to the team per season               |
| `active`      | boolean            | NOT NULL, default `true`  | —                                                     |

**Constraints:**

- `unique_main_sponsor_per_team` — partial unique on `(team)` where `is_main = true`

---

## SponsorCondition

**App:** `teams` | **Table:** `teams_sponsorcondition`

Represents an affinity (reward) or penalty that a sponsor applies based on a team's performance category.

| Column        | Type           | Constraints           | Notes                                        |
| ------------- | -------------- | --------------------- | -------------------------------------------- |
| `id`          | integer        | PK, auto              | —                                            |
| `sponsor_id`  | FK → `Sponsor` | NOT NULL, CASCADE     | —                                            |
| `type`        | varchar(20)    | NOT NULL              | `affinity` / `penalty`                       |
| `category`    | varchar(20)    | NOT NULL              | See **Affinity choices** below               |
| `value`       | integer        | NOT NULL, default `0` | Positive = bonus credits, negative = penalty |
| `description` | varchar(200)   | blank                 | Human-readable note                          |

**`type` choices** (`SponsorConditionType`):

| Value      | Label                              |
| ---------- | ---------------------------------- |
| `affinity` | Affinity — rewards this behaviour  |
| `penalty`  | Penalty — penalises this behaviour |

**`category` choices** (`Affinity`):

| Value         | Label       |
| ------------- | ----------- |
| `podiums`     | Podiums     |
| `wins`        | Wins        |
| `development` | Development |
| `money`       | Money       |
| `points`      | Points      |
| `speed`       | Speed       |
| `consistency` | Consistency |

---

## Driver

**App:** `drivers` | **Table:** `drivers_driver`

| Column       | Type              | Constraints              | Notes                     |
| ------------ | ----------------- | ------------------------ | ------------------------- |
| `id`         | integer           | PK, auto                 | —                         |
| `name`       | varchar(100)      | NOT NULL                 | —                         |
| `team_id`    | OneToOne → `Team` | NULL, SET NULL           | One driver per team slot  |
| `steam_id`   | varchar(64)       | UNIQUE, nullable         | Steam platform identifier |
| `active`     | boolean           | NOT NULL, default `true` | —                         |
| `created_at` | datetime          | NOT NULL, auto           | —                         |

**Ordering:** `name`

---

## DriverStanding

**App:** `drivers` | **Table:** `drivers_driverstanding`

Accumulated season standings per driver. One row per `(driver, season)`.

| Column           | Type                | Constraints           | Notes          |
| ---------------- | ------------------- | --------------------- | -------------- |
| `id`             | integer             | PK, auto              | —              |
| `driver_id`      | FK → `Driver`       | NOT NULL, CASCADE     | —              |
| `season_id`      | FK → `Season`       | NOT NULL, CASCADE     | —              |
| `total_points`   | integer (unsigned)  | NOT NULL, default `0` | —              |
| `races_entered`  | smallint (unsigned) | NOT NULL, default `0` | —              |
| `wins`           | smallint (unsigned) | NOT NULL, default `0` | —              |
| `podiums`        | smallint (unsigned) | NOT NULL, default `0` | Top-3 finishes |
| `pole_positions` | smallint (unsigned) | NOT NULL, default `0` | —              |
| `fastest_laps`   | smallint (unsigned) | NOT NULL, default `0` | —              |
| `dnf_count`      | smallint (unsigned) | NOT NULL, default `0` | Did Not Finish |

**Constraints:** UNIQUE `(driver, season)`
**Ordering:** `season`, `-total_points`

---

## Circuit

**App:** `races` | **Table:** `races_circuit`

| Column      | Type                | Constraints      | Notes                        |
| ----------- | ------------------- | ---------------- | ---------------------------- |
| `id`        | integer             | PK, auto         | —                            |
| `name`      | varchar(100)        | NOT NULL, UNIQUE | —                            |
| `location`  | varchar(100)        | blank            | City / country               |
| `laps`      | smallint (unsigned) | NOT NULL         | Number of laps in a race     |
| `length_km` | decimal(5,2)        | NOT NULL         | Circuit length in kilometres |

**Ordering:** `name`

---

## Race

**App:** `races` | **Table:** `races_race`

| Column         | Type                | Constraints                  | Notes                   |
| -------------- | ------------------- | ---------------------------- | ----------------------- |
| `id`           | integer             | PK, auto                     | —                       |
| `season_id`    | FK → `Season`       | NOT NULL, CASCADE            | —                       |
| `round_number` | smallint (unsigned) | NOT NULL                     | Round within the season |
| `circuit_id`   | FK → `Circuit`      | NOT NULL, CASCADE            | —                       |
| `race_date`    | date                | nullable                     | —                       |
| `status`       | varchar(20)         | NOT NULL, default `practice` | See choices below       |

**`status` choices** (`RaceStatus`):

| Value        | Label      |
| ------------ | ---------- |
| `practice`   | Practice   |
| `qualifying` | Qualifying |
| `race`       | Race       |
| `finished`   | Finished   |

**Constraints:** UNIQUE `(season, round_number)`
**Ordering:** `season`, `round_number`

---

## RaceResult

**App:** `races` | **Table:** `races_raceresult`

One result row per driver per race.

| Column           | Type                | Constraints               | Notes              |
| ---------------- | ------------------- | ------------------------- | ------------------ |
| `id`             | integer             | PK, auto                  | —                  |
| `race_id`        | FK → `Race`         | NOT NULL, CASCADE         | —                  |
| `driver_id`      | FK → `Driver`       | NOT NULL, CASCADE         | —                  |
| `team_id`        | FK → `Team`         | NOT NULL, CASCADE         | Team at race time  |
| `position`       | smallint (unsigned) | NOT NULL                  | Finishing position |
| `pole_position`  | boolean             | NOT NULL, default `false` | —                  |
| `fastest_lap`    | boolean             | NOT NULL, default `false` | —                  |
| `finished_race`  | boolean             | NOT NULL, default `true`  | `false` = DNF/DSQ  |
| `points_awarded` | integer (unsigned)  | NOT NULL, default `0`     | —                  |

**Constraints:** UNIQUE `(race, driver)`
**Ordering:** `race`, `position`

---

## CreditTransaction

**App:** `races` | **Table:** `races_credittransaction`

Audit log of all credit movements for a team.

| Column             | Type         | Constraints       | Notes                                 |
| ------------------ | ------------ | ----------------- | ------------------------------------- |
| `id`               | integer      | PK, auto          | —                                     |
| `team_id`          | FK → `Team`  | NOT NULL, CASCADE | —                                     |
| `amount`           | integer      | NOT NULL          | Positive = income, negative = expense |
| `transaction_type` | varchar(20)  | NOT NULL          | See choices below                     |
| `description`      | varchar(255) | blank             | —                                     |
| `race_id`          | FK → `Race`  | NULL, SET NULL    | Optional link to triggering race      |
| `created_at`       | datetime     | NOT NULL, auto    | —                                     |

**`transaction_type` choices** (`TransactionType`):

| Value              | Label                     |
| ------------------ | ------------------------- |
| `race_result`      | Race Result               |
| `balance_bonus`    | Competitive Balance Bonus |
| `upgrade_purchase` | Upgrade Purchase          |
| `admin_adjustment` | Administrative Adjustment |

**Ordering:** `-created_at`

---

## TeamDevelopment

**App:** `developments` | **Table:** `developments_teamdevelopment`

Snapshot of a team's technical level per season. All department levels range **1–5**.

| Column         | Type                | Constraints                | Notes |
| -------------- | ------------------- | -------------------------- | ----- |
| `id`           | integer             | PK, auto                   | —     |
| `team_id`      | FK → `Team`         | NOT NULL, CASCADE          | —     |
| `season_id`    | FK → `Season`       | NOT NULL, CASCADE          | —     |
| `engine`       | smallint (unsigned) | NOT NULL, default `1`, 1–5 | —     |
| `aerodynamics` | smallint (unsigned) | NOT NULL, default `1`, 1–5 | —     |
| `chassis`      | smallint (unsigned) | NOT NULL, default `1`, 1–5 | —     |
| `suspension`   | smallint (unsigned) | NOT NULL, default `1`, 1–5 | —     |
| `electronics`  | smallint (unsigned) | NOT NULL, default `1`, 1–5 | —     |
| `updated_at`   | datetime            | NOT NULL, auto-update      | —     |

**Constraints:** UNIQUE `(team, season)`

---

## PurchasedUpgrade

**App:** `developments` | **Table:** `developments_purchasedupgrade`

History of upgrade purchases by a team.

| Column           | Type                | Constraints               | Notes                            |
| ---------------- | ------------------- | ------------------------- | -------------------------------- |
| `id`             | integer             | PK, auto                  | —                                |
| `team_id`        | FK → `Team`         | NOT NULL, CASCADE         | —                                |
| `season_id`      | FK → `Season`       | NOT NULL, CASCADE         | —                                |
| `department`     | varchar(20)         | NOT NULL                  | See **Department choices** below |
| `previous_level` | smallint (unsigned) | NOT NULL                  | Level before upgrade             |
| `new_level`      | smallint (unsigned) | NOT NULL                  | Level after upgrade              |
| `cost`           | integer (unsigned)  | NOT NULL                  | Credits spent                    |
| `applied`        | boolean             | NOT NULL, default `false` | Whether the upgrade is active    |
| `purchased_at`   | datetime            | NOT NULL, auto            | —                                |

**`department` choices** (`Department`):

| Value          | Label        |
| -------------- | ------------ |
| `engine`       | Engine       |
| `aerodynamics` | Aerodynamics |
| `chassis`      | Chassis      |
| `suspension`   | Suspension   |
| `electronics`  | Electronics  |

**Ordering:** `-purchased_at`

---

## Relationships Diagram

```
Season
├── Race (many)
│   ├── RaceResult (many)  →  Driver, Team
│   └── CreditTransaction (many)  →  Team
├── DriverStanding (many)  →  Driver
├── TeamDevelopment (many)  →  Team
└── PurchasedUpgrade (many)  →  Team

Team
├── Sponsor (many, max 1 is_main)
│   └── SponsorCondition (many)
├── Driver (OneToOne)
├── race_results  (via RaceResult)
├── transactions  (via CreditTransaction)
├── developments  (via TeamDevelopment)
└── upgrades      (via PurchasedUpgrade)

Driver
├── team  (OneToOne → Team)
├── race_results  (via RaceResult)
└── standings     (via DriverStanding)

Circuit
└── Race (many)
```
