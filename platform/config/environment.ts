if (!process.env.NEXT_PUBLIC_API_URL) {
    throw new Error("NEXT_PUBLIC_API_URL is not set");
}

export const config = {
    wsUrl: process.env.NEXT_PUBLIC_API_URL,
};

console.log(`Websocket URL set to: ${config.wsUrl}`);
