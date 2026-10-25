/**
 * Organization Scoping Middleware
 * Enforces multi-tenant isolation by ensuring that any resource query is strictly
 * bounded to req.user.organization.
 *
 * Crucial Security Rule:
 * Returns 404 (Not Found) rather than 403 (Forbidden) when a resource belongs
 * to another organization, to prevent enumeration of IDs across tenants.
 */

export const enforceOrgScope = (resourceModel, idParam = "id") => {
  return async (req, res, next) => {
    try {
      const resourceId = req.params[idParam];
      if (!resourceId) {
        return next();
      }

      if (!req.user || !req.user.organization) {
        return res.status(401).json({ message: "Unauthorized: Missing organization context" });
      }

      const resource = await resourceModel.findById(resourceId);
      if (!resource) {
        return res.status(404).json({ message: "Resource not found" });
      }

      // Check organization ownership
      if (resource.organization.toString() !== req.user.organization.toString()) {
        // Return 404 to avoid leaking existence of cross-tenant resource
        return res.status(404).json({ message: "Resource not found" });
      }

      // Attach verified scoped resource to request
      req.scopedResource = resource;
      next();
    } catch (error) {
      next(error);
    }
  };
};

/**
 * Filter helper that attaches user's organization to query filters
 */
export const scopeFilter = (req, extraFilter = {}) => {
  return {
    ...extraFilter,
    organization: req.user.organization,
  };
};
