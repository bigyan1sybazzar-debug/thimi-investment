window.onload = async function () {

    const data = await apiRequest("/members/");
    if (!data) return;

    const table = document.getElementById("memberTable");
    table.innerHTML = "";

    if (!data.length) {
        table.innerHTML = `<tr><td colspan="7" class="text-center text-muted py-4">No members found.</td></tr>`;
        return;
    }

    data.forEach(member => {
        const fullName = [member.first_name, member.last_name].filter(Boolean).join(" ") || member.username;
        table.innerHTML += `
            <tr>
                <td><span class="badge bg-secondary">${member.member_id}</span></td>
                <td><strong>${fullName}</strong></td>
                <td class="text-muted small">${member.email || "—"}</td>
                <td>${member.phone || "—"}</td>
                <td class="text-muted small">${member.address || "—"}</td>
                <td>
                    ${member.is_active_member
                ? '<span class="badge bg-success">Active</span>'
                : '<span class="badge bg-danger">Inactive</span>'}
                </td>
                <td>
                    <a href="/members/profile/${member.id}/" class="btn btn-sm btn-outline-info">
                        <i class="bi bi-eye"></i>
                    </a>
                    <a href="/members/edit/${member.id}/" class="btn btn-sm btn-outline-primary ms-1">
                        <i class="bi bi-pencil"></i> Edit
                    </a>
                </td>
            </tr>
        `;
    });
};