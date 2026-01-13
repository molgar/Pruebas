# Basketball Games Calendar

A simple web application to track and export basketball games for multiple players/categories.

## Features

- 📅 **Visual Calendar View** - See all games in a monthly calendar format
- 🎯 **Category Filtering** - Filter games by Mini, Infantil, or Cadete categories
- 📄 **PDF Export** - Export current month's games to PDF
- 📱 **Calendar Export** - Export games to iCalendar format (.ics)
- 🔄 **Calendar Subscription** - Subscribe to auto-updating calendar feeds
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile devices

## Usage

### Viewing Games

1. Open `basketball-calendar.html` in your web browser
2. Use the **Previous** and **Next** buttons to navigate between months
3. Click on any game to view full details
4. Click on category badges (Mini, Infantil, Cadete) to filter games

### Exporting to PDF

1. Click the **"📄 Export to PDF"** button
2. The PDF will include all games for the current month (respecting active filters)
3. The file will be automatically downloaded

### Exporting to Calendar Apps

#### Option 1: Download and Import (Immediate)

1. Click the **"📅 Export to Calendar"** button
2. Select which games to export:
   - **Download All Games** - All 33 games across all categories
   - **Download Mini Only** - Carmen's games (16 games)
   - **Download Infantil Only** - Marta's games (6 games)
   - **Download Cadete Only** - Lucía's games (11 games)
3. A `.ics` file will be downloaded
4. Open the file to import into your calendar app:
   - **iOS**: Tap the file, then tap "Add All"
   - **Google Calendar**: Import via Settings → Import & Export
   - **Outlook**: Import via File → Open & Export → Import/Export

#### Option 2: Subscribe (Auto-Update)

For automatic updates when games change:

**iOS (iPhone/iPad):**
1. Go to Settings → Calendar → Accounts → Add Account → Other
2. Select "Add Subscribed Calendar"
3. Enter one of these URLs:
   - All Games: `webcal://molgar.github.io/Pruebas/calendars/basketball-all.ics`
   - Mini Only: `webcal://molgar.github.io/Pruebas/calendars/basketball-mini.ics`
   - Infantil Only: `webcal://molgar.github.io/Pruebas/calendars/basketball-infantil.ics`
   - Cadete Only: `webcal://molgar.github.io/Pruebas/calendars/basketball-cadete.ics`

**Google Calendar:**
1. Open Google Calendar on desktop
2. Click "+" next to "Other calendars"
3. Select "From URL"
4. Paste the URL (replace `webcal://` with `https://`)

**Outlook:**
1. Open Outlook → Calendar
2. Add calendar → Subscribe from web
3. Paste the URL

**Note:** Subscribed calendars typically update every 24-48 hours. For immediate updates, use the download option.

## Updating Calendar Files

When games change in `games-data.js`:

1. Run the calendar generator:
   ```bash
   node generate-calendars.js
   ```

2. Commit and push the updated calendar files:
   ```bash
   git add calendars/*.ics
   git commit -m "Update calendar files"
   git push
   ```

3. Subscribed calendars will auto-update within 24-48 hours

## File Structure

```
.
├── basketball-calendar.html   # Main application
├── games-data.js              # Game data source
├── generate-calendars.js      # Calendar file generator
├── calendars/                 # Static calendar files for subscription
│   ├── basketball-all.ics
│   ├── basketball-mini.ics
│   ├── basketball-infantil.ics
│   └── basketball-cadete.ics
└── README.md                  # This file
```

## Game Data Format

Games are stored in `games-data.js` with the following structure:

```javascript
{
  "id": 1,
  "player": "marta",           // carmen, marta, or lucia
  "date": "2026-01-26",        // YYYY-MM-DD format
  "time": "19:00",             // HH:MM format (24-hour)
  "opponent": "SEK B",
  "location": "Tejera",
  "notes": "FERE Infantil"
}
```

## Categories

- **Mini** (Carmen) - 16 games - FEDE Mini league
- **Infantil** (Marta) - 6 games - FERE Infantil league
- **Cadete** (Lucía) - 11 games - Cadete Femenino league

## Technical Details

- **Frontend**: Vanilla JavaScript, no frameworks
- **Libraries**:
  - jsPDF & jsPDF-autotable for PDF export
  - ics.js for calendar export
- **Calendar Format**: iCalendar (.ics) RFC 5545 compliant
- **Event Duration**: 90 minutes per game
- **Hosting**: GitHub Pages
- **Browser Support**: Modern browsers (Chrome, Firefox, Safari, Edge)

## Development

To make changes:

1. Edit `games-data.js` to update game information
2. Edit `basketball-calendar.html` for UI changes
3. Run `node generate-calendars.js` to regenerate calendar files
4. Test locally by opening `basketball-calendar.html` in a browser
5. Commit and push to update the live version on GitHub Pages

## License

This is a personal project for tracking basketball games.
