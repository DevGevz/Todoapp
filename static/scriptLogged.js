const GridTaskNameInput = document.getElementById("TaskNameInput");
const GridTaskTextInput = document.getElementById("TaskInput");
const ValidTaskButton = document.getElementById("ValidTask");
const taskGrid = document.getElementById("taskGrid");
const iconInputLabel = document.querySelector(".Image-Input");
let selectedIconClass = null;

// Patterns pour les colonnes (somme ≤ 6)
const patterns = [
  [2, 2, 2],
  [3, 2, 1],
  [2, 1,1 , 2],
  [1, 2, 1, 2]
];
let patternIndex = 0;
let itemIndexInPattern = 0;

// Sélection de l’icône
iconInputLabel.querySelectorAll("i").forEach(icon => {
  icon.addEventListener("click", () => {
    selectedIconClass = icon.className;

    // Highlight sélection
    iconInputLabel.querySelectorAll("i").forEach(ic => (ic.style.opacity = "0.4"));
    icon.style.opacity = "1";
  });
});

// Ajouter une tâche dans la grille
function addTaskToGrid(task) {
  const card = document.createElement("div");
  card.className = "task-card";
  card.dataset.id = task.id; // ⚡ stocke l'id dans l'attribut data-id

  card.innerHTML = `
    <div class="task-header">
      <button onclick="deleteTask(this)">
        <i class="fa-solid fa-trash"></i>
      </button>
    </div>
    <div class="task-content">
      <div class="task-title">
        <h2>${task.name}</h2>
        <i class="${task.image_path}" style="font-size: 2rem;"></i>
      </div>
      <p>${task.text}</p>
    </div>
  `;

  // Choisir span selon pattern ou responsive
  if (window.innerWidth < 700) {
    card.style.gridColumn = "span 1";
  } else {
    const currentPattern = patterns[patternIndex];
    const span = currentPattern[itemIndexInPattern];
    card.style.gridColumn = `span ${span}`;

    // Avancer dans le pattern
    itemIndexInPattern++;
    if (itemIndexInPattern >= currentPattern.length) {
      itemIndexInPattern = 0;
      patternIndex = (patternIndex + 1) % patterns.length;
    }
  }

  taskGrid.appendChild(card);
}


// Recalcul des spans au resize
window.addEventListener("resize", () => {
  const cards = taskGrid.querySelectorAll(".task-card");
  cards.forEach((card, idx) => {
    if (window.innerWidth < 700) {
      card.style.gridColumn = "span 1";
    } else {
      let totalIndex = 0;
      for (let p = 0; p < patterns.length; p++) {
        for (let i = 0; i < patterns[p].length; i++) {
          if (totalIndex === idx) {
            card.style.gridColumn = `span ${patterns[p][i]}`;
            return;
          }
          totalIndex++;
        }
      }
    }
  });
});

// Charger les tâches initiales depuis backend
window.initialTasks.forEach(task => {
  addTaskToGrid({
    ...task,
    image_path: task.image_path || "fa-solid fa-star"
  });
});

// Ajouter une nouvelle tâche
ValidTaskButton.addEventListener("click", async () => {
  const name = GridTaskNameInput.value.trim();
  const text = GridTaskTextInput.value.trim();

  if (!selectedIconClass || !name || !text) {
    alert("Veuillez remplir tous les champs et sélectionner une icône.");
    return;
  }

  const formData = new FormData();
  formData.append("name", name);
  formData.append("text", text);
  formData.append("image_path", selectedIconClass);

  const response = await fetch("/add_task", {
    method: "POST",
    body: formData
  });

  if (response.ok) {
    const data = await response.json();

    addTaskToGrid({
      id: data.id, // ⚡ l'id retourné par Flask
      name,
      text,
      image_path: selectedIconClass
    });

    // Reset inputs
    GridTaskNameInput.value = "";
    GridTaskTextInput.value = "";
    iconInputLabel.querySelectorAll("i").forEach(ic => (ic.style.opacity = "1"));
    selectedIconClass = null;
  } else {
    alert("Erreur lors de l'ajout de la tâche.");
  }
});



function deleteTask(button) {
  const card = button.closest(".task-card");
  const taskId = card.dataset.id;

  fetch("/delete_task", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ id: taskId })
}).then(async response => {
  if (response.ok) {
    card.remove();
  } else {
    const err = await response.json();
    console.error("Erreur backend:", err);
    alert("Erreur lors de la suppression.");
  }
});

}


const ManageAccountBtn = document.getElementById("AccountBtn");
const main = document.querySelector("main");
const container = document.querySelector(".container");

ManageAccountBtn.addEventListener("click", (e) => {
  e.preventDefault();

  // Si container est visible
  if (!container.classList.contains("unactive")) {
    container.classList.add("unactive");  // masque container
    main.classList.remove("unactive");    // affiche main
  } else {
    container.classList.remove("unactive"); // affiche container
    main.classList.add("unactive");         // masque main
  }
});

