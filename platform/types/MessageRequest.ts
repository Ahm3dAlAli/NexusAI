import { AgentMessage } from "./AgentMessage";

export enum MessageType {
    init = "init",
    query = "query",
}

export interface MessageRequest {
    type: MessageType;
    messages?: AgentMessage[];
    query?: string;
}
