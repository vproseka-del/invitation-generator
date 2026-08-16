function copyLetter() {
    var textarea = document.getElementById("letter-text");
    var status = document.getElementById("copy-status");
    navigator.clipboard.writeText(textarea.value).then(function () {
        status.textContent = "Текст скопирован.";
    }).catch(function () {
        status.textContent = "Не удалось скопировать автоматически. Выделите текст и скопируйте вручную.";
    });
}
