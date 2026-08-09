
import api from "./axios";

export async function getTickets() {
	const response = await api.get("/tickets");
	return response.data;
}

export async function getTicket(ticketId) {
	const response = await api.get(`/tickets/${ticketId}`);
	return response.data;
}

export async function createTicket(payload) {
	const response = await api.post(`/tickets`, payload);
	return response.data;
}

