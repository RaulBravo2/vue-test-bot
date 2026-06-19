import { reactive } from "vue";
import {
  User,
  signOut,
  updateProfile,
  setPersistence,
  browserLocalPersistence,
  browserSessionPersistence,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword
} from "firebase/auth";
// FIREBASE CONFIG
import { auth } from "./firebase";

// ==============================================================
interface LoginData {
  email: string;
  password: string;
  rememberMe: boolean;
}

interface RegisterData {
  name: string;
  email: string;
  password: string;
}

interface AuthState {
  user: User | null;
  loading: boolean;
  error: Error | null;
}
// ==============================================================

let authReadyCallback: ((user: User | null) => void) | null = null;

// Las operaciones de auth requieren Firebase configurado. Si `auth` es null (sin
// VITE_FIREBASE_*), lanzamos un error claro en vez de un crash poco descriptivo.
const ensureAuth = (): NonNullable<typeof auth> => {
  if (!auth) {
    throw new Error(
      "Firebase no está configurado: definí las variables VITE_FIREBASE_* para usar el login."
    );
  }
  return auth;
};

export const useAuth = () => {
  const state = reactive<AuthState>({
    user: null,
    loading: true,
    error: null
  });

  // WATCH FOR AUTHENTICATION STATE CHANGES
  if (auth) {
    onAuthStateChanged(
      auth,
      (currentUser) => {
        state.user = currentUser;
        state.loading = false;
        if (authReadyCallback) authReadyCallback(currentUser);
      },
      (error) => {
        state.error = error;
        state.loading = false;
      }
    );
  } else {
    // Firebase no configurado (preview/demo sin VITE_FIREBASE_*): no hay sesión posible.
    state.loading = false;
    if (authReadyCallback) authReadyCallback(null);
  }

  const login = async ({ email, password, rememberMe }: LoginData) => {
    try {
      state.loading = true;
      state.error = null;

      const a = ensureAuth();
      await setPersistence(a, rememberMe ? browserLocalPersistence : browserSessionPersistence);
      return await signInWithEmailAndPassword(a, email, password);
    } catch (error) {
      state.error = error as Error;
      throw error;
    } finally {
      state.loading = false;
    }
  };

  const register = async ({ name, email, password }: RegisterData) => {
    try {
      state.loading = true;
      state.error = null;

      const userCredential = await createUserWithEmailAndPassword(ensureAuth(), email, password);
      await updateProfile(userCredential.user, { displayName: name });
      return userCredential;
    } catch (error) {
      state.error = error as Error;
      throw error;
    } finally {
      state.loading = false;
    }
  };

  const logout = async () => {
    try {
      state.loading = true;
      state.error = null;

      await signOut(ensureAuth());
    } catch (error) {
      state.error = error as Error;
      throw error;
    } finally {
      state.loading = false;
    }
  };

  const waitForAuth = () => {
    return new Promise((resolve) => {
      // Sin Firebase no hay sesión que esperar: resolver ya para no bloquear el router.
      if (!auth) {
        resolve(null);
        return;
      }
      if (state.user) {
        resolve(state.user);
      } else {
        authReadyCallback = (user) => resolve(user);
      }
    });
  };

  return {
    login,
    state,
    logout,
    register,
    waitForAuth
  };
};
