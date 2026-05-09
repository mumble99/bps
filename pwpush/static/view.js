const dataBox = document.getElementById("dataBox");
const copyBtn = document.getElementById("copyBtn");
const messageBox = document.getElementById("message");

let currentData = "";

function showMessage(text, type = "success") {
    messageBox.style.display = "block";
    messageBox.className = `message ${type}`;
    messageBox.innerText = text;
}

function decodeBase64(base64) {
    try {
        return decodeURIComponent(
            escape(atob(base64))
        );
    } catch (_) {
        return atob(base64);
    }
}

function base64ToBlob(base64, mimeType = "application/octet-stream") {
    const bytes = atob(base64);
    const buffer = new Uint8Array(bytes.length);

    for (let i = 0; i < bytes.length; i++) {
        buffer[i] = bytes.charCodeAt(i);
    }

    return new Blob([buffer], { type: mimeType });
}

async function processData() {
    try {
        const data_type = dataBox.getAttribute("type")
        const filename = dataBox.getAttribute("filename")
        if (data_type === "data") {
            currentData = decodeBase64(dataBox.textContent);
            dataBox.innerText = currentData;
        }

        else if (data_type === "file") {
            const blob = base64ToBlob(dataBox.textContent);

            const url = URL.createObjectURL(blob);

            const a = document.createElement("a");
            a.href = url;
            a.download = filename ? filename : "download.bin";

            document.body.appendChild(a);
            a.click();
            a.remove();

            URL.revokeObjectURL(url);

            dataBox.classList.remove("blurred");
            dataBox.innerText = "Началась загрузка файла.";

            copyBtn.style.display = "none";
        }

    } catch (err) {
        showMessage("error", "error");
    }
}

dataBox.addEventListener("click", () => {
    dataBox.classList.toggle("blurred");
});

copyBtn.addEventListener("click", async () => {
    try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(currentData);
        }
        else {
            const textarea = document.createElement("textarea");

            textarea.value = currentData;
            textarea.style.position = "fixed";
            textarea.style.opacity = "0";

            document.body.appendChild(textarea);

            textarea.focus();
            textarea.select();

            const success = document.execCommand("copy");

            document.body.removeChild(textarea);

            if (!success) {
                throw new Error("copy failed");
            }
        }

        showMessage("Copied to clipboard.", "success");

    } catch (err) {
        showMessage("Failed to copy", "error");
    }
});

processData();