document.addEventListener("DOMContentLoaded", function () {

    // =============== ADD FIELD (AJAX) ==================
    const addFieldForm = document.querySelector("#fieldForm");

    if (addFieldForm) {
        addFieldForm.addEventListener("submit", async function (e) {
            e.preventDefault();

            const formData = new FormData(addFieldForm);

            const response = await fetch(addFieldForm.action, {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            // Append new field row
            const row = `
                <tr id="row-${data.id}">
                    <td>${data.field_name}</td>
                    <td>${data.data_type}</td>
                    <td>${data.mandatory ? "Yes" : "No"}</td>
                    <td>${data.primary_key ? "✔" : "—"}</td>
                    <td>
                        <a href="#" data-id="${data.id}" class="delete-field text-danger fs-5">
                            <i class="bi bi-trash"></i>
                        </a>
                    </td>
                </tr>
            `;

            document.getElementById("schemaTableBody")
                .insertAdjacentHTML("beforeend", row);

            addFieldForm.reset();
            document.getElementById("addFieldForm").classList.add("d-none");
        });
    }

    // =============== DELETE FIELD (AJAX) ==================
    document.addEventListener("click", async function (e) {
        if (e.target.closest(".delete-field")) {
            e.preventDefault();
            const id = e.target.closest(".delete-field").dataset.id;

            const res = await fetch(`/recon/structure/field/${id}/delete`, {
                method: "DELETE"
            });

            const data = await res.json();

            if (data.success) {
                document.getElementById(`row-${id}`).remove();
            }
        }
    });

});
