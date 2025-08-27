const register_form = document.querySelector(".register-form");
const login_form = document.querySelector(".login-form");
const switches = document.querySelectorAll(".switchbtn");

switches.forEach(link => {
  link.addEventListener("click", (e) => {
    e.preventDefault();               // évite le reload dû à href=""
    register_form.classList.toggle("unactive");
    login_form.classList.toggle("unactive");
  });
});
