// Basketball Games Data
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
