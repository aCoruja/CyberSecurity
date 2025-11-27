const API = "https://cybersecurity-xlct.onrender.com"; // coloque a URL do seu Render

document.getElementById("btnLogin").addEventListener("click", async () => {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    if (!username || !password) {
        document.getElementById("msg").innerText = "Preencha todos os campos";
        return;
    }

    try {
        const res = await fetch(`${API}/login`, {
            method: "POST",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify({username, password})
        });

        const data = await res.json();
        if (!res.ok) {
            document.getElementById("msg").innerText = data.error;
            return;
        }

        document.getElementById("msg").innerText = "Login bem-sucedido!";
        document.getElementById("tokenDiv").style.display = "block";
        document.getElementById("tokenText").value = data.token;

    } catch (err) {
        console.error(err);
        document.getElementById("msg").innerText = "Erro de conexão";
    }
});
