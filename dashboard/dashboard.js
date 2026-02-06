const API_BASE = window.location.origin;

async function updateDashboard() {
    try {
        const chainResponse = await fetch(`${API_BASE}/chain`);
        const chainData = await chainResponse.json();

        const height = chainData.length;
        const lastBlock = chainData[chainData.length - 1];

        // Update Stats Header
        document.getElementById('statHeight').innerText = height;
        document.getElementById('statSupply').innerText = (height * 132575).toLocaleString(); // Estimated
        document.getElementById('statDifficulty').innerText = lastBlock.difficulty || 'N/A';

        // Update Blocks Table
        const tableBody = document.getElementById('blocksTable');
        tableBody.innerHTML = '';

        // Show last 10 blocks
        const latestBlocks = [...chainData].reverse().slice(0, 10);
        latestBlocks.forEach((block, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="glow-text">#${block.index}</td>
                <td><span class="time-badge">${new Date(block.timestamp * 1000).toLocaleTimeString()}</span></td>
                <td><span class="addr-chip" onclick="viewAddress('${block.validator}')">${block.validator.substring(0, 12)}...</span></td>
                <td>${block.transactions.length}</td>
                <td class="reward-text">+132,575</td>
            `;
            tableBody.appendChild(row);
        });

    } catch (e) {
        console.error("Dashboard update failed", e);
    }
}

function viewAddress(addr) {
    window.location.hash = `addr-${addr}`;
    // Future: Address page logic
}

// Initial pull and interval
updateDashboard();
setInterval(updateDashboard, 5000);
