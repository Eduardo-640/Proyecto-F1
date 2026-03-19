Fixtures for sponsors used by `setup_season` management command.

- File: `sponsors_template.json` (contains 25 sponsors and a set of SponsorCondition entries)
- Load with: `python manage.py loaddata platform/apps/teams/fixtures/sponsors_template.json`
- Intended for use with `python manage.py setup_season <season_id> --load-sponsors` which will:
    1. Load the fixture (if `--load-sponsors` provided)
    2. Apply sponsor base bonuses via `apply_sponsor_base <season_id>`
    3. Create an `AccionMasiva` to initialise presets for teams

Notes:

- Each sponsor is `teams.sponsor` and conditions are `teams.sponsorcondition`.
- Conditions map to categories like `aero`, `engine`, `chassis`, `suspension`, `electronics`, `consistency`.
- The `setup_season` command expects the fixture path relative to the developments app; keep this file at `platform/apps/teams/fixtures/sponsors_template.json`.
