# Bug report: CSV export fails when filtered results include emoji

## Environment

- Product: Admin Dashboard
- Browser: Chrome 125
- Account type: Team admin
- Date first noticed: 2026-07-03

## Steps to reproduce

1. Open the Admin Dashboard.
2. Go to `Reports > User Activity`.
3. Set the search filter to `feedback 😀`.
4. Click `Export CSV`.

## Expected behavior

The dashboard downloads a CSV file containing the filtered user activity rows.

## Observed behavior

The export button changes to `Preparing...` for about 10 seconds, then the page
shows `Something went wrong`. No CSV file is downloaded.

## Impact

Team admins cannot export filtered activity reports when matching rows contain
emoji. This blocks weekly reporting for teams that collect free-text feedback.

## Extra notes

The same export works when the filter is `feedback` without the emoji.
