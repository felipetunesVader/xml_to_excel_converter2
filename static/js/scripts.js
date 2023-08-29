document.addEventListener("DOMContentLoaded", function() {
    let selectAllButton = document.createElement('button');
    selectAllButton.innerText = "Marcar todos";
    selectAllButton.onclick = function() {
        let checkboxes = document.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.checked = true;
        });
    };
    document.querySelector('form').prepend(selectAllButton);
});
