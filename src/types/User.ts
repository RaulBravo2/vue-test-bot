export interface User {
  id: number;
  name: string;
  role: string;
  image: string;
  email: string;
  phone: string;
  status: string;
  address: string;
  createAt: string;
  age: number;
}

export interface UserPayload {
  name: string;
  role: string;
  image: string;
  email: string;
  phone: string;
  status: string;
  address: string;
  age: number;
}
