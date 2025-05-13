document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById("sidebar");
    const mainContent = document.querySelector(".container-fluid");
    const toggleButton = document.getElementById("sidebarToggle");

    function toggleSidebar() {
        sidebar.classList.toggle("shrink");
        mainContent.classList.toggle("shrink");
        toggleButton.classList.toggle("shrink");
        
        // Force reflow to ensure smooth transition
        window.requestAnimationFrame(() => {
            document.body.style.marginLeft = sidebar.classList.contains("shrink") ? "70px" : "250px";
        });
        
        // Save state to localStorage
        const isShrunk = sidebar.classList.contains("shrink");
        localStorage.setItem("sidebarShrunk", isShrunk);
    }

    // Add click event listener
    if (toggleButton) {
        toggleButton.addEventListener("click", toggleSidebar);
    }

    // Restore sidebar state
    const isShrunk = localStorage.getItem("sidebarShrunk") === "true";
    if (isShrunk) {
        sidebar.classList.add("shrink");
        mainContent.classList.add("shrink");
        toggleButton.classList.add("shrink");
        document.body.style.marginLeft = "70px";
    }
});