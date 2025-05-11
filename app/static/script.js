let currentSort = { field: 'pid', order: 'asc' };
let currentFilter = '';

function loadProcessData() {
    fetch(`/api/processes?sort_by=${currentSort.field}&order=${currentSort.order}&name=${encodeURIComponent(currentFilter)}`)
        .then(res => res.json())
        .then(data => {
            updateProcessTable(data.processes);
            document.getElementById('processCount').textContent = data.total;
            document.getElementById('lastUpdate').textContent = data.timestamp;
        });
}

function updateProcessTable(processes) {
    const tbody = document.getElementById('processTableBody');
    tbody.innerHTML = '';
    if (processes.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `<td colspan="6" class="text-center">No processes found</td>`;
        tbody.appendChild(row);
        return;
    }

    processes.forEach(process => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${process.pid}</td>
            <td>${process.name}</td>
            <td>${process.cpu_percent}%</td>
            <td>${process.memory_percent}%</td>
            <td>${process.status}</td>
            <td><a href="/process/${process.pid}" class="btn btn-sm btn-outline-primary">Details</a></td>
        `;
        tbody.appendChild(row);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    loadProcessData();
    setInterval(loadProcessData, 5000);

    document.querySelectorAll('.sortable').forEach(header => {
        header.addEventListener('click', () => {
            const field = header.getAttribute('data-sort');
            currentSort.order = (currentSort.field === field && currentSort.order === 'asc') ? 'desc' : 'asc';
            currentSort.field = field;
            loadProcessData();
        });
    });

    document.getElementById('processFilter').addEventListener('input', (e) => {
        currentFilter = e.target.value;
        loadProcessData();
    });
});
