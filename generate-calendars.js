// Basketball Calendar Generator
// Generates static .ics files for webcal subscription

const gamesData = [
  {
    "id": 1,
    "player": "marta",
    "date": "2026-01-12",
    "time": "18:00",
    "opponent": "Teresianas",
    "location": "Teresianas",
    "notes": "FERE Infantil"
  },
  {
    "id": 2,
    "player": "marta",
    "date": "2026-01-26",
    "time": "19:00",
    "opponent": "SEK B",
    "location": "Tejera",
    "notes": "FERE Infantil"
  },
  {
    "id": 3,
    "player": "marta",
    "date": "2026-01-30",
    "time": "18:30",
    "opponent": "Puerta Oscura",
    "location": "Pista verde",
    "notes": "FERE Infantil"
  },
  {
    "id": 4,
    "player": "marta",
    "date": "2026-02-06",
    "time": "19:00",
    "opponent": "Sierra Blanca",
    "location": "Pista verde",
    "notes": "FERE Infantil"
  },
  {
    "id": 5,
    "player": "marta",
    "date": "2026-02-14",
    "time": "10:00",
    "opponent": "SEK",
    "location": "Cerrado de Calderón",
    "notes": "FERE Infantil"
  },
  {
    "id": 6,
    "player": "marta",
    "date": "2026-02-16",
    "time": "19:00",
    "opponent": "Goleta",
    "location": "Pista verde",
    "notes": "FERE Infantil"
  },
  {
    "id": 7,
    "player": "carmen",
    "date": "2026-01-08",
    "time": "17:45",
    "opponent": "León 13 A",
    "location": "León 13 A",
    "notes": "FERE Mini"
  },
  {
    "id": 8,
    "player": "carmen",
    "date": "2026-01-17",
    "time": "11:30",
    "opponent": "Palo '16",
    "location": "Palo '16",
    "notes": "FEDE Mini"
  },
  {
    "id": 9,
    "player": "carmen",
    "date": "2026-01-24",
    "time": "9:30",
    "opponent": "Miramar Torremolinos",
    "location": "SEK",
    "notes": "FEDE Mini"
  },
  {
    "id": 10,
    "player": "carmen",
    "date": "2026-01-31",
    "time": "11:30",
    "opponent": "EBG '15",
    "location": "EBG '15",
    "notes": "FEDE Mini"
  },
  {
    "id": 11,
    "player": "carmen",
    "date": "2026-02-07",
    "time": "9:30",
    "opponent": "Estepona '15",
    "location": "SEK",
    "notes": "FEDE Mini"
  },
  {
    "id": 12,
    "player": "carmen",
    "date": "2026-02-14",
    "time": "13:00",
    "opponent": "Estepona '16",
    "location": "Estepona '16",
    "notes": "FEDE Mini"
  },
  {
    "id": 13,
    "player": "carmen",
    "date": "2026-02-21",
    "time": "13:30",
    "opponent": "CP Mijas",
    "location": "CP Mijas",
    "notes": "FEDE Mini"
  },
  {
    "id": 14,
    "player": "carmen",
    "date": "2026-03-07",
    "time": "9:30",
    "opponent": "San Patricio",
    "location": "SEK",
    "notes": "FEDE Mini"
  },
  {
    "id": 15,
    "player": "carmen",
    "date": "2026-03-14",
    "time": "9:30",
    "opponent": "El Palo '16",
    "location": "SEK",
    "notes": "FEDE Mini"
  },
  {
    "id": 16,
    "player": "carmen",
    "date": "2026-03-21",
    "time": "10:30",
    "opponent": "Miramar Torremolinos",
    "location": "Miramar Torremolinos",
    "notes": "FEDE Mini"
  },
  {
    "id": 17,
    "player": "carmen",
    "date": "2026-04-11",
    "time": "9:30",
    "opponent": "EBG '15",
    "location": "SEK",
    "notes": "FEDE Mini"
  },
  {
    "id": 18,
    "player": "carmen",
    "date": "2026-04-19",
    "time": "9:30",
    "opponent": "Estepona '15",
    "location": "Estepona '15",
    "notes": "FEDE Mini"
  },
  {
    "id": 19,
    "player": "carmen",
    "date": "2026-04-25",
    "time": "9:30",
    "opponent": "Estepona '16",
    "location": "SEK",
    "notes": "FEDE Mini"
  },
  {
    "id": 20,
    "player": "carmen",
    "date": "2026-05-09",
    "time": "9:30",
    "opponent": "CP Mijas",
    "location": "SEK",
    "notes": "FEDE Mini"
  },
  {
    "id": 21,
    "player": "carmen",
    "date": "2026-05-15",
    "time": "17:00",
    "opponent": "San Patricio",
    "location": "San Patricio",
    "notes": "FEDE Mini"
  },
  {
    "id": 22,
    "player": "lucia",
    "date": "2025-11-28",
    "time": "19:00",
    "opponent": "SEK",
    "location": "Ciudad Deportiva Cártama",
    "notes": "Cadete Femenino"
  },
  {
    "id": 23,
    "player": "lucia",
    "date": "2025-12-14",
    "time": "10:00",
    "opponent": "MBK",
    "location": "SEK Pabellón",
    "notes": "Cadete Femenino"
  },
  {
    "id": 24,
    "player": "lucia",
    "date": "2026-01-17",
    "time": "17:30",
    "opponent": "SEK",
    "location": "Pabellón El Maulí",
    "notes": "Cadete Femenino"
  },
  {
    "id": 25,
    "player": "lucia",
    "date": "2026-01-18",
    "time": "10:00",
    "opponent": "Torremolinos",
    "location": "SEK Pabellón",
    "notes": "Cadete Femenino"
  },
  {
    "id": 26,
    "player": "lucia",
    "date": "2026-01-25",
    "time": "11:00",
    "opponent": "SEK",
    "location": "Pabellón La Mosca",
    "notes": "Cadete Femenino"
  },
  {
    "id": 27,
    "player": "lucia",
    "date": "2026-02-08",
    "time": "10:00",
    "opponent": "Marbella",
    "location": "SEK Pabellón",
    "notes": "Cadete Femenino"
  },
  {
    "id": 28,
    "player": "lucia",
    "date": "2026-02-15",
    "time": "10:00",
    "opponent": "Cártama",
    "location": "SEK Pabellón",
    "notes": "Cadete Femenino"
  },
  {
    "id": 29,
    "player": "lucia",
    "date": "2026-02-21",
    "time": "17:00",
    "opponent": "SEK",
    "location": "Revello de Toro",
    "notes": "Cadete Femenino"
  },
  {
    "id": 30,
    "player": "lucia",
    "date": "2026-03-08",
    "time": "10:00",
    "opponent": "Antequera",
    "location": "SEK Pabellón",
    "notes": "Cadete Femenino"
  },
  {
    "id": 31,
    "player": "lucia",
    "date": "2026-03-14",
    "time": "17:00",
    "opponent": "SEK",
    "location": "Pistas Polideportivas Torremolinos",
    "notes": "Cadete Femenino"
  },
  {
    "id": 32,
    "player": "lucia",
    "date": "2026-03-22",
    "time": "10:00",
    "opponent": "El Palo",
    "location": "SEK Pabellón",
    "notes": "Cadete Femenino"
  },
  {
    "id": 33,
    "player": "lucia",
    "date": "2026-04-19",
    "time": "17:00",
    "opponent": "SEK",
    "location": "Pabellón Carlos Cabezas",
    "notes": "Cadete Femenino"
  }
];

const playerInfo = {
  carmen: { name: 'Mini', category: 'Mini' },
  marta: { name: 'Infantil', category: 'Infantil' },
  lucia: { name: 'Cadete', category: 'Cadete' }
};

function formatICSDate(date, time) {
  const [year, month, day] = date.split('-');
  const [hour, minute] = time.split(':');
  return `${year}${month}${day}T${hour.padStart(2, '0')}${minute.padStart(2, '0')}00`;
}

function addMinutes(date, time, minutes) {
  const [year, month, day] = date.split('-').map(Number);
  const [hour, minute] = time.split(':').map(Number);
  const d = new Date(year, month - 1, day, hour, minute);
  d.setMinutes(d.getMinutes() + minutes);

  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const dy = String(d.getDate()).padStart(2, '0');
  const h = String(d.getHours()).padStart(2, '0');
  const min = String(d.getMinutes()).padStart(2, '0');

  return `${y}${m}${dy}T${h}${min}00`;
}

function escapeICS(text) {
  return text.replace(/\\/g, '\\\\').replace(/;/g, '\\;').replace(/,/g, '\\,').replace(/\n/g, '\\n');
}

function generateICSContent(games, calendarName) {
  let ics = 'BEGIN:VCALENDAR\r\n';
  ics += 'VERSION:2.0\r\n';
  ics += 'PRODID:-//Basketball Calendar//EN\r\n';
  ics += `X-WR-CALNAME:${calendarName}\r\n`;
  ics += 'X-WR-TIMEZONE:Europe/Madrid\r\n';
  ics += 'CALSCALE:GREGORIAN\r\n';
  ics += 'METHOD:PUBLISH\r\n';

  games.forEach(game => {
    const player = playerInfo[game.player];
    const startDate = formatICSDate(game.date, game.time);
    const endDate = addMinutes(game.date, game.time, 90);

    ics += 'BEGIN:VEVENT\r\n';
    ics += `UID:game-${game.id}@basketballcalendar.github.io\r\n`;
    ics += `DTSTART:${startDate}\r\n`;
    ics += `DTEND:${endDate}\r\n`;
    ics += `SUMMARY:${escapeICS(game.time + ' - ' + player.category + ' vs ' + game.opponent)}\r\n`;
    ics += `DESCRIPTION:${escapeICS(player.category + ' game vs ' + game.opponent + '\\n' + (game.notes || ''))}\r\n`;
    ics += `LOCATION:${escapeICS(game.location)}\r\n`;
    ics += `CATEGORIES:${player.category}\r\n`;
    ics += 'STATUS:CONFIRMED\r\n';
    ics += 'END:VEVENT\r\n';
  });

  ics += 'END:VCALENDAR\r\n';
  return ics;
}

// Generate calendar files
const fs = require('fs');
const path = require('path');

const calendarsDir = path.join(__dirname, 'calendars');
if (!fs.existsSync(calendarsDir)) {
  fs.mkdirSync(calendarsDir);
}

// All games
const allGamesICS = generateICSContent(gamesData, 'Basketball - All Games');
fs.writeFileSync(path.join(calendarsDir, 'basketball-all.ics'), allGamesICS);
console.log('✓ Generated basketball-all.ics');

// Mini only
const miniGames = gamesData.filter(g => g.player === 'carmen');
const miniICS = generateICSContent(miniGames, 'Basketball - Mini');
fs.writeFileSync(path.join(calendarsDir, 'basketball-mini.ics'), miniICS);
console.log('✓ Generated basketball-mini.ics');

// Infantil only
const infantilGames = gamesData.filter(g => g.player === 'marta');
const infantilICS = generateICSContent(infantilGames, 'Basketball - Infantil');
fs.writeFileSync(path.join(calendarsDir, 'basketball-infantil.ics'), infantilICS);
console.log('✓ Generated basketball-infantil.ics');

// Cadete only
const cadeteGames = gamesData.filter(g => g.player === 'lucia');
const cadeteICS = generateICSContent(cadeteGames, 'Basketball - Cadete');
fs.writeFileSync(path.join(calendarsDir, 'basketball-cadete.ics'), cadeteICS);
console.log('✓ Generated basketball-cadete.ics');

console.log('\nAll calendar files generated successfully!');
