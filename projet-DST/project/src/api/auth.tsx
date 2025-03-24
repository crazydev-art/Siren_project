// src/api/auth.tsx
export const loginUser = async (email: string, password: string) => {
  try {
      const response = await fetch("http://141.145.207.10:8000/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json", "Accept": "application/json", },
          body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
          return { success: true, token: data.token };
      } else {
          return { success: false, message: data.message || 'Login failed' };
      }
  } catch (error) {
      console.error('Error during login:', error);
      return { success: false, message: 'Network error' };
  }
};

export async function registerUser(username: string, email: string, password: string) {
  try {
      const response = await fetch("http://141.145.207.10:8000/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json", "Accept": "application/json", },
          body: JSON.stringify({ username, email, password }),
      });

      const data = await response.json();

      if (response.ok) {
          return { success: true, message: "Registration successful!" };
      } else {
          // Check if the error is due to the user already existing
          if (data.detail && data.detail.includes(" already exists")) {
              console.log(data.detail);
              return { success: false, message: "User already exists, please sign in." };
          } else {
              return { success: false, message: data.detail || "Registration failed." };
          }
      }
  } catch (error) {
      console.error('Error during registration:', error);
      return { success: false, message: 'Network error' };
  }
}
