window.onload = () => {
  console.log("Website Loaded.");

  const loginForm = document.getElementById("login-form");

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const username = document.getElementById("username").value.trim();
      const password = document.getElementById("password").value.trim();

      try {
        const response = await fetch("http://localhost:3001/api/login", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
          console.log("✅ Logged in:", data);
          callCompanyApp(data.company); // step 2 call
        } else {
          alert("Login failed: " + data.message);
        }
      } catch (err) {
        console.error("Error logging in:", err);
        alert("Something went wrong.");
      }
    });
  } else {
    console.warn("Login form not found.");
  }
};
