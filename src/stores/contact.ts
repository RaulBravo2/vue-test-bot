import { defineStore } from "pinia";
import axios from "axios";
// TYPES
import { ContactPayload } from "@/types/Contact";

export const useContact = defineStore("contact", () => {
  const sendContactMessage = (payload: ContactPayload) => {
    return axios.post("/api/contact", payload);
  };

  return { sendContactMessage };
});
