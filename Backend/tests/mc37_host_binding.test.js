import { describe, it, expect, vi, afterEach } from "vitest";
import http from "http";

// Mock connectDB so host binding test runs instantaneously without DB dependency
vi.mock("../src/config/dbConfig.js", () => ({
  default: vi.fn().mockResolvedValue(true),
}));

import app, { startServer } from "../src/index.js";

describe("MC37: Backend HOST Binding Default (127.0.0.1 Containment)", () => {
  let serverInstance = null;
  const originalHost = process.env.HOST;

  afterEach(async () => {
    if (serverInstance && serverInstance.close) {
      await new Promise((resolve) => serverInstance.close(resolve));
      serverInstance = null;
    }
    if (originalHost === undefined) {
      delete process.env.HOST;
    } else {
      process.env.HOST = originalHost;
    }
  });

  it("should strictly bind to 127.0.0.1 by default when process.env.HOST is unset", async () => {
    delete process.env.HOST;

    const listenSpy = vi.spyOn(app, "listen").mockImplementation((port, host, cb) => {
      const s = http.createServer(app);
      if (cb) cb();
      return s;
    });

    serverInstance = await startServer();

    expect(listenSpy).toHaveBeenCalled();
    const boundHost = listenSpy.mock.calls[0][1];
    expect(boundHost).toBe("127.0.0.1");
    expect(boundHost).not.toBe("0.0.0.0");

    listenSpy.mockRestore();
  }, 15000);

  it("should allow explicit HOST override only when configured via environment", async () => {
    process.env.HOST = "10.0.0.5";

    const listenSpy = vi.spyOn(app, "listen").mockImplementation((port, host, cb) => {
      const s = http.createServer(app);
      if (cb) cb();
      return s;
    });

    serverInstance = await startServer();

    expect(listenSpy).toHaveBeenCalled();
    const boundHost = listenSpy.mock.calls[0][1];
    expect(boundHost).toBe("10.0.0.5");

    listenSpy.mockRestore();
  }, 15000);
});
