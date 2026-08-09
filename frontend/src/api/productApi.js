import api from "./axios";

export async function getProducts() {
	const response = await api.get("/products");
	return response.data;
}

export async function getProduct(productId) {
	const response = await api.get(`/products/${productId}`);
	return response.data;
}
