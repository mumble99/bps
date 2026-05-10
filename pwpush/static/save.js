const submitBtn = document.getElementById("submitBtn");
const fileInput = document.getElementById("fileInput");
const textData = document.getElementById("textData");
const expire = document.getElementById("expire");
const viewCount = document.getElementById("viewCount");
const messageBox = document.getElementById("message");
const togglePasswordBtn = document.getElementById("togglePasswordBtn");
const passwordContainer = document.getElementById("passwordContainer");
const passwordInput = document.getElementById("passwordInput");

function showMessage(text, type = "success") {
    messageBox.style.display = "block";
    messageBox.className = `message ${type}`;
    messageBox.innerHTML = text;
}

function toBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();

        reader.readAsDataURL(file);

        reader.onload = () => {
            const base64 = reader.result.split(",")[1];
            resolve(base64);
        };

        reader.onerror = reject;
    });
}

function textToBase64(text) {
    return btoa(unescape(encodeURIComponent(text)));
}

submitBtn.addEventListener("click", async () => {
    try {
        messageBox.style.display = "none";

        const file = fileInput.files[0];
        const fileName = fileInput.files[0]?.name;
        const text = textData.value.trim();

        if (!file && !text) {
            showMessage("Please attach a file or enter text.", "error");
            return;
        }

        let type;
        let data;

        if (file) {
            type = "file";
            data = await toBase64(file);
        } else {
            type = "data";
            data = textToBase64(text);
        }

        const days = parseInt(expire.value, 10);

        const payload = {
            type,
            expire: days * 24 * 60 * 60,
            view_count: parseInt(viewCount.value, 10),
            data
        };

        if (type === "file") {
            payload["filename"] = fileName;
        }

        const password = passwordInput.value.trim();

        if (password.length > 0) {
            payload["password"] = password;
        }

        const response = await fetch("/create-secret", {
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

        if (response.status !== 200) {
            showMessage(
                `Request failed with status ${response.status}`, "error"
            );
            return;
        }

        if (json.status !== "ok" || !json.key) {
            showMessage(
                "Something went wrong", "error"
            );
            return;
        }

        let url = `${document.location.href}secret/${json.key}`;

        showMessage(`Сохрани URL секретика: <a href="${url}">${url}</a>`, "success");

    } catch (err) {
        showMessage("Something went wrong", "error");
    }
});

togglePasswordBtn.addEventListener("click", () => {
    const hidden = passwordContainer.style.display === "none";

    passwordContainer.style.display = hidden ? "block" : "none";

    togglePasswordBtn.innerText = hidden
        ? "Убрать пароль"
        : "Добавить пароль";
});