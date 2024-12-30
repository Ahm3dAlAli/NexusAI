if (!process.env.NEXT_PUBLIC_API_URL) {
    throw new Error("NEXT_PUBLIC_API_URL is not set");
}

if (!process.env.NEXT_PUBLIC_WS_URL) {
    throw new Error("NEXT_PUBLIC_WS_URL is not set");
}

export const config = {
    apiUrl: process.env.NEXT_PUBLIC_API_URL,
    wsUrl: process.env.NEXT_PUBLIC_WS_URL,
};

console.log(`API URL set to: ${config.apiUrl}`);
console.log(`Websocket URL set to: ${config.wsUrl}`);
