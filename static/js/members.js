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
        const hasFront = !!member.gov_id_front;
        const hasBack = !!member.gov_id_back;

        let govIdBadge = `<span class="badge bg-secondary">Not Uploaded</span>`;
        if (hasFront && hasBack) {
            govIdBadge = `<span class="badge bg-success"><i class="bi bi-check-circle me-1"></i>Front &amp; Back</span>`;
        } else if (hasFront) {
            govIdBadge = `<span class="badge bg-info text-dark"><i class="bi bi-check me-1"></i>Front Only</span>`;
        } else if (hasBack) {
            govIdBadge = `<span class="badge bg-info text-dark"><i class="bi bi-check me-1"></i>Back Only</span>`;
        }

        table.innerHTML += `
            <tr>
                <td><span class="badge bg-dark">${member.member_id}</span></td>
                <td><strong>${fullName}</strong><div class="small text-muted">${member.username}</div></td>
                <td class="text-muted small">${member.email || "—"}</td>
                <td>${member.phone || "—"}</td>
                <td>
                    ${govIdBadge}
                    ${(hasFront || hasBack) ? `
                        <div class="mt-1">
                            ${hasFront ? `<a href="${member.gov_id_front}" target="_blank" class="btn btn-xs btn-outline-primary py-0 px-1 me-1" style="font-size:0.75rem;">Front</a>` : ''}
                            ${hasBack ? `<a href="${member.gov_id_back}" target="_blank" class="btn btn-xs btn-outline-primary py-0 px-1" style="font-size:0.75rem;">Back</a>` : ''}
                        </div>
                    ` : ''}
                </td>
                <td>
                    ${member.is_active_member
                ? '<span class="badge bg-success">Active</span>'
                : '<span class="badge bg-danger">Inactive</span>'}
                </td>
                <td>
                    <a href="/members/profile/${member.id}/" class="btn btn-sm btn-outline-info" title="View Profile">
                        <i class="bi bi-eye"></i>
                    </a>
                    <a href="/members/edit/${member.id}/" class="btn btn-sm btn-outline-primary ms-1" title="Edit Member">
                        <i class="bi bi-pencil"></i> Edit
                    </a>
                </td>
            </tr>
        `;
    });
};