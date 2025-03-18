const API_BASE_URL = "http://127.0.0.1:8000";

export async function createRFQ(rfqData) {
    const response = await fetch(`${API_BASE_URL}/rfq/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(rfqData),
    });
    return response.json();
}
