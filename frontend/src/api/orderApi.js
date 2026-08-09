import api from "./axios";

export async function getOrders() {
	const response = await api.get("/orders");
	return response.data;
}

export async function getOrder(orderId) {
	const response = await api.get(`/orders/${orderId}`);
	return response.data;
}
