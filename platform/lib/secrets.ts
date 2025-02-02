import { SecretClient } from "@azure/keyvault-secrets";
import { DefaultAzureCredential, AzureCliCredential, ClientSecretCredential } from "@azure/identity";
import { publicConfig } from "@/config/environment";

let credential;

if (process.env.NODE_ENV === "production") {
  try {
    credential = new DefaultAzureCredential();
  } catch (error) {
    console.error("Error initializing DefaultAzureCredential:", error);
    
    // Check if we have environment variables for service principal authentication
    if (process.env.AZURE_TENANT_ID && process.env.AZURE_CLIENT_ID && process.env.AZURE_CLIENT_SECRET) {
      console.log("Using ClientSecretCredential with environment variables");
      credential = new ClientSecretCredential(
        process.env.AZURE_TENANT_ID,
        process.env.AZURE_CLIENT_ID,
        process.env.AZURE_CLIENT_SECRET
      );
    } else {
      console.log("Falling back to AzureCliCredential");
      credential = new AzureCliCredential();
    }
  }
} else {
  console.log("Using DefaultAzureCredential for development");
  credential = new AzureCliCredential();
}

if (!publicConfig.azureKeyVaultUrl) {
  throw new Error("Azure Key Vault URL is not configured");
}

console.log(`Initializing Key Vault client for ${publicConfig.azureKeyVaultUrl}`);
export const secretClient = new SecretClient(publicConfig.azureKeyVaultUrl, credential);

export async function storeSecret(secretName: string, secretValue: string): Promise<void> {
  try {
    await secretClient.setSecret(secretName, secretValue);
  } catch (error) {
    console.error('Error storing secret:', error);
    throw error;
  }
}

export async function getSecret(secretName: string): Promise<string | undefined> {
  try {
    const retrievedSecret = await secretClient.getSecret(secretName);
    return retrievedSecret.value ? JSON.parse(retrievedSecret.value) : undefined;
  } catch (error) {
    console.error(`Error retrieving secret ${secretName}:`, error);
    return undefined;
  }
}

export async function deleteSecret(secretName: string): Promise<void> {
  try {
    await secretClient.beginDeleteSecret(secretName);
  } catch (error) {
    console.error(`Error deleting secret ${secretName}:`, error);
    throw error;
  }
}
