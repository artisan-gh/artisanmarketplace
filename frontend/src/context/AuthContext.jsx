
/* eslint-disable react-refresh/only-export-components */

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from "react";

import api from "../api/axios";

// ============================================================
// AUTH CONTEXT
// ============================================================

export const AuthContext = createContext(null);

// ============================================================
// USE AUTH HOOK
// ============================================================

export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
};

// ============================================================
// AUTH PROVIDER
// ============================================================

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // ==========================================================
  // LOGOUT
  // ==========================================================

  const logout = useCallback(() => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    localStorage.removeItem("user_type");

    setUser(null);

    // IMPORTANT:
    // Do not use window.location.href = "/login" here.
    // The component that calls logout() should navigate
    // using React Router.
  }, []);

  // ==========================================================
  // FETCH CURRENT USER
  // ==========================================================

  useEffect(() => {
    let mounted = true;

    const getUser = async () => {
      const token = localStorage.getItem("accessToken");

      // No token means the user is not authenticated
      if (!token) {
        if (mounted) {
          setLoading(false);
        }

        return;
      }

      try {
        const response = await api.get("/auth/users/me/");

        if (mounted) {
          setUser(response.data);

          // Keep user type synchronized
          if (response.data?.user_type) {
            localStorage.setItem(
              "user_type",
              response.data.user_type
            );
          }
        }
      } catch (error) {
        console.error("Failed to fetch current user:", error);

        if (mounted) {
          // Token is invalid/expired and could not be refreshed
          localStorage.removeItem("accessToken");
          localStorage.removeItem("refreshToken");
          localStorage.removeItem("user_type");

          setUser(null);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    getUser();

    return () => {
      mounted = false;
    };
  }, []);

  // ==========================================================
  // LOGIN
  // ==========================================================

  const login = async (email, password) => {
    try {
      const { data } = await api.post("/auth/token/", {
        email: email.trim(),
        password,
      });

      // --------------------------------------------------------
      // Validate response
      // --------------------------------------------------------

      if (!data?.access || !data?.refresh) {
        throw new Error(
          "Login succeeded but the server did not return authentication tokens."
        );
      }

      // --------------------------------------------------------
      // Store JWT tokens
      // --------------------------------------------------------

      localStorage.setItem("accessToken", data.access);
      localStorage.setItem("refreshToken", data.refresh);

      // --------------------------------------------------------
      // Store user type
      // --------------------------------------------------------

      const userType =
        data?.user?.user_type ||
        data?.user_type ||
        null;

      if (userType) {
        localStorage.setItem("user_type", userType);
      }

      // --------------------------------------------------------
      // Store user
      // --------------------------------------------------------

      const authenticatedUser = data?.user || null;

      setUser(authenticatedUser);

      return data;
    } catch (error) {
      console.error("Login error:", error);

      // --------------------------------------------------------
      // Extract useful backend error message
      // --------------------------------------------------------

      const responseData = error?.response?.data;

      if (responseData) {
        // SimpleJWT/custom authentication errors
        if (typeof responseData.detail === "string") {
          throw {
            detail: responseData.detail,
          };
        }

        // Backend may return:
        // { email: [...] }
        if (responseData.email) {
          throw {
            detail: Array.isArray(responseData.email)
              ? responseData.email.join(" ")
              : String(responseData.email),
          };
        }

        // Backend may return:
        // { password: [...] }
        if (responseData.password) {
          throw {
            detail: Array.isArray(responseData.password)
              ? responseData.password.join(" ")
              : String(responseData.password),
          };
        }

        // Generic backend message
        if (responseData.message) {
          throw {
            detail: responseData.message,
          };
        }
      }

      // --------------------------------------------------------
      // Network error
      // --------------------------------------------------------

      if (!error?.response) {
        throw {
          detail:
            "Unable to connect to the server. Please check your internet connection and try again.",
        };
      }

      // --------------------------------------------------------
      // HTTP error fallback
      // --------------------------------------------------------

      throw {
        detail: "Invalid email or password.",
      };
    }
  };

  // ==========================================================
  // REGISTER
  // ==========================================================

  const register = async (userData) => {
    try {
      /*
       * IMPORTANT:
       * If userData is FormData, do not manually specify
       * multipart/form-data.
       *
       * The browser must generate the multipart boundary.
       */

      const isFormData = userData instanceof FormData;

      const config = isFormData
        ? {
            headers: {
              "Content-Type": undefined,
            },
          }
        : {
            headers: {
              "Content-Type": "application/json",
            },
          };

      const { data } = await api.post(
        "/auth/register/",
        userData,
        config
      );

      // --------------------------------------------------------
      // If registration also authenticates the user
      // --------------------------------------------------------

      if (data?.access && data?.refresh) {
        localStorage.setItem(
          "accessToken",
          data.access
        );

        localStorage.setItem(
          "refreshToken",
          data.refresh
        );

        const userType =
          data?.user?.user_type ||
          data?.user_type ||
          null;

        if (userType) {
          localStorage.setItem(
            "user_type",
            userType
          );
        }

        setUser(data?.user || data);
      }

      return data;
    } catch (error) {
      console.error("Registration error:", error);

      const responseData = error?.response?.data;

      if (responseData) {
        throw responseData;
      }

      if (!error?.response) {
        throw {
          message:
            "Unable to connect to the server. Please check your internet connection and try again.",
        };
      }

      throw {
        message:
          "Registration failed. Please try again.",
      };
    }
  };

  // ==========================================================
  // UPDATE PROFILE
  // ==========================================================

  const updateProfile = async (profileData) => {
    try {
      const isFormData = profileData instanceof FormData;

      const config = isFormData
        ? {
            headers: {
              "Content-Type": undefined,
            },
          }
        : {
            headers: {
              "Content-Type": "application/json",
            },
          };

      const response = await api.patch(
        "/auth/users/me/",
        profileData,
        config
      );

      // Update local user state
      setUser(response.data);

      // Keep user type synchronized
      if (response.data?.user_type) {
        localStorage.setItem(
          "user_type",
          response.data.user_type
        );
      }

      return response.data;
    } catch (error) {
      console.error("Profile update error:", error);

      const responseData = error?.response?.data;

      if (responseData) {
        throw responseData;
      }

      if (!error?.response) {
        throw {
          message:
            "Unable to connect to the server.",
        };
      }

      throw {
        message:
          "Profile update failed. Please try again.",
      };
    }
  };

  // ==========================================================
  // AUTH CONTEXT VALUE
  // ==========================================================

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    updateProfile,
  };

  // ==========================================================
  // PROVIDER
  // ==========================================================

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};



