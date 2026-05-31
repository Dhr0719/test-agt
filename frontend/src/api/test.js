import request from "@/utils/request";

export function testBackend() {
  return request.get("/api/test/");
}