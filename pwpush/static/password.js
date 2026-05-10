const submitBtn = document.getElementById("submitBtn");
const passwordInput = document.getElementById("passwordInput");
const messageBox = document.getElementById("message");

function showMessage(text, type = "success") {
    messageBox.style.display = "block";
    messageBox.className = `message ${type}`;
    messageBox.innerHTML = text;
}

submitBtn.addEventListener("click", async () => {
    try {
        const password = passwordInput.value.trim();

        if (!password) {
            showMessage("Добрячок, ты забыл ввести пароль :(", "error");
            return;
        }

        const payload = {
            password
        };

        const response = await fetch(`${document.location.pathname}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        let json = null;

        try {
            json = await response.json();
        } catch (_) {
            showMessage("Server returned invalid JSON.", "error");
            return;
        }

        if (response.status === 200 && json.status === "ok") {
            document.location = `${document.location.pathname}/view`
            return;
        }
        showMessage(
                "Добрячок, пароль неправильный :(", "error"
            );

    } catch (err) {
        showMessage("Something went wrong", "error");
    }
});