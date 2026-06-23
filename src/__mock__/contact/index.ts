import Mock from "../mock";

const requiredFields = ["name", "email", "subject", "message"];

Mock.onPost("/api/contact").reply(({ data }) => {
  if (!data) return [400, { message: "Invalid request" }];

  const payload = JSON.parse(data);
  const missingField = requiredFields.find((field) => !payload[field]);

  if (missingField) {
    return [400, { message: `${missingField} is required` }];
  }

  return [200, payload];
});
