// ========================================================
// AUTH LOGIN / REGISTER TAB SWITCH
// ========================================================
const authTabs = document.querySelectorAll(".auth-tab");
const tabContents = document.querySelectorAll(".tab-content");

authTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    // Remove active from all tabs
    authTabs.forEach((t) => t.classList.remove("active"));
    tabContents.forEach((c) => c.classList.remove("active"));

    // Activate clicked tab
    tab.classList.add("active");

    // Show matching content
    const target = tab.dataset.tab;
    document.getElementById(`${target}-tab`).classList.add("active");
  });
});

// ==========================================================
// GLOBAL DOM READY
// ==========================================================
document.addEventListener("DOMContentLoaded", function () {
  // ========================================================
  // AUTO-HIDE BOOTSTRAP ALERTS
  // ========================================================
  document.querySelectorAll(".alert").forEach((alert) => {
    setTimeout(() => {
      bootstrap.Alert.getOrCreateInstance(alert).close();
    }, 5000);
  });

  document.querySelectorAll(".toast").forEach((toastEl) => {
    const toast = new bootstrap.Toast(toastEl, {
      delay: 2500,
      autohide: true,
    });

    toast.show();
  });

  // ========================================================
  // BOOKING MODAL (STAFF)
  // ========================================================
  const bookingModal = document.getElementById("bookingModal");

  if (bookingModal) {
    bookingModal.addEventListener("show.bs.modal", function (event) {
      const button = event.relatedTarget;
      if (!button) return;

      document.getElementById("modalFacilityId").value =
        button.dataset.facilityId || "";

      document.getElementById("modalFacilityName").textContent =
        button.dataset.facilityName || "";

      document.getElementById("modalFacilityCapacity").textContent =
        button.dataset.facilityCapacity || "";

      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);

      bookingModal.querySelector('input[name="booking_date"]').value = tomorrow
        .toISOString()
        .split("T")[0];

      bookingModal.querySelector('input[name="start_time"]').value = "09:00";
      bookingModal.querySelector('input[name="end_time"]').value = "10:00";
    });
  }

  // ========================================================
  // FACILITY EDIT MODAL (ADMIN) ✅ CORRECT
  // ========================================================
  const editModal = document.getElementById("facilityEditModal");

  if (editModal) {
    editModal.addEventListener("show.bs.modal", function (event) {
      const button = event.relatedTarget;

      console.log("EDIT DATA:", button.dataset);

      editModal.querySelector('[name="facility_id"]').value = button.dataset.id;
      editModal.querySelector('[name="name"]').value = button.dataset.name;
      editModal.querySelector('[name="capacity"]').value =
        button.dataset.capacity;
      editModal.querySelector('[name="status"]').value = button.dataset.status;
    });
  }

  // ========================================================
  // STATS (ONLY IF API EXISTS)
  // ========================================================
  if (document.getElementById("stat-total")) {
    refreshStats();
    setInterval(refreshStats, 5000);
  }
});

// ==========================================================
// STATS AUTO REFRESH
// ==========================================================
function refreshStats() {
  fetch("/api/stats")
    .then((res) => {
      if (!res.ok) return null;
      return res.json();
    })
    .then((data) => {
      if (!data) return;

      document.getElementById("stat-total").textContent = data.total;
      document.getElementById("stat-pending").textContent = data.pending;
      document.getElementById("stat-approved").textContent = data.approved;
    })
    .catch(() => {});
}
