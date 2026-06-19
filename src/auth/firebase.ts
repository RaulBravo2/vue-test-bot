import { initializeApp } from "firebase/app";
import { getAuth, type Auth } from "firebase/auth";

// FIREBASE CONFIGURATION FROM FIREBASE CONSOLE
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID
};

// Sin VITE_FIREBASE_API_KEY (p. ej. en un preview/demo de Railway), getAuth() lanza
// "auth/invalid-api-key" al importar el módulo y la app no llega a montar (pantalla en
// blanco). Para que el preview renderice igual, solo inicializamos Firebase si hay API
// key; si no, `auth` queda en null y useAuth degrada a "no autenticado".
const auth: Auth | null = import.meta.env.VITE_FIREBASE_API_KEY
  ? getAuth(initializeApp(firebaseConfig))
  : null;

export { auth };
