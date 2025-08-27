  document.querySelectorAll("span.email").forEach(span => {
    span.style.cursor = "pointer"; // curseur main
    span.addEventListener("click", () => {
      const text = span.innerText.trim();
      navigator.clipboard.writeText(text)
        .then(() => {
          console.log("Copié :", text);
          // petit feedback visuel
          const oldColor = span.style.color;
          span.style.color = "red";
          setTimeout(() => span.style.color = oldColor, 200);
        })
        .catch(err => {
          console.error("Erreur de copie :", err);
        });
    });
  });