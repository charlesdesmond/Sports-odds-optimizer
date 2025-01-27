document.addEventListener("DOMContentLoaded", () => {
    const sportSelect = document.getElementById("sport");
    const gameSelect = document.getElementById("game");
    const resultsDiv = document.getElementById("odds-info");
    const form = document.getElementById("arb-form");
    const stakeInput = document.getElementById("stake");

    // Fetch sports and populate the dropdown
    fetch("/api/sports")
        .then(response => response.json())
        .then(data => {
            data.forEach(sport => {
                const option = document.createElement("option");
                option.value = sport.key;
                option.textContent = sport.title;
                sportSelect.appendChild(option);
            });
        })
        .catch(error => console.error("Error fetching sports:", error));

    // Fetch games when a sport is selected
    sportSelect.addEventListener("change", () => {
        const sportKey = sportSelect.value;

        if (sportKey) {
            fetch(`/api/games?sport=${sportKey}`)
                .then(response => response.json())
                .then(data => {
                    gameSelect.innerHTML = '<option value="">--Select a Game--</option>'; // Reset games dropdown
                    gameSelect.disabled = false;

                    data.forEach(game => {
                        const option = document.createElement("option");
                        option.value = game.id;
                        option.textContent = `${game.home_team} vs ${game.away_team}`;
                        gameSelect.appendChild(option);
                    });
                })
                .catch(error => console.error("Error fetching games:", error));
        } else {
            gameSelect.innerHTML = '<option value="">--Select a Game--</option>';
            gameSelect.disabled = true;
        }
    });

    // Fetch best odds when a game is selected
    gameSelect.addEventListener("change", () => {
        const gameId = gameSelect.value;
        const sportKey = sportSelect.value;

        if (gameId) {
            fetch(`/api/odds?game_id=${gameId}&sport=${sportKey}`)
                .then(response => response.json())
                .then(data => {
                    resultsDiv.innerHTML = `
                        <h3>Best Odds</h3>
                        <p>${Object.keys(data)[0]}: ${data[Object.keys(data)[0]].odds} (Bookmaker: ${data[Object.keys(data)[0]].bookmaker})</p>
                        <p>${Object.keys(data)[1]}: ${data[Object.keys(data)[1]].odds} (Bookmaker: ${data[Object.keys(data)[1]].bookmaker})</p>
                    `;
                })
                .catch(error => console.error("Error fetching odds:", error));
        } else {
            resultsDiv.innerHTML = '';
        }
    });

    // Handle form submission for arbitrage calculation
    form.addEventListener("submit", (event) => {
        event.preventDefault();

        const odds1 = parseFloat(gameSelect.options[gameSelect.selectedIndex].dataset.odds1);
        const odds2 = parseFloat(gameSelect.options[gameSelect.selectedIndex].dataset.odds2);
        const stake = parseFloat(stakeInput.value);

        fetch("/api/calculate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ odds1, odds2, stake }),
        })
            .then(response => response.json())
            .then(data => {
                resultsDiv.innerHTML += `
                    <h3>Arbitrage Calculation</h3>
                    <p>Bet 1: $${data["Bet 1"]}</p>
                    <p>Bet 2: $${data["Bet 2"]}</p>
                    <p>Payout: $${data["Payout"]}</p>
                    <p>ROI: ${data["ROI"]}%</p>
                `;
            })
            .catch(error => console.error("Error calculating arbitrage:", error));
    });
});