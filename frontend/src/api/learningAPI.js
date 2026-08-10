import api from './axios';

/**
 * Learning API client
 */

// ─── Categories ──────────────────────────────────────────────

export const getCourseCategories = (params = {}) => api.get('/learning/categories/', { params });
export const getCourseCategory = (id) => api.get(`/learning/categories/${id}/`);
export const createCourseCategory = (data) => api.post('/learning/categories/', data);
export const updateCourseCategory = (id, data) => api.put(`/learning/categories/${id}/`, data);
export const deleteCourseCategory = (id) => api.delete(`/learning/categories/${id}/`);

// ─── Courses ─────────────────────────────────────────────────

export const getCourses = (params = {}) => api.get('/learning/courses/', { params });
export const getCourse = (id) => api.get(`/learning/courses/${id}/`);
export const createCourse = (data) => api.post('/learning/courses/', data);
export const updateCourse = (id, data) => api.put(`/learning/courses/${id}/`, data);
export const patchCourse = (id, data) => api.patch(`/learning/courses/${id}/`, data);
export const deleteCourse = (id) => api.delete(`/learning/courses/${id}/`);

// ─── Course Actions ──────────────────────────────────────────

export const enrollInCourse = (courseId) => api.post(`/learning/courses/${courseId}/enroll/`);
export const unenrollFromCourse = (courseId) => api.post(`/learning/courses/${courseId}/unenroll/`);
export const getMyCourses = () => api.get('/learning/courses/my_courses/');

// ─── Lessons ─────────────────────────────────────────────────

export const getLessons = (params = {}) => api.get('/learning/lessons/', { params });
export const getLesson = (id) => api.get(`/learning/lessons/${id}/`);

// ─── Enrollments ─────────────────────────────────────────────

export const getEnrollments = (params = {}) => api.get('/learning/enrollments/', { params });
export const getEnrollment = (id) => api.get(`/learning/enrollments/${id}/`);
export const completeLesson = (enrollmentId, lessonId) =>
  api.post(`/learning/enrollments/${enrollmentId}/complete_lesson/`, { lesson_id: lessonId });

// ─── Quizzes ──────────────────────────────────────────────────

export const getQuiz = (id) => api.get(`/learning/quizzes/${id}/`);
export const submitQuiz = (quizId, answers) =>
  api.post(`/learning/quizzes/${quizId}/submit/`, { answers });

// ─── Certificates ────────────────────────────────────────────

export const getCertificate = (enrollmentId) =>
  api.get(`/learning/certificates/${enrollmentId}/`);

// ─── Default export ──────────────────────────────────────────

export default {
  getCourseCategories,
  getCourseCategory,
  createCourseCategory,
  updateCourseCategory,
  deleteCourseCategory,
  getCourses,
  getCourse,
  createCourse,
  updateCourse,
  patchCourse,
  deleteCourse,
  enrollInCourse,
  unenrollFromCourse,
  getMyCourses,
  getLessons,
  getLesson,
  getEnrollments,
  getEnrollment,
  completeLesson,
  getQuiz,
  submitQuiz,
  getCertificate,
};