import { AgentMessage } from "./AgentMessage";

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
}
