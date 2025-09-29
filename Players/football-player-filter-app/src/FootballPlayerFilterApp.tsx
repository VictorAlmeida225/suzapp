import React, { useState, useEffect } from "react";

const CONFIG = {
  season: "2024",
  leagues: [
    { id: 39, code: "ENG", name: "Premier League (Inglaterra)" },
    { id: 61, code: "FRA", name: "Ligue 1 (França)" },
    { id: 135, code: "ITA", name: "Serie A (Itália)" },
    { id: 140, code: "ESP", name: "La Liga (Espanha)" },
    { id: 78, code: "GER", name: "Bundesliga (Alemanha)" },
    { id: 71, code: "BRA", name: "Brasileirão Série A" },
  ],
};

interface Player {
  id: number;
  name: string;
  age: number;
  nationality: string;
  position: string;
  number: number | null;
  photo?: string;
  teamLogo?: string;
}

export default function FootballPlayerFilterApp(): JSX.Element {
  const [players, setPlayers] = useState<Player[]>([]);
  const [selectedLeagues, setSelectedLeagues] = useState<string[]>(
    CONFIG.leagues.map((l) => l.code)
  );
  const [selectedPositions, setSelectedPositions] = useState<string[]>([
    "Goleiro",
    "Defensor",
    "Meia",
    "Atacante",
  ]);
  const [selectedNationalities, setSelectedNationalities] = useState<string[]>(
    []
  );
  const [ageRange, setAgeRange] = useState<[number, number]>([16, 45]);
  const [shirtNumberRange, setShirtNumberRange] = useState<[number, number]>([
    1, 99,
  ]);

  const useMock = true;

  useEffect(() => {
    if (useMock) {
      const mockPlayers: Player[] = [
        {
          id: 1,
          name: "Neymar Jr.",
          age: 31,
          nationality: "Brasil",
          position: "Atacante",
          number: 10,
          photo: "https://media.api-sports.io/football/players/276.png",
          teamLogo: "https://media.api-sports.io/football/teams/85.png",
        },
        {
          id: 2,
          name: "Harry Kane",
          age: 30,
          nationality: "Inglaterra",
          position: "Atacante",
          number: 9,
          photo: "https://media.api-sports.io/football/players/19088.png",
          teamLogo: "https://media.api-sports.io/football/teams/47.png",
        },
        {
          id: 3,
          name: "Manuel Neuer",
          age: 37,
          nationality: "Alemanha",
          position: "Goleiro",
          number: 1,
          photo: "https://media.api-sports.io/football/players/28.png",
          teamLogo: "https://media.api-sports.io/football/teams/157.png",
        },
      ];
      setPlayers(mockPlayers);
    }
  }, []);

  const filteredPlayers = players.filter((p) => {
    const inPosition = selectedPositions.includes(p.position);
    const inNationality =
      selectedNationalities.length === 0 ||
      selectedNationalities.includes(p.nationality);
    const inAge = p.age >= ageRange[0] && p.age <= ageRange[1];
    const inNumber =
      (p.number ?? 0) >= shirtNumberRange[0] &&
      (p.number ?? 0) <= shirtNumberRange[1];
    return inPosition && inNationality && inAge && inNumber;
  });

  const toggle = (value: string, state: string[], setter: any) => {
    setter(
      state.includes(value)
        ? state.filter((v) => v !== value)
        : [...state, value]
    );
  };

  const allNationalities = Array.from(new Set(players.map((p) => p.nationality)));

  return (
    <div className="bg-gray-950 text-white min-h-screen">
      <header className="sticky top-0 z-10 bg-gray-900 border-b border-gray-700 shadow-lg p-4">
        <h1 className="text-3xl font-bold text-center">⚽ Filtro de Jogadores</h1>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Filtros */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Ligas */}
          <div className="bg-gray-900 rounded-xl p-4 shadow-md">
            <h2 className="text-lg font-semibold mb-2">Ligas</h2>
            <div className="flex flex-wrap gap-2">
              {CONFIG.leagues.map((l) => (
                <button
                  key={l.code}
                  onClick={() =>
                    toggle(l.code, selectedLeagues, setSelectedLeagues)
                  }
                  className={`px-3 py-1 rounded-full text-sm transition 
                    ${selectedLeagues.includes(l.code)
                      ? "bg-green-500 text-black"
                      : "bg-gray-700 hover:bg-gray-600"
                    }`}
                >
                  {l.name}
                </button>
              ))}
            </div>
          </div>

          {/* Posições */}
          <div className="bg-gray-900 rounded-xl p-4 shadow-md">
            <h2 className="text-lg font-semibold mb-2">Posições</h2>
            <div className="flex flex-wrap gap-2">
              {["Goleiro", "Defensor", "Meia", "Atacante"].map((pos) => (
                <button
                  key={pos}
                  onClick={() =>
                    toggle(pos, selectedPositions, setSelectedPositions)
                  }
                  className={`px-3 py-1 rounded-full text-sm transition 
                    ${selectedPositions.includes(pos)
                      ? "bg-blue-500 text-black"
                      : "bg-gray-700 hover:bg-gray-600"
                    }`}
                >
                  {pos}
                </button>
              ))}
            </div>
          </div>

          {/* Nacionalidades */}
          <div className="bg-gray-900 rounded-xl p-4 shadow-md">
            <h2 className="text-lg font-semibold mb-2">Nacionalidades</h2>
            <div className="flex flex-wrap gap-2">
              {allNationalities.map((nat) => (
                <button
                  key={nat}
                  onClick={() =>
                    toggle(nat, selectedNationalities, setSelectedNationalities)
                  }
                  className={`px-3 py-1 rounded-full text-sm transition 
                    ${selectedNationalities.includes(nat)
                      ? "bg-yellow-400 text-black"
                      : "bg-gray-700 hover:bg-gray-600"
                    }`}
                >
                  {nat}
                </button>
              ))}
            </div>
          </div>

          {/* Idade */}
          <div className="bg-gray-900 rounded-xl p-4 shadow-md">
            <h2 className="text-lg font-semibold mb-2">Idade</h2>
            <div className="flex gap-2 items-center">
              <input
                type="number"
                value={ageRange[0]}
                onChange={(e) =>
                  setAgeRange([Number(e.target.value), ageRange[1]])
                }
                className="text-black w-16 p-1 rounded"
              />
              <span>-</span>
              <input
                type="number"
                value={ageRange[1]}
                onChange={(e) =>
                  setAgeRange([ageRange[0], Number(e.target.value)])
                }
                className="text-black w-16 p-1 rounded"
              />
            </div>
          </div>

          {/* Camisa */}
          <div className="bg-gray-900 rounded-xl p-4 shadow-md">
            <h2 className="text-lg font-semibold mb-2">Número Camisa</h2>
            <div className="flex gap-2 items-center">
              <input
                type="number"
                value={shirtNumberRange[0]}
                onChange={(e) =>
                  setShirtNumberRange([
                    Number(e.target.value),
                    shirtNumberRange[1],
                  ])
                }
                className="text-black w-16 p-1 rounded"
              />
              <span>-</span>
              <input
                type="number"
                value={shirtNumberRange[1]}
                onChange={(e) =>
                  setShirtNumberRange([
                    shirtNumberRange[0],
                    Number(e.target.value),
                  ])
                }
                className="text-black w-16 p-1 rounded"
              />
            </div>
          </div>
        </div>

        {/* Lista de jogadores */}
        <h2 className="text-2xl font-bold mt-8 mb-4">
          Jogadores ({filteredPlayers.length})
        </h2>
        <div className="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {filteredPlayers.map((player) => (
            <div
              key={player.id}
              className="bg-gray-900 rounded-xl shadow-lg p-4 flex flex-col items-center hover:scale-[1.02] transition"
            >
              <div className="flex items-center justify-center relative">
                <img
                  src={player.photo}
                  alt={player.name}
                  className="w-20 h-20 rounded-full border-2 border-gray-700 object-cover"
                />
                {player.teamLogo && (
                  <img
                    src={player.teamLogo}
                    alt="escudo"
                    className="w-8 h-8 absolute bottom-0 right-0 rounded-full bg-white p-1"
                  />
                )}
              </div>
              <div className="text-center mt-3">
                <p className="font-bold text-lg">{player.name}</p>
                <p className="text-sm text-gray-300">{player.position}</p>
                <p className="text-sm text-gray-400">{player.nationality}</p>
                <p className="text-sm text-gray-400">
                  {player.age} anos - #{player.number}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
