import express from "express";
import { createWorker, getWorkers, login, logout, deleteWorker } from "../controller/worker.controller.js";
import verifyToken from "../middlewares/auth.middleware.js";

const workerRouter = express.Router();

// Admin-only routes
workerRouter.post("/", verifyToken(["admin"]), createWorker);       // POST /api/v1/worker
workerRouter.get("/", verifyToken(["admin"]), getWorkers);          // GET  /api/v1/worker
workerRouter.delete("/:id", verifyToken(["admin"]), deleteWorker);  // DELETE /api/v1/worker/:id

// Worker auth routes (public)
workerRouter.post("/login", login);                                  // POST /api/v1/worker/login
workerRouter.post("/logout", verifyToken(["worker"]), logout);       // POST /api/v1/worker/logout

export default workerRouter;
