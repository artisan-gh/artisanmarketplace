import api from "./axios";

// =============================================================================
// CATEGORY API
// =============================================================================

// Get all categories
export const getCategories = (params = {}) =>
    api.get("/categories/", { params });

// Get active categories
export const getActiveCategories = () =>
    api.get("/categories/active/");

// Get category by ID
export const getCategory = (id) =>
    api.get(`/categories/${id}/`);

// Create category
export const createCategory = (data) =>
    api.post("/categories/", data);

// Update category
export const updateCategory = (id, data) =>
    api.put(`/categories/${id}/`, data);

// Partial update
export const patchCategory = (id, data) =>
    api.patch(`/categories/${id}/`, data);

// Delete category
export const deleteCategory = (id) =>
    api.delete(`/categories/${id}/`);

// Category statistics
export const getCategoryStatistics = () =>
    api.get("/categories/statistics/");


// =============================================================================
// SUBCATEGORY API
// =============================================================================

// Get all subcategories
export const getSubCategories = (params = {}) =>
    api.get("/categories/subcategories/", { params });

// Get active subcategories
export const getActiveSubCategories = () =>
    api.get("/categories/subcategories/active/");

// Get one subcategory
export const getSubCategory = (id) =>
    api.get(`/categories/subcategories/${id}/`);

// Create subcategory
export const createSubCategory = (data) =>
    api.post("/categories/subcategories/", data);

// Update subcategory
export const updateSubCategory = (id, data) =>
    api.put(`/categories/subcategories/${id}/`, data);

// Partial update
export const patchSubCategory = (id, data) =>
    api.patch(`/categories/subcategories/${id}/`, data);

// Delete subcategory
export const deleteSubCategory = (id) =>
    api.delete(`/categories/subcategories/${id}/`);

// Subcategory statistics
export const getSubCategoryStatistics = () =>
    api.get("/categories/subcategories/statistics/");