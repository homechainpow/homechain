const API_URL = 'http://localhost:5000';

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    showHome();
    fetchChainData();
    // Poll updates
    setInterval(fetchChainData, 3000);
});

async function fetchChainData() {
    try {
        const res = await fetch(`${API_URL}/chain`);
        const data = await res.json();

        // Update Stats
        document.getElementById('statHeight').innerText = data.length;
        document.getElementById('statSupply').innerText = data.supply.toLocaleString();

        // Render Blocks (Reverse order)
        const tbody = document.getElementById('blocksTable');
        // Only update if changes to avoid jitter, simplified for V1
        let html = '';
        [...data.chain].reverse().slice(0, 10).forEach(block => {
            const timeAgo = Math.floor((Date.now() / 1000 - block.timestamp)) + 's ago';
            html += `
                <tr>
                    <td><span style="color:var(--primary); font-weight:bold">#${block.index}</span></td>
                    <td>${timeAgo}</td>
                    <td><span class="addr-link" onclick="showAddress('${block.validator}')">${block.validator.substring(0, 8)}...</span></td>
                    <td>${block.transactions.length}</td>
                    <td>10 $HOME</td>
                </tr>
            `;
        });
        tbody.innerHTML = html;

    } catch (e) {
        console.error(e);
        document.getElementById('statStatus').innerText = 'Offline';
        document.getElementById('statStatus').style.color = 'red';
    }
}

async function showAddress(address) {
    // Switch View
    document.getElementById('view-home').classList.remove('active-view');
    document.getElementById('view-address').classList.add('active-view');
    window.scrollTo(0, 0);

    if (address === "SYSTEM") {
        document.getElementById('addrTitle').innerText = "SYSTEM (Protocol)";
        return;
    }

    document.getElementById('addrTitle').innerText = address;

    // Fetch Details
    const res = await fetch(`${API_URL}/address/${address}`);
    const data = await res.json();

    document.getElementById('addrBalance').innerText = data.balance + ' $HOME';
    document.getElementById('addrStake').innerText = data.stake + ' $HOME';

    const tagsDiv = document.getElementById('addrTags');
    tagsDiv.innerHTML = '';
    if (data.is_validator) {
        tagsDiv.innerHTML += '<span class="addr-badge">VALIDATOR</span>';
    }

    // Render History
    const tbody = document.getElementById('addrTxTable');
    let html = '';
    data.history.reverse().forEach(item => {
        const tx = item.tx;
        const isIncoming = tx.receiver === address;
        const type = isIncoming ? '<span style="color:#00ff00">IN</span>' : '<span style="color:orange">OUT</span>';
        const otherParty = isIncoming ? tx.sender : tx.receiver;

        html += `
            <tr>
                <td>${type}</td>
                <td><span class="addr-link" onclick="showAddress('${otherParty}')">${otherParty.substring(0, 12)}...</span></td>
                <td>${tx.amount} $HOME</td>
                <td>Block #${item.block}</td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
}

function showHome() {
    document.getElementById('view-address').classList.remove('active-view');
    document.getElementById('view-home').classList.add('active-view');
}

async function mineBlock() {
    await fetch(`${API_URL}/mine`);
    fetchChainData();
}
