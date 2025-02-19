document.getElementById('login-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const username = document.getElementById('username').value
    const password = document.getElementById('password').value

    const data = {
        username: username,
        password: password
    }

    try {
        const response = await fetch('http://127.0.0.1:8000/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            const result = await response.json();

            const token = result.token;

            if (token) {
                document.cookie = `user_access_token=${token}; path=/; max-age=86400`;
                window.location.replace("/");
            } else {
                alert('Токен не найден в ответе!');
            }
        } else {
            alert('Ошибка авторизации');
        }
    } catch (error) {
        alert('Произошла ошибка при отправке запроса');
        console.error(error);
    }
});