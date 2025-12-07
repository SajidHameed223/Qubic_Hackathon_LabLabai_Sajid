export function getToken() {
    return document.cookie
      .split("; ")
      .find((row) => row.startsWith("autopilot_token="))
      ?.split("=")[1];
  }