import { AgentMessage } from "./AgentMessage";

export interface MessageRequest {
    history?: AgentMessage[];
    query?: string;
}
