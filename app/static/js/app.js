document.addEventListener("DOMContentLoaded", () => {
    const addButton = document.getElementById("add-sale-row");
    const items = document.getElementById("sale-items");
    if (!addButton || !items) return;

    addButton.addEventListener("click", () => {
        const first = items.querySelector(".sale-row");
        const row = first.cloneNode(true);
        row.querySelector("select").selectedIndex = 0;
        row.querySelector("input").value = "1";
        items.appendChild(row);
    });

    items.addEventListener("click", (event) => {
        if (!event.target.classList.contains("remove-row")) return;
        const rows = items.querySelectorAll(".sale-row");
        if (rows.length === 1) return;
        event.target.closest(".sale-row").remove();
    });
});

function numberFormat(value) {
    return new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 3 }).format(value);
}
