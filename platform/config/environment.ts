console.log(`Current environment: ${process.env.NODE_ENV}`);

if (!process.env.NEXT_PUBLIC_API_URL) {
    throw new Error("NEXT_PUBLIC_API_URL is not set");
}

if (!process.env.NEXT_PUBLIC_WS_URL) {
    throw new Error("NEXT_PUBLIC_WS_URL is not set");
}

if (!process.env.NEXT_PUBLIC_AZURE_KEY_VAULT_URL) {
    throw new Error("NEXT_PUBLIC_AZURE_KEY_VAULT_URL is not set");
}

export const publicConfig = {
    apiUrl: process.env.NEXT_PUBLIC_API_URL,
    wsUrl: process.env.NEXT_PUBLIC_WS_URL,
    azureKeyVaultUrl: process.env.NEXT_PUBLIC_AZURE_KEY_VAULT_URL,
};

console.log(`API URL set to: ${publicConfig.apiUrl}`);
console.log(`Websocket URL set to: ${publicConfig.wsUrl}`);
console.log(`Azure Key Vault URL set to: ${publicConfig.azureKeyVaultUrl}`);