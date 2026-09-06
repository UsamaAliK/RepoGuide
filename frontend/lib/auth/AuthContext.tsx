"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { getToken, getUsername, storeSession, clearSession } from "@/lib/auth/token";
import { login as apiLogin, register as apiRegister } from "@/lib/api/auth";

type AuthContextValue = {
  token: string | null;
  username: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [username, setUsername] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setToken(getToken());
    setUsername(getUsername());
    setIsLoading(false);
  }, []);

  async function login(name: string, password: string) {
    const response = await apiLogin(name, password);
    storeSession(response.access_token, name);
    setToken(response.access_token);
    setUsername(name);
  }

  async function register(name: string, password: string) {
    const response = await apiRegister(name, password);
    storeSession(response.access_token, name);
    setToken(response.access_token);
    setUsername(name);
  }

  function logout() {
    clearSession();
    setToken(null);
    setUsername(null);
  }

  return (
    <AuthContext.Provider
      value={{ token, username, isAuthenticated: token !== null, isLoading, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}