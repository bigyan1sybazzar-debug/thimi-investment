window.onload = async function () {
  const data = await apiRequest("/deposits/admin/dashboard/");

  document.getElementById("totalMembers").innerHTML = data.total_members;

  document.getElementById("pendingDeposits").innerHTML = data.pending_deposits;

  document.getElementById("approvedDeposits").innerHTML =
    data.approved_deposits;

  document.getElementById("totalCollection").innerHTML =
    "Rs. " + data.total_collection;
};
