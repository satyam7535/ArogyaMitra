/**
 * Express middleware for schema validation using Zod
 * @param {import("zod").ZodSchema} schema
 * @param {"body" | "query" | "params"} source
 */
export const validate = (schema, source = "body") => {
  return (req, res, next) => {
    const rawData = source === "body" ? req.body : source === "query" ? req.query : req.params;
    const data = rawData !== undefined ? rawData : {};
    const result = schema.safeParse(data);

    if (!result.success) {
      return res.status(400).json({
        message: "Request validation failed",
        code: "VALIDATION_ERROR",
        errors: (result.error.issues || result.error.errors || []).map((e) => ({
          field: (e.path || []).join("."),
          message: e.message,
        })),
      });
    }

    if (source === "body") {
      req.body = result.data;
    } else if (source === "query") {
      req.validatedQuery = result.data;
    } else {
      req.params = result.data;
    }

    next();
  };
};

export default validate;
