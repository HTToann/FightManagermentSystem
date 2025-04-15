    document.addEventListener("DOMContentLoaded", function () {
        fetchFlashMessages();
    });

    function fetchFlashMessages() {
        let messages = JSON.parse(document.getElementById("flash-messages").textContent);

        if (messages.length > 0) {
            messages.forEach(([category, message]) => {
                Swal.fire({
                    icon: category === "success" ? "success" : "error",
                    title: message,
                    showConfirmButton: false,
                    timer: 2500
                });
            });
        }
    }