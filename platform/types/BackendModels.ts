import { AgentMessage } from "./AgentMessage";
import { ModelProviderType } from "@prisma/client";
import { ProviderDetails } from "../lib/modelProviders";

export interface PapersRequest {
    urls: string[];
}

export interface PaperOutput {
    title: string;
    authors: string;
    summary: string;
    url: string;
}

export interface MessageRequest {
    history?: AgentMessage[];
    query?: string;
    custom_instructions?: string[];
    model_provider?: ModelProviderType;
    provider_details?: ProviderDetails | null;
}
