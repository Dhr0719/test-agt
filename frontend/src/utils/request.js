import axios from "axios";

const request = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 30000,
});

request.interceptors.response.use(
  response => {
    return response.data;
  },
  error => {
    console.error("请求出错：", error);
    return Promise.reject(error);
  }
);

export default request;