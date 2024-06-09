import authHeader from './auth.header';
import config from '../config';

export default async function makeApiCall({
  endpoint = "",
  method = "GET",
  headers = { "Content-Type": "application/json" },
  body = {},
  timeout = 90000,
  binaryResponse = false,
  streamResponse = false,
} = {}) {
  if (endpoint === "") {
    throw new Error("Endpoint is required");
  }
  if(method.toUpperCase() === "GET") {
    // For GET requests, we don't need to send any data in the request body
    body = undefined;
  } else if (body instanceof FormData) {
    // For FormData, do not set Content-Type header
    delete headers["Content-Type"];
  } else {
    body = JSON.stringify(body);
  }

  try {
    const controller = new AbortController();
    //const callTimeout = setTimeout(() => {
    //  controller.abort();
    //}, timeout);

    //headers = {"Content-Type": "application/json"}
    if (!endpoint.includes("registerUser")) {
      headers = {
        ...headers,
        ...authHeader()
      }
    }

    const response = await fetch(endpoint, {
      method,
      headers,
      body: body,
      signal: controller.signal
    });

    if (streamResponse) {
      return response;
    }
    const data = await response.json();
    if (config.DEBUG == 1) {
      console.log("response: ", data)
    }

    // not sure if its good idea
    //if (response.ok) {
    if (response.ok && data.code === 200) {
      return { code: 200, success: true, message: data.message }
    } else if (response.status === 401) {
      return { code: 401, success: false, message: "Unauthorized" };
    } else {
      //throw new Error(data.message || "Something went wrong!");
      return { code: data.code, success: false, message: data.message }
    }

  } catch (error) {
    if (error.name === "AbortError") {
      return { code: 408, success: false, message: "Problem reaching auth server. Please contact us!" };
    } else {
      console.log("error: ", error)
      return { code: 500, success: false, message: "Something went wrong" };
    }
  }
}
