import Mock from "./mock";

import "./users";
import "./orders";
import "./products";
import "./invoices";
import "./contact";

Mock.onAny().passThrough();
