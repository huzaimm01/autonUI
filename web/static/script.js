document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("pathForm");
  const resultBox = document.getElementById("result");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      game: document.getElementById("game").value,
      field_width: parseFloat(document.getElementById("fieldWidth").value),
      field_length: parseFloat(document.getElementById("fieldLength").value),
      robot_width: parseFloat(document.getElementById("robotWidth").value),
      robot_length: parseFloat(document.getElementById("robotLength").value),
      robot_height: parseFloat(document.getElementById("robotHeight").value),
      start: [
        parseFloat(document.getElementById("startX").value),
        parseFloat(document.getElementById("startY").value)
      ],
      goal: [
        parseFloat(document.getElementById("goalX").value),
        parseFloat(document.getElementById("goalY").value)
      ]
    };

    try {
      const response = await fetch("/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (data.path) {
        resultBox.value = data.path.map(p => `${p.x}, ${p.y}`).join("\n");
      } else {
        resultBox.value = "Error generating path.";
      }
    } catch (err) {
      resultBox.value = "Server error or invalid response.";
    }
  });
});
