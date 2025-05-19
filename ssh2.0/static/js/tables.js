document.addEventListener("DOMContentLoaded", function () {
    function loadTable(endpoint, tableId) {
        fetch(endpoint)
            .then(response => response.json())
            .then(data => {
                const tableBody = document.getElementById(tableId);
                tableBody.innerHTML = "";
                data.forEach(row => {
                    let htmlRow = "<tr>";
                    Object.values(row).forEach(value => {
                        htmlRow += `<td>${value}</td>`;
                    });
                    htmlRow += "</tr>";
                    tableBody.innerHTML += htmlRow;
                });
            })
            .catch(error => console.error(`Errore nel recupero di ${endpoint}:`, error));
    }

    loadTable("/get-studenti", "studenti-table");
    loadTable("/get-aziende", "aziende-table");
    loadTable("/get-associazioni", "associazioni-table");
});
